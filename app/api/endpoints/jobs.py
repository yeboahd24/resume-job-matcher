"""
Job matching endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
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
    file_service: FileService = Depends(get_file_service),
    user: Optional[User] = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
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
            user_id=user.id if user else None
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