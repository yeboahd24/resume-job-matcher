"""
Job-related Pydantic models
"""

from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
from datetime import datetime


class JobDetail(BaseModel):
    """
    Model representing a job listing with similarity score
    """
    title: str
    company: str
    location: str
    description: str
    url: str
    similarity_score: float
    posted_date: Optional[datetime] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    remote_allowed: Optional[bool] = None
    
    @validator("similarity_score")
    def validate_similarity_score(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Similarity score must be between 0 and 1")
        return round(v, 3)
    
    @validator("description")
    def validate_description_length(cls, v):
        if len(v) > 1000:
            return v[:997] + "..."
        return v


class JobSearchQuery(BaseModel):
    """
    Model for job search parameters
    """
    keywords: List[str]
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_only: bool = False
    limit: int = 5
    
    @validator("limit")
    def validate_limit(cls, v):
        if not 1 <= v <= 50:
            raise ValueError("Limit must be between 1 and 50")
        return v


class JobMatchResult(BaseModel):
    """
    Model for job matching results
    """
    matched_jobs: List[JobDetail]
    total_jobs_found: int
    matched_jobs_count: int
    search_queries: List[str]
    processing_time_seconds: Optional[float] = None