"""
Application configuration management
"""

import os
from typing import List, Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import validator
except ImportError:
    # Fallback for older pydantic versions
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
    SIMILARITY_THRESHOLD: float = 0.05  # Lower threshold to show more jobs (5%)
    MAX_SKILLS_EXTRACT: int = 20
    MAX_JOB_TITLES_EXTRACT: int = 10
    MAX_JOBS_PER_SKILL: int = 2
    MAX_MATCHED_JOBS: int = 10  # Show up to 10 matched jobs
    
    # Job scraping settings
    JOB_SCRAPING_ENABLED: bool = True
    JOB_SCRAPING_TIMEOUT: int = 30
    USE_MOCK_JOBS: bool = False  # Set to False for real scraping
    
    # Rate limiting for web scraping
    SCRAPING_MIN_DELAY: float = 1.0  # Minimum delay between requests (seconds)
    SCRAPING_MAX_DELAY: float = 3.0  # Maximum delay between requests (seconds)
    SCRAPING_MAX_RETRIES: int = 3    # Maximum retries for failed requests
    
    # Free job board settings
    ENABLE_REMOTEOK: bool = True
    ENABLE_WEWORKREMOTELY: bool = True
    ENABLE_ENHANCED_FALLBACK: bool = True  # Use enhanced job generation as fallback
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False
    
    @validator("DATABASE_URL", pre=True)
    def assemble_database_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # Default to SQLite for development
        return "sqlite+aiosqlite:///./data/resumematcher.db"
    
    # Authentication settings
    SECRET_KEY: str = "your-secret-key-change-in-production-please-use-a-secure-random-key"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # User settings
    USER_REGISTRATION_ENABLED: bool = True
    USER_VERIFICATION_ENABLED: bool = False  # Email verification (disabled for MVP)
    RESET_PASSWORD_ENABLED: bool = True
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
