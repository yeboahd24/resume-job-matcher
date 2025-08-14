"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.config import settings
from app.api.endpoints.json_auth import router as json_auth_router

from app.auth.manager import (
    fastapi_users,
    auth_backend,
    current_active_user,
    current_superuser
)
from app.db.database import get_async_session
from app.models.user import (
    User,
    UserRead,
    UserCreate,
    UserUpdate,
    UserProfile,
    UserProfileRead,
    UserProfileCreate,
    UserProfileUpdate,
    SubscriptionInfo,
    SubscriptionTier,
    JobMatchRead,
    JobMatch
)
import json
from sqlalchemy import select, update
from datetime import datetime, timedelta

router = APIRouter()

# Include JSON login endpoint
router.include_router(json_auth_router)

# Include FastAPI Users routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    tags=["users"],
)

if settings.RESET_PASSWORD_ENABLED:
    router.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/reset-password",
        tags=["auth"],
    )

if settings.USER_VERIFICATION_ENABLED:
    router.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/verify",
        tags=["auth"],
    )


@router.get("/me/profile", response_model=UserProfileRead, tags=["users"])
async def get_user_profile(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get current user's profile
    """
    # Check if profile exists
    result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalars().first()
    
    if not profile:
        # Create empty profile
        profile = UserProfile(user_id=user.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    
    # Convert JSON strings to lists
    if profile.preferred_job_titles:
        profile.preferred_job_titles = json.loads(profile.preferred_job_titles)
    
    if profile.preferred_locations:
        profile.preferred_locations = json.loads(profile.preferred_locations)
    
    if profile.skills:
        profile.skills = json.loads(profile.skills)
    
    if profile.job_types:
        profile.job_types = json.loads(profile.job_types)
    
    if profile.industries:
        profile.industries = json.loads(profile.industries)
    
    return profile


@router.post("/me/profile", response_model=UserProfileRead, tags=["users"])
async def create_user_profile(
    profile_data: UserProfileCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create or update user profile
    """
    # Check if profile exists
    result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalars().first()
    
    if profile:
        # Update existing profile
        if profile_data.preferred_job_titles is not None:
            profile.preferred_job_titles = json.dumps(profile_data.preferred_job_titles)
        
        if profile_data.preferred_locations is not None:
            profile.preferred_locations = json.dumps(profile_data.preferred_locations)
        
        if profile_data.salary_min is not None:
            profile.salary_min = profile_data.salary_min
        
        if profile_data.salary_max is not None:
            profile.salary_max = profile_data.salary_max
        
        profile.remote_only = profile_data.remote_only
        
        if profile_data.skills is not None:
            profile.skills = json.dumps(profile_data.skills)
        
        if profile_data.experience_years is not None:
            profile.experience_years = profile_data.experience_years
        
        if profile_data.education_level is not None:
            profile.education_level = profile_data.education_level
        
        if profile_data.job_types is not None:
            profile.job_types = json.dumps(profile_data.job_types)
        
        if profile_data.industries is not None:
            profile.industries = json.dumps(profile_data.industries)
        
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        profile = UserProfile(
            user_id=user.id,
            preferred_job_titles=json.dumps(profile_data.preferred_job_titles) if profile_data.preferred_job_titles else None,
            preferred_locations=json.dumps(profile_data.preferred_locations) if profile_data.preferred_locations else None,
            salary_min=profile_data.salary_min,
            salary_max=profile_data.salary_max,
            remote_only=profile_data.remote_only,
            skills=json.dumps(profile_data.skills) if profile_data.skills else None,
            experience_years=profile_data.experience_years,
            education_level=profile_data.education_level,
            job_types=json.dumps(profile_data.job_types) if profile_data.job_types else None,
            industries=json.dumps(profile_data.industries) if profile_data.industries else None,
        )
        session.add(profile)
    
    await session.commit()
    await session.refresh(profile)
    
    # Convert JSON strings to lists for response
    if profile.preferred_job_titles:
        profile.preferred_job_titles = json.loads(profile.preferred_job_titles)
    
    if profile.preferred_locations:
        profile.preferred_locations = json.loads(profile.preferred_locations)
    
    if profile.skills:
        profile.skills = json.loads(profile.skills)
    
    if profile.job_types:
        profile.job_types = json.loads(profile.job_types)
    
    if profile.industries:
        profile.industries = json.loads(profile.industries)
    
    return profile


@router.get("/me/subscription", response_model=SubscriptionInfo, tags=["users"])
async def get_subscription_info(
    user: User = Depends(current_active_user),
):
    """
    Get current user's subscription information
    """
    # Check if it's time to reset the monthly counter
    if user.last_match_reset:
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        if user.last_match_reset < one_month_ago:
            # Reset counter (this will be saved when the user makes their next request)
            user.monthly_matches_used = 0
            user.last_match_reset = datetime.utcnow()
    
    return SubscriptionInfo.from_user(user)


@router.get("/me/job-matches", response_model=List[JobMatchRead], tags=["users"])
async def get_job_matches(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    limit: int = 10,
    offset: int = 0,
):
    """
    Get current user's job match history
    """
    result = await session.execute(
        select(JobMatch)
        .where(JobMatch.user_id == user.id)
        .order_by(JobMatch.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    
    matches = result.scalars().all()
    return matches