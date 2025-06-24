"""
Health check endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.celery_app import celery_app
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def root():
    """
    Basic health check endpoint
    """
    return {
        "message": f"{settings.PROJECT_NAME} is running",
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check including all system components
    """
    try:
        # Check Celery workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        celery_status = "healthy" if active_workers else "no_workers"
        worker_count = len(active_workers) if active_workers else 0
        
        # Check Redis connection
        redis_status = "healthy"
        try:
            from redis import Redis
            from urllib.parse import urlparse
            
            parsed_url = urlparse(settings.REDIS_URL)
            redis_client = Redis(
                host=parsed_url.hostname,
                port=parsed_url.port,
                db=int(parsed_url.path[1:]) if parsed_url.path else 0,
                password=parsed_url.password,
                socket_timeout=5
            )
            redis_client.ping()
        except Exception as e:
            redis_status = f"error: {str(e)}"
        
        health_data = {
            "api_status": "healthy",
            "celery_status": celery_status,
            "redis_status": redis_status,
            "active_workers": worker_count,
            "settings": {
                "debug": settings.DEBUG,
                "environment": settings.ENVIRONMENT,
                "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
                "similarity_threshold": settings.SIMILARITY_THRESHOLD
            }
        }
        
        # Determine overall health
        is_healthy = all([
            celery_status == "healthy",
            redis_status == "healthy"
        ])
        
        status_code = 200 if is_healthy else 503
        
        return JSONResponse(
            status_code=status_code,
            content=health_data
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "api_status": "healthy",
                "celery_status": "error",
                "redis_status": "error", 
                "error": str(e)
            }
        )


@router.get("/readiness")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    try:
        # Quick check of essential services
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if not active_workers:
            raise HTTPException(status_code=503, detail="No Celery workers available")
        
        return {"status": "ready"}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/liveness")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return {"status": "alive"}