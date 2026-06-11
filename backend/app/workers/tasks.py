import logging
import uuid
from celery.exceptions import MaxRetriesExceededError
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.video_processor import video_processor
from app.repositories.job_repository import job_repository

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_task(self, video_id_str: str, job_id_str: str) -> str:
    """
    Celery task to run the video pipeline processing asynchronously.
    Supports retrying up to 3 times on transient failures.
    """
    logger.info(f"Celery worker picked up video processing job: {job_id_str} for video: {video_id_str}")
    
    video_id = uuid.UUID(video_id_str)
    job_id = uuid.UUID(job_id_str)
    
    # Create manual DB session for worker execution
    db = SessionLocal()
    try:
        # Run processing orchestration
        video_processor.process_video(db, video_id, job_id)
        return f"Successfully processed video: {video_id_str}"
    except Exception as e:
        logger.error(f"Error in process_video_task (Job: {job_id_str}): {e}", exc_info=True)
        # Handle retry on exception
        try:
            # Re-raise to trigger Celery retry
            self.retry(exc=e)
        except MaxRetriesExceededError:
            # If maximum retries exceeded, ensure job and video status is set to FAILED
            logger.error(f"Job {job_id_str} exceeded maximum retries. Setting status to FAILED.")
            # Set job progress and status
            job_repository.update_progress(db, job_id_str, "FAILED", 100.0)
            db.commit()
            return f"Failed processing video: {video_id_str} after maximum retries"
    finally:
        db.close()
