"""
Subscription management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Dict, Any

from app.auth.manager import current_active_user, current_superuser
from app.models.user import User, SubscriptionTier, SubscriptionInfo
from app.db.database import get_async_session

router = APIRouter()


@router.post("/upgrade", response_model=SubscriptionInfo)
async def upgrade_subscription(
    tier: SubscriptionTier = Body(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Upgrade user subscription to a higher tier
    
    This is a simplified implementation without payment processing.
    In a production environment, this would integrate with a payment provider like Stripe.
    """
    # Validate tier upgrade
    tier_levels = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.STUDENT: 1,
        SubscriptionTier.PRO: 2,
        SubscriptionTier.ENTERPRISE: 3,
    }
    
    current_level = tier_levels.get(user.subscription_tier, 0)
    new_level = tier_levels.get(tier, 0)
    
    if new_level <= current_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot downgrade from {user.subscription_tier} to {tier}. Please contact support for downgrades."
        )
    
    # Update user subscription
    user.subscription_tier = tier
    user.updated_at = datetime.utcnow()
    
    # Reset usage counters for the new subscription
    user.monthly_matches_used = 0
    user.last_match_reset = datetime.utcnow()
    
    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Return updated subscription info
    return SubscriptionInfo.from_user(user)


@router.post("/reset-usage", response_model=SubscriptionInfo)
async def reset_usage(
    user: User = Depends(current_superuser),
    user_id: int = Body(...),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Reset a user's monthly usage (admin only)
    """
    # Get user by ID
    result = await session.get(User, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    target_user = result
    
    # Reset usage counters
    target_user.monthly_matches_used = 0
    target_user.last_match_reset = datetime.utcnow()
    
    # Save changes
    session.add(target_user)
    await session.commit()
    await session.refresh(target_user)
    
    # Return updated subscription info
    return SubscriptionInfo.from_user(target_user)


@router.get("/usage-stats", response_model=Dict[str, Any])
async def get_usage_stats(
    user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get usage statistics for all subscription tiers (admin only)
    """
    # In a real implementation, this would query the database for aggregate statistics
    # For now, we'll return some placeholder data
    return {
        "total_users": 100,
        "subscription_breakdown": {
            "free": 80,
            "student": 10,
            "pro": 8,
            "enterprise": 2
        },
        "monthly_job_matches": 250,
        "average_matches_per_user": 2.5,
        "top_tier_conversion_rate": "10%"
    }