#!/usr/bin/env python3
"""
Initialize the authentication database
"""

import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.init_db import init_db
from app.core.config import settings

async def main():
    """
    Main function to initialize the database
    """
    print(f"Initializing database at: {settings.DATABASE_URL}")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Initialize database
    await init_db()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    asyncio.run(main())