"""
Authentication manager for user management
"""

from typing import Optional, Union
from datetime import datetime, timedelta

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, FastAPIUsers, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_async_session
from app.models.user import User, UserCreate


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Get user database dependency
    """
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    User manager for authentication
    """
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Hook after user registration
        """
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Hook after forgot password request
        """
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Hook after verification request
        """
        print(f"Verification requested for user {user.id}. Verification token: {token}")
    
    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Create a new user with additional fields
        """
        # Create the user with parent method
        user = await super().create(user_create, safe, request)
        
        # Create update dict with additional fields
        update_dict = {
            "first_name": user_create.first_name,
            "last_name": user_create.last_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save the user with the update dict
        await self.user_db.update(user, update_dict)
        
        return user


async def get_user_manager(user_db=Depends(get_user_db)):
    """
    Get user manager dependency
    """
    yield UserManager(user_db)


# Bearer transport for token
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# JWT strategy for token
def get_jwt_strategy() -> JWTStrategy:
    """
    Get JWT strategy for authentication
    """
    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


# Current user dependencies
current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)