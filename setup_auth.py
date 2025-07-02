#!/usr/bin/env python3
"""
Setup authentication system
"""

import asyncio
import os
import sys
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.init_db import init_db
from app.core.config import settings

async def setup_authentication():
    """
    Setup the authentication system
    """
    print("🔧 Setting up Authentication System")
    print("=" * 40)
    
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
            print("✅ Authentication system setup complete!")
            return
    
    # Initialize database
    print("🗄️  Initializing database...")
    await init_db()
    
    print("✅ Authentication system setup complete!")
    print()
    print("🎯 Next Steps:")
    print("   1. Install new dependencies: pip install -r requirements.txt")
    print("   2. Start the API server: python main.py")
    print("   3. Create a superuser: python create_admin_user.py")
    print("   4. Test the system: python test_auth_system.py")
    print()
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔐 Authentication endpoints: http://localhost:8000/docs#/auth")

if __name__ == "__main__":
    asyncio.run(setup_authentication())