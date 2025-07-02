"""
Celery tasks for background processing
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from app.core.celery_app import celery_app
from app.services.file_service import FileService
from app.services.nlp_service import NLPService
from app.services.job_scraper import JobScraperService
from app.services.matching_service import JobMatchingService
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.services.tasks.process_resume_and_match_jobs")
def process_resume_and_match_jobs(self, file_content: bytes, filename: str, content_type: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Main Celery task to process resume and match jobs
    
    Args:
        self: Celery task instance
        file_content: Resume file content as bytes
        filename: Original filename
        content_type: MIME type of the file
        user_id: Optional user ID for authenticated users
        
    Returns:
        Dictionary with matched jobs and processing metadata
    """
    start_time = time.time()
    
    try:
        # Initialize services
        file_service = FileService()
        nlp_service = NLPService()
        job_scraper = JobScraperService()
        matching_service = JobMatchingService()
        
        # Step 1: Extract text from resume
        self.update_state(
            state='STARTED', 
            meta={
                'progress': 'Extracting text from resume...',
                'percentage': 10,
                'started_at': datetime.utcnow().isoformat()
            }
        )
        
        resume_text = file_service.extract_text_from_file(file_content, content_type)
        
        if not resume_text.strip():
            raise ValueError("No text could be extracted from the resume")
        
        logger.info(f"Extracted {len(resume_text)} characters from resume: {filename}")
        
        # Step 2: Extract skills and job titles
        self.update_state(
            state='STARTED',
            meta={
                'progress': 'Analyzing resume and extracting skills...',
                'percentage': 25
            }
        )
        
        extracted_skills = nlp_service.extract_skills_and_titles(resume_text)
        
        if not extracted_skills.technical_skills:
            raise ValueError("No technical skills could be extracted from the resume")
        
        logger.info(f"Extracted {len(extracted_skills.technical_skills)} technical skills")
        
        # Step 3: Search for jobs
        self.update_state(
            state='STARTED',
            meta={
                'progress': 'Searching for relevant job listings...',
                'percentage': 50
            }
        )
        
        # Use top skills for job search
        search_queries = extracted_skills.technical_skills[:5]
        
        # Use async job scraping
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            all_jobs = loop.run_until_complete(
                job_scraper.scrape_multiple_sources(search_queries)
            )
        finally:
            # Ensure session is closed
            loop.run_until_complete(job_scraper.close())
            loop.close()
        
        if not all_jobs:
            return {
                'matched_jobs': [],
                'message': 'No jobs found matching your skills',
                'extracted_skills': extracted_skills.dict(),
                'processing_time_seconds': time.time() - start_time
            }
        
        logger.info(f"Found {len(all_jobs)} unique job listings")
        
        # Step 4: Calculate job matches
        self.update_state(
            state='STARTED',
            meta={
                'progress': 'Calculating job similarity scores...',
                'percentage': 75
            }
        )
        
        matched_jobs = matching_service.match_jobs_to_resume(
            resume_text=resume_text,
            jobs=all_jobs,
            extracted_skills=extracted_skills.technical_skills
        )
        
        # Step 5: Finalize results
        self.update_state(
            state='STARTED',
            meta={
                'progress': 'Finalizing results...',
                'percentage': 90
            }
        )
        
        processing_time = time.time() - start_time
        
        # Convert JobDetail objects to dictionaries for JSON serialization
        matched_jobs_dict = [job.dict() for job in matched_jobs]
        
        result = {
            'matched_jobs': matched_jobs_dict,
            'extracted_skills': extracted_skills.dict(),
            'total_jobs_found': len(all_jobs),
            'matched_jobs_count': len(matched_jobs),
            'search_queries': search_queries,
            'processing_time_seconds': round(processing_time, 2),
            'file_info': {
                'filename': filename,
                'content_type': content_type,
                'size_bytes': len(file_content)
            },
            'user_id': user_id  # Include user ID if available
        }
        
        logger.info(f"Job matching completed in {processing_time:.2f} seconds. "
                   f"Found {len(matched_jobs)} matches out of {len(all_jobs)} jobs.")
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in process_resume_and_match_jobs: {error_msg}")
        
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'processing_time_seconds': time.time() - start_time
            }
        )
        raise


@celery_app.task(name="app.services.tasks.health_check_task")
def health_check_task() -> Dict[str, Any]:
    """
    Simple health check task for monitoring Celery workers
    
    Returns:
        Dictionary with health status
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'worker_id': health_check_task.request.hostname if hasattr(health_check_task, 'request') else 'unknown'
    }


@celery_app.task(name="app.services.tasks.cleanup_old_results")
def cleanup_old_results() -> Dict[str, Any]:
    """
    Cleanup old task results (can be scheduled to run periodically)
    
    Returns:
        Dictionary with cleanup status
    """
    try:
        # This is a placeholder for cleanup logic
        # In production, you might want to:
        # 1. Clean up old Redis keys
        # 2. Remove temporary files
        # 3. Archive old results to database
        
        logger.info("Cleanup task executed successfully")
        
        return {
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Cleanup completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {
            'status': 'failed',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }