"""
Pydantic models for the application
"""

from .job import JobDetail, JobSearchQuery
from .resume import ResumeData, ExtractedSkills
from .task import TaskResponse, TaskStatusResponse, MatchJobsResponse, TaskStatus
from .user import (
    User, UserRead, UserCreate, UserUpdate,
    UserProfile, UserProfileRead, UserProfileCreate, UserProfileUpdate,
    JobMatch, JobMatchRead, SubscriptionInfo, SubscriptionTier
)
from .report import (
    ReportRequest, ReportResponse, ReportData, ReportMetadata,
    ReportFormat, ReportTheme, ReportSection
)

__all__ = [
    "JobDetail",
    "JobSearchQuery", 
    "ResumeData",
    "ExtractedSkills",
    "TaskResponse",
    "TaskStatusResponse",
    "MatchJobsResponse",
    "TaskStatus",
    "User",
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "UserProfile",
    "UserProfileRead",
    "UserProfileCreate",
    "UserProfileUpdate",
    "JobMatch",
    "JobMatchRead",
    "SubscriptionInfo",
    "SubscriptionTier",
    "ReportRequest",
    "ReportResponse",
    "ReportData",
    "ReportMetadata",
    "ReportFormat",
    "ReportTheme",
    "ReportSection",
]