#!/usr/bin/env python3
"""
Create a superuser for the application
"""

import asyncio
import getpass
import sys
import os
import warnings
from datetime import datetime

# Suppress bcrypt warning
warnings.filterwarnings("ignore", message=".*bcrypt version.*")

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.database import async_session_maker
from app.models.user import User, UserCreate
from fastapi_users.password import PasswordHelper

async def create_superuser():
    """
    Create a superuser interactively
    """
    print("Creating superuser...")
    
    # Get user input
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    first_name = input("First name (optional): ") or None
    last_name = input("Last name (optional): ") or None
    
    # Validate email
    if "@" not in email:
        print("Invalid email address")
        return
    
    # Validate password
    if len(password) < 8:
        print("Password must be at least 8 characters long")
        return
    
    try:
        # Create password hash
        password_helper = PasswordHelper()
        hashed_password = password_helper.hash(password)
        
        # Create user directly
        async with async_session_maker() as session:
            # Check if user already exists
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.email == email))
            existing_user = result.scalars().first()
            
            if existing_user:
                print(f"User with email {email} already exists")
                return
            
            # Create new user
            user = User(
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True,
                is_verified=True,
                first_name=first_name,
                last_name=last_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                monthly_matches_used=0,
                last_match_reset=datetime.utcnow()
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"Superuser created successfully!")
            print(f"Email: {user.email}")
            print(f"ID: {user.id}")
            
    except Exception as e:
        print(f"Error creating superuser: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_superuser())