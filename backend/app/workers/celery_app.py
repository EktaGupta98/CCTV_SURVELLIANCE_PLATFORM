import logging
from celery import Celery
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "surveillance_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Optional configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Standard settings for video processing load
    worker_concurrency=1,  # Keep it 1 on single GPU/CPU setups to prevent memory/inference conflict
    task_time_limit=7200,   # 2 hours max per video task (per requirement 1: 'Support videos up to 2 hours each')
)

logger.info("Celery application configured.")
