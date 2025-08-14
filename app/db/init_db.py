"""
Database initialization script
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.user import Base

async def init_db():
    """
    Initialize database tables
    """
    # Create engine for initialization
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Close engine
    await engine.dispose()
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())