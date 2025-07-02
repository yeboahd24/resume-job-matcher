"""
PDF Report models
"""

from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .job import JobDetail
from .user import SubscriptionTier


class ReportFormat(str, Enum):
    """Report format options"""
    PDF = "pdf"
    HTML = "html"


class ReportTheme(str, Enum):
    """Report theme options"""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMAL = "minimal"
    COLORFUL = "colorful"


class ReportSection(str, Enum):
    """Available report sections"""
    SUMMARY = "summary"
    MATCHED_JOBS = "matched_jobs"
    SKILLS_ANALYSIS = "skills_analysis"
    RECOMMENDATIONS = "recommendations"
    SEARCH_QUERIES = "search_queries"
    STATISTICS = "statistics"


class ReportRequest(BaseModel):
    """Request model for generating reports"""
    task_id: str
    format: ReportFormat = ReportFormat.PDF
    theme: ReportTheme = ReportTheme.PROFESSIONAL
    sections: List[ReportSection] = [
        ReportSection.SUMMARY,
        ReportSection.MATCHED_JOBS,
        ReportSection.SKILLS_ANALYSIS,
        ReportSection.RECOMMENDATIONS
    ]
    include_company_logos: bool = False
    include_charts: bool = True
    custom_title: Optional[str] = None
    
    @validator("sections")
    def validate_sections(cls, v):
        if not v:
            raise ValueError("At least one section must be included")
        return v


class ReportData(BaseModel):
    """Data model for report generation"""
    # Basic info
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    generated_at: datetime
    
    # Resume info
    resume_filename: str
    extracted_skills: List[str] = []
    experience_level: Optional[str] = None
    
    # Job matching results
    matched_jobs: List[JobDetail] = []
    total_jobs_found: int = 0
    search_queries: List[str] = []
    processing_time_seconds: Optional[float] = None
    
    # Analysis
    top_skills: List[Dict[str, Any]] = []  # [{"skill": "Python", "frequency": 5, "relevance": 0.9}]
    skill_gaps: List[str] = []
    industry_insights: List[str] = []
    salary_insights: Dict[str, Any] = {}
    
    # Recommendations
    recommendations: List[str] = []
    suggested_skills: List[str] = []
    career_tips: List[str] = []


class ReportResponse(BaseModel):
    """Response model for report generation"""
    report_id: str
    status: str
    download_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    expires_at: Optional[datetime] = None
    generated_at: datetime
    format: ReportFormat
    theme: ReportTheme


class ReportMetadata(BaseModel):
    """Metadata for generated reports"""
    report_id: str
    user_id: Optional[int] = None
    task_id: str
    filename: str
    file_path: str
    file_size_bytes: int
    format: ReportFormat
    theme: ReportTheme
    sections_included: List[ReportSection]
    generated_at: datetime
    expires_at: Optional[datetime] = None
    download_count: int = 0
    last_downloaded_at: Optional[datetime] = None