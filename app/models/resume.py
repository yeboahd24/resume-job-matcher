"""
Resume-related Pydantic models
"""

from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExtractedSkills(BaseModel):
    """
    Model for skills extracted from resume
    """
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    programming_languages: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []
    certifications: List[str] = []
    job_titles: List[str] = []
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    
    @validator("experience_years")
    def validate_experience_years(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError("Experience years must be between 0 and 50")
        return v


class ResumeData(BaseModel):
    """
    Model for processed resume data
    """
    original_filename: str
    file_type: str
    file_size_bytes: int
    extracted_text: str
    extracted_skills: ExtractedSkills
    processed_at: datetime
    processing_time_seconds: float
    
    @validator("extracted_text")
    def validate_text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Extracted text cannot be empty")
        return v
    
    @validator("file_size_bytes")
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f"File size cannot exceed {max_size} bytes")
        return v


class ResumeUpload(BaseModel):
    """
    Model for resume upload metadata
    """
    filename: str
    content_type: str
    size_bytes: int
    upload_timestamp: datetime = None
    
    def __init__(self, **data):
        if data.get('upload_timestamp') is None:
            data['upload_timestamp'] = datetime.utcnow()
        super().__init__(**data)