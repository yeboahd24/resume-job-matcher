"""
User models for authentication and profiles
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from pydantic import BaseModel, EmailStr, validator
from enum import Enum

Base = declarative_base()


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    STUDENT = "student"


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    User table for authentication
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Additional user fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    subscription_tier = Column(String(20), default=SubscriptionTier.FREE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Usage tracking
    monthly_matches_used = Column(Integer, default=0, nullable=False)
    last_match_reset = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    job_matches = relationship("JobMatch", back_populates="user")


class UserProfile(Base):
    """
    Extended user profile with job preferences
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job preferences
    preferred_job_titles = Column(Text, nullable=True)  # JSON string
    preferred_locations = Column(Text, nullable=True)   # JSON string
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    remote_only = Column(Boolean, default=False, nullable=False)
    
    # Skills and experience
    skills = Column(Text, nullable=True)  # JSON string
    experience_years = Column(Integer, nullable=True)
    education_level = Column(String(50), nullable=True)
    
    # Preferences
    job_types = Column(Text, nullable=True)  # JSON string: ["full-time", "contract", etc.]
    industries = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class JobMatch(Base):
    """
    Store job matching history for users
    """
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Resume info
    resume_filename = Column(String(255), nullable=False)
    resume_content_hash = Column(String(64), nullable=True)  # For deduplication
    
    # Job match results
    jobs_found = Column(Integer, default=0, nullable=False)
    match_results = Column(Text, nullable=True)  # JSON string of job matches
    processing_time_seconds = Column(Float, nullable=True)
    
    # Metadata
    search_queries = Column(Text, nullable=True)  # JSON string
    extracted_skills = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="job_matches")


# Pydantic models for API

class UserRead(BaseModel):
    """User model for reading (public info)"""
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    subscription_tier: SubscriptionTier
    is_active: bool
    is_verified: bool
    created_at: datetime
    monthly_matches_used: int
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User model for registration"""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    def create_update_dict(self):
        """
        Generate a dict of values that can be used with SQLAlchemyUserDatabase.create
        This is required by FastAPI Users v12.x
        """
        return {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        }


class UserUpdate(BaseModel):
    """User model for updates"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    def create_update_dict(self):
        """
        Generate a dict of values that can be used with SQLAlchemyUserDatabase.update
        This is required by FastAPI Users v12.x
        """
        data = {}
        if self.first_name is not None:
            data["first_name"] = self.first_name
        if self.last_name is not None:
            data["last_name"] = self.last_name
        if self.email is not None:
            data["email"] = self.email
        return data


class UserProfileRead(BaseModel):
    """User profile model for reading"""
    id: int
    user_id: int
    preferred_job_titles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_only: bool = False
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    job_types: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileCreate(BaseModel):
    """User profile model for creation"""
    preferred_job_titles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_only: bool = False
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    job_types: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    
    @validator("salary_min", "salary_max")
    def validate_salary(cls, v):
        if v is not None and v < 0:
            raise ValueError("Salary must be positive")
        return v
    
    @validator("experience_years")
    def validate_experience(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError("Experience years must be between 0 and 50")
        return v


class UserProfileUpdate(UserProfileCreate):
    """User profile model for updates (same as create)"""
    pass


class JobMatchRead(BaseModel):
    """Job match history model for reading"""
    id: int
    user_id: int
    resume_filename: str
    jobs_found: int
    processing_time_seconds: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionInfo(BaseModel):
    """Subscription information model"""
    tier: SubscriptionTier
    monthly_limit: int
    matches_used: int
    matches_remaining: int
    features: List[str]
    next_reset_date: Optional[datetime] = None
    upgrade_options: List[str] = []
    price_info: Optional[dict] = None
    
    @classmethod
    def from_user(cls, user: User) -> "SubscriptionInfo":
        """Create subscription info from user"""
        tier_limits = {
            SubscriptionTier.FREE: 5,
            SubscriptionTier.PRO: -1,  # Unlimited
            SubscriptionTier.ENTERPRISE: -1,  # Unlimited
            SubscriptionTier.STUDENT: 15,
        }
        
        tier_features = {
            SubscriptionTier.FREE: ["Basic job matching", "5 matches per month", "Standard processing time"],
            SubscriptionTier.PRO: ["Unlimited matches", "Priority processing", "Advanced filters", "PDF reports", "Email notifications"],
            SubscriptionTier.ENTERPRISE: ["All Pro features", "API access", "Bulk processing", "Custom integrations", "Dedicated support"],
            SubscriptionTier.STUDENT: ["15 matches per month", "Student discount", "Career resources", "Resume templates"],
        }
        
        # Price information (placeholder for now)
        price_info = {
            SubscriptionTier.FREE: {"monthly": 0, "annual": 0},
            SubscriptionTier.STUDENT: {"monthly": 4.99, "annual": 49.99},
            SubscriptionTier.PRO: {"monthly": 9.99, "annual": 99.99},
            SubscriptionTier.ENTERPRISE: {"monthly": 49.99, "annual": 499.99},
        }
        
        # Calculate next reset date
        next_reset_date = None
        if user.last_match_reset:
            next_reset_date = user.last_match_reset + timedelta(days=30)
        
        # Determine available upgrade options based on current tier
        upgrade_options = []
        current_tier = user.subscription_tier
        
        if current_tier == SubscriptionTier.FREE:
            upgrade_options = [SubscriptionTier.STUDENT, SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
        elif current_tier == SubscriptionTier.STUDENT:
            upgrade_options = [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
        elif current_tier == SubscriptionTier.PRO:
            upgrade_options = [SubscriptionTier.ENTERPRISE]
        
        monthly_limit = tier_limits.get(user.subscription_tier, 5)
        matches_remaining = monthly_limit - user.monthly_matches_used if monthly_limit > 0 else -1
        
        return cls(
            tier=user.subscription_tier,
            monthly_limit=monthly_limit,
            matches_used=user.monthly_matches_used,
            matches_remaining=matches_remaining,
            features=tier_features.get(user.subscription_tier, []),
            next_reset_date=next_reset_date,
            upgrade_options=upgrade_options,
            price_info=price_info.get(user.subscription_tier)
        )