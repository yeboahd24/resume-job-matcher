"""
Main API router that includes all endpoint routers
"""

from fastapi import APIRouter

from app.api.endpoints import health, jobs, tasks, auth

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])