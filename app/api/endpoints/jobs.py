"""
Job matching endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status, Query
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models import MatchJobsResponse
from app.services.file_service import FileService
from app.services.tasks import process_resume_and_match_jobs
from app.core.config import settings
from app.auth.manager import current_active_user, current_superuser
from app.models.user import User, JobMatch, SubscriptionTier
from app.db.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter()


def get_file_service() -> FileService:
    """
    Dependency to get file service instance
    """
    return FileService()


def parse_float_param(param: Optional[str] = None) -> Optional[float]:
    """Parse and validate float parameter, handling whitespace"""
    if param is None:
        return None
    try:
        # Strip whitespace and convert to float
        cleaned_param = param.strip() if isinstance(param, str) else param
        value = float(cleaned_param)
        if 0 <= value <= 1:
            return value
        raise HTTPException(status_code=400, detail="Parameter must be between 0 and 1")
    except ValueError:
        raise HTTPException(status_code=400, detail="Parameter must be a valid float")

def parse_int_param(param: Optional[str] = None) -> Optional[int]:
    """Parse and validate integer parameter, handling whitespace"""
    if param is None:
        return None
    try:
        # Strip whitespace and convert to int
        cleaned_param = param.strip() if isinstance(param, str) else param
        value = int(cleaned_param)
        if 1 <= value <= 50:
            return value
        raise HTTPException(status_code=400, detail="Parameter must be between 1 and 50")
    except ValueError:
        raise HTTPException(status_code=400, detail="Parameter must be a valid integer")

def parse_salary_param(param: Optional[str] = None) -> Optional[int]:
    """Parse and validate salary parameter, handling whitespace"""
    if param is None:
        return None
    try:
        # Strip whitespace and convert to int
        cleaned_param = param.strip() if isinstance(param, str) else param
        value = int(cleaned_param)
        if value < 0:
            raise HTTPException(status_code=400, detail="Salary must be a positive value")
        return value
    except ValueError:
        raise HTTPException(status_code=400, detail="Salary must be a valid integer")

@router.post("/match", response_model=MatchJobsResponse)
async def match_jobs(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
    user: Optional[User] = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    similarity_threshold: Optional[str] = Query(None, description="Custom similarity threshold (0.0 to 1.0)"),
    max_jobs: Optional[str] = Query(None, description="Maximum number of jobs to return (1 to 50)"),
    min_salary: Optional[str] = Query(None, description="Minimum salary requirement (e.g., 50000)"),
    max_salary: Optional[str] = Query(None, description="Maximum salary consideration (e.g., 150000)"),
    use_profile_salary: bool = Query(False, description="Use salary preferences from user profile")
):
    """
    Upload a resume and trigger job matching process.
    
    Args:
        file: Resume file (PDF or text format)
        similarity_threshold: Optional custom similarity threshold (0.0 to 1.0)
        max_jobs: Optional maximum number of jobs to return (1 to 50)
        min_salary: Optional minimum salary requirement
        max_salary: Optional maximum salary consideration
        use_profile_salary: Whether to use salary preferences from user profile
        
    Returns:
        Task ID and status for tracking the job matching process
    """
    try:
        # Parse and validate parameters
        parsed_similarity_threshold = parse_float_param(similarity_threshold)
        parsed_max_jobs = parse_int_param(max_jobs)
        parsed_min_salary = parse_salary_param(min_salary)
        parsed_max_salary = parse_salary_param(max_salary)
        
        # Get salary preferences from user profile if requested
        profile_min_salary = None
        profile_max_salary = None
        
        if use_profile_salary and user:
            # Get user profile
            from sqlalchemy import select
            from app.models.user import UserProfile
            
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user.id)
            )
            profile = result.scalars().first()
            
            if profile:
                profile_min_salary = profile.salary_min
                profile_max_salary = profile.salary_max
                
                # Use profile values if no explicit parameters provided
                if parsed_min_salary is None and profile_min_salary is not None:
                    parsed_min_salary = profile_min_salary
                    
                if parsed_max_salary is None and profile_max_salary is not None:
                    parsed_max_salary = profile_max_salary
        
        # Debug parameters
        logger.info(
            f"Job matching parameters - "
            f"similarity_threshold: {parsed_similarity_threshold}, "
            f"max_jobs: {parsed_max_jobs}, "
            f"min_salary: {parsed_min_salary}, "
            f"max_salary: {parsed_max_salary}, "
            f"use_profile_salary: {use_profile_salary}"
        )
        
        # Validate file
        file_service.validate_file(file)
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Check subscription limits if user is authenticated
        if user:
            # Check if user has reached their monthly limit
            if user.subscription_tier == SubscriptionTier.FREE and user.monthly_matches_used >= 5:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="You have reached your monthly limit of 5 job matches. Please upgrade your subscription."
                )
            elif user.subscription_tier == SubscriptionTier.STUDENT and user.monthly_matches_used >= 15:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="You have reached your monthly limit of 15 job matches. Please upgrade your subscription."
                )
            
            # Check if it's time to reset the monthly counter
            if user.last_match_reset:
                one_month_ago = datetime.utcnow() - timedelta(days=30)
                if user.last_match_reset < one_month_ago:
                    # Reset counter
                    user.monthly_matches_used = 0
                    user.last_match_reset = datetime.utcnow()
            
            # Increment usage counter
            user.monthly_matches_used += 1
            
            # Update user in database
            user.updated_at = datetime.utcnow()
            session.add(user)
            await session.commit()
        
        # Trigger Celery task
        task = process_resume_and_match_jobs.delay(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
            user_id=user.id if user else None,
            similarity_threshold=parsed_similarity_threshold,
            max_jobs=parsed_max_jobs,
            min_salary=parsed_min_salary,
            max_salary=parsed_max_salary
        )
        
        # Record job match in database if user is authenticated
        if user:
            job_match = JobMatch(
                user_id=user.id,
                resume_filename=file.filename,
                created_at=datetime.utcnow()
            )
            session.add(job_match)
            await session.commit()
        
        logger.info(f"Started job matching task: {task.id} for file: {file.filename}")
        
        return MatchJobsResponse(
            task_id=task.id,
            status="started",
            message="Resume uploaded successfully. Job matching in progress."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in match_jobs endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats for resume upload
    """
    return {
        "supported_formats": settings.ALLOWED_FILE_TYPES,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "description": {
            "application/pdf": "PDF documents",
            "text/plain": "Plain text files"
        }
    }


@router.get("/salary-ranges")
async def get_salary_ranges():
    """
    Get common salary ranges for different job types
    """
    from app.services.job_scraper import JobScraperService
    
    job_scraper = JobScraperService()
    
    # Get sample salary ranges for different job types
    salary_ranges = {
        "entry_level": {
            "range": "$50,000 - $80,000",
            "median": "$65,000"
        },
        "mid_level": {
            "range": "$80,000 - $120,000",
            "median": "$95,000"
        },
        "senior_level": {
            "range": "$120,000 - $180,000",
            "median": "$145,000"
        },
        "management": {
            "range": "$140,000 - $220,000",
            "median": "$175,000"
        },
        "contract": {
            "range": "$50 - $100 per hour",
            "median": "$75 per hour"
        }
    }
    
    # Get job types with salary ranges
    job_types = {}
    for job_type in ["Full-time", "Part-time", "Contract", "Internship", "Remote"]:
        job_types[job_type] = job_scraper._generate_salary_range(job_type)
    
    return {
        "salary_ranges_by_level": salary_ranges,
        "salary_ranges_by_job_type": job_types,
        "recommended_filtering": {
            "entry_level": {"min": 50000, "max": 80000},
            "mid_level": {"min": 80000, "max": 120000},
            "senior_level": {"min": 120000, "max": 180000}
        }
    }