"""
Celery application configuration
"""

from celery import Celery

from app.core.config import settings


def create_celery_app() -> Celery:
    """
    Create and configure Celery application
    """
    celery_app = Celery(
        "resume_matcher",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=["app.services.tasks"]
    )
    
    # Configure Celery
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
        task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        # Use default queue for all tasks
        task_default_queue='default',
        task_routes={
            "app.services.tasks.*": {"queue": "default"},
        },
    )
    
    return celery_app


# Create global celery instance
celery_app = create_celery_app()