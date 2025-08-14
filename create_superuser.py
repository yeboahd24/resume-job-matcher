#!/usr/bin/env python3
"""
Create a superuser for the application
"""

import asyncio
import os
import sys
import getpass
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.models.user import User
from app.auth.manager import get_user_manager, get_user_db
from app.db.database import get_async_session
from fastapi_users.password import PasswordHelper

async def create_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    is_superuser: bool = False
) -> User:
    """
    Create a new user
    """
    # Get async session
    async for session in get_async_session():
        # Get user database
        user_db = next(get_user_db(session))
        
        # Get user manager
        user_manager = next(get_user_manager(user_db))
        
        # Check if user already exists
        existing_user = await user_db.get_by_email(email)
        if existing_user:
            print(f"User with email {email} already exists")
            return existing_user
        
        # Create user
        password_helper = PasswordHelper()
        hashed_password = password_helper.hash(password)
        
        # Create user data
        user_dict = {
            "email": email,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_superuser": is_superuser,
            "is_verified": True,
            "first_name": first_name,
            "last_name": last_name,
            "subscription_tier": "pro" if is_superuser else "free",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "monthly_matches_used": 0,
            "last_match_reset": datetime.utcnow(),
        }
        
        # Create user
        user = await user_db.create(user_dict)
        
        print(f"User {email} created successfully!")
        return user

async def main():
    """
    Main function to create a superuser
    """
    print("Create Superuser")
    print("===============")
    
    # Get user input
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    
    # Create superuser
    await create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_superuser=True
    )
    
    print("Superuser created successfully!")

if __name__ == "__main__":
    asyncio.run(main())