"""
Pydantic models for the application
"""

from .job import JobDetail, JobSearchQuery
from .resume import ResumeData, ExtractedSkills
from .task import TaskResponse, TaskStatusResponse, MatchJobsResponse, TaskStatus

__all__ = [
    "JobDetail",
    "JobSearchQuery", 
    "ResumeData",
    "ExtractedSkills",
    "TaskResponse",
    "TaskStatusResponse",
    "MatchJobsResponse",
    "TaskStatus",
]