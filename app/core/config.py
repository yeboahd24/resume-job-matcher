"""
Application configuration management
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """
    
    # Basic app settings
    PROJECT_NAME: str = "Resume Job Matcher API"
    PROJECT_DESCRIPTION: str = "A backend service for matching resumes to job listings using AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        
        password_part = f":{values.get('REDIS_PASSWORD')}@" if values.get('REDIS_PASSWORD') else ""
        return f"redis://{password_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    # Celery settings
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = 25 * 60  # 25 minutes
    
    @validator("CELERY_BROKER_URL", pre=True)
    def assemble_celery_broker(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return values.get("REDIS_URL", "redis://localhost:6379/0")
    
    @validator("CELERY_RESULT_BACKEND", pre=True)
    def assemble_celery_backend(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return values.get("REDIS_URL", "redis://localhost:6379/0")
    
    # File upload settings
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf", "text/plain"]
    UPLOAD_DIR: str = "data/uploads"
    
    # ML/NLP settings
    SPACY_MODEL: str = "en_core_web_sm"
    SIMILARITY_THRESHOLD: float = 0.1
    MAX_SKILLS_EXTRACT: int = 20
    MAX_JOB_TITLES_EXTRACT: int = 10
    MAX_JOBS_PER_SKILL: int = 2
    MAX_MATCHED_JOBS: int = 5
    
    # Job scraping settings
    JOB_SCRAPING_ENABLED: bool = True
    JOB_SCRAPING_TIMEOUT: int = 30
    USE_MOCK_JOBS: bool = True  # Set to False for real scraping
    
    # Database settings (for future use)
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()