#!/usr/bin/env python3
"""
Complete setup for authentication system
"""

import asyncio
import os
import sys
import getpass
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from fastapi_users.password import PasswordHelper
from app.core.config import settings
from app.models.user import Base, User

async def setup_complete():
    """
    Complete setup for authentication system
    """
    print("🔧 Complete Authentication System Setup")
    print("=" * 50)
    
    # Create data directory
    print("📁 Creating data directory...")
    os.makedirs("data", exist_ok=True)
    
    # Check if SQLite database already exists
    db_path = "data/resumematcher.db"
    if os.path.exists(db_path):
        print(f"⚠️  Database already exists at {db_path}")
        choice = input("Do you want to reset the database? (y/n): ")
        if choice.lower() == 'y':
            print("🗑️  Removing existing database...")
            os.remove(db_path)
        else:
            print("✅ Using existing database")
            print("✅ Setup complete!")
            return
    
    # Create engine for initialization
    print("🔧 Creating database engine...")
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
    )
    
    # Create tables
    print("🗄️  Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Ask if user wants to create admin user
    print("\n🔐 Admin User Creation")
    create_admin = input("Do you want to create an admin user now? (y/n): ")
    
    if create_admin.lower() == 'y':
        print("\nCreating admin user...")
        
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
            
            # Create SQLAlchemy session
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy.orm import sessionmaker
            
            async_session = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )
            
            # Create user directly
            async with async_session() as session:
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
                
                print(f"✅ Admin user created successfully!")
                print(f"📧 Email: {user.email}")
                print(f"🆔 ID: {user.id}")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            import traceback
            traceback.print_exc()
    
    # Close engine
    await engine.dispose()
    
    print("\n✅ Authentication system setup complete!")
    print("\n🎯 Next Steps:")
    print("   1. Start the API server: python main.py")
    print("   2. Test the system: python test_auth_system.py")
    print("   3. Open auth_test.html in your browser to test the web interface")
    print("\n📖 API Documentation: http://localhost:8000/docs")
    print("🔐 Authentication endpoints: http://localhost:8000/docs#/auth")

if __name__ == "__main__":
    asyncio.run(setup_complete())