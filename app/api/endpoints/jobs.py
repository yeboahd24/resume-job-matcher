"""
Job matching endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import logging
from typing import List

from app.models import MatchJobsResponse
from app.services.file_service import FileService
from app.services.tasks import process_resume_and_match_jobs
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def get_file_service() -> FileService:
    """
    Dependency to get file service instance
    """
    return FileService()


@router.post("/match", response_model=MatchJobsResponse)
async def match_jobs(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload a resume and trigger job matching process.
    
    Args:
        file: Resume file (PDF or text format)
        
    Returns:
        Task ID and status for tracking the job matching process
    """
    try:
        # Validate file
        file_service.validate_file(file)
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Trigger Celery task
        task = process_resume_and_match_jobs.delay(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
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