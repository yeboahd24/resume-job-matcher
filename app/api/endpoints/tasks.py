"""
Task management endpoints
"""

from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, Any

from app.models import TaskStatusResponse, TaskStatus, JobDetail
from app.core.celery_app import celery_app

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a job matching task.
    
    Args:
        task_id: The task ID returned from the match-jobs endpoint
        
    Returns:
        Task status and results (if completed)
    """
    try:
        # Get task result
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.PENDING,
                progress="Task is waiting to be processed...",
                progress_percentage=0
            )
        
        elif task_result.state == 'STARTED':
            progress_info = task_result.info if task_result.info else {}
            progress = progress_info.get('progress', 'Processing...')
            percentage = progress_info.get('percentage', 10)
            
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.STARTED,
                progress=progress,
                progress_percentage=percentage,
                started_at=progress_info.get('started_at')
            )
        
        elif task_result.state == 'SUCCESS':
            result_data = task_result.result
            
            # Convert matched jobs to JobDetail objects
            matched_jobs = []
            if 'matched_jobs' in result_data:
                for job_data in result_data['matched_jobs']:
                    job_detail = JobDetail(**job_data)
                    matched_jobs.append(job_detail)
            
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.SUCCESS,
                result=matched_jobs,
                progress="Job matching completed successfully",
                progress_percentage=100,
                processing_time_seconds=result_data.get('processing_time_seconds'),
                metadata={
                    'total_jobs_found': result_data.get('total_jobs_found', 0),
                    'matched_jobs_count': result_data.get('matched_jobs_count', 0),
                    'extracted_skills': result_data.get('extracted_skills', {})
                }
            )
        
        elif task_result.state == 'FAILURE':
            error_info = task_result.info if task_result.info else {}
            error_msg = error_info.get('error', str(task_result.info)) if task_result.info else "Unknown error occurred"
            
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.FAILURE,
                error=error_msg,
                progress="Task failed",
                progress_percentage=0
            )
        
        else:
            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus(task_result.state),
                progress=f"Task state: {task_result.state}",
                progress_percentage=50
            )
            
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task status: {str(e)}"
        )


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running task
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} has been cancelled"}
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling task: {str(e)}"
        )


@router.get("/active")
async def list_active_tasks():
    """
    List all active tasks (for debugging/monitoring)
    """
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        
        return {
            "active_tasks": active_tasks or {},
            "scheduled_tasks": scheduled_tasks or {},
            "total_active": sum(len(tasks) for tasks in (active_tasks or {}).values()),
            "total_scheduled": sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing tasks: {str(e)}"
        )