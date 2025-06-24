"""
Task-related Pydantic models
"""

from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from enum import Enum
from datetime import datetime

from .job import JobDetail


class TaskStatus(str, Enum):
    """
    Enum for Celery task statuses
    """
    PENDING = "PENDING"
    STARTED = "STARTED" 
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TaskResponse(BaseModel):
    """
    Basic task response model
    """
    task_id: str
    status: str
    message: str
    created_at: datetime = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class TaskStatusResponse(BaseModel):
    """
    Detailed task status response model
    """
    task_id: str
    status: TaskStatus
    result: Optional[List[JobDetail]] = None
    error: Optional[str] = None
    progress: Optional[str] = None
    progress_percentage: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class MatchJobsResponse(BaseModel):
    """
    Response model for job matching request
    """
    task_id: str
    status: str
    message: str
    estimated_completion_time: Optional[int] = None  # seconds
    created_at: datetime = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        if data.get('estimated_completion_time') is None:
            data['estimated_completion_time'] = 30  # 30 seconds default
        super().__init__(**data)


class TaskProgress(BaseModel):
    """
    Model for tracking task progress
    """
    current_step: str
    total_steps: int
    completed_steps: int
    percentage: int
    details: Optional[str] = None
    
    def __init__(self, **data):
        if 'percentage' not in data and 'total_steps' in data and 'completed_steps' in data:
            data['percentage'] = int((data['completed_steps'] / data['total_steps']) * 100)
        super().__init__(**data)