from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.processing_job import ProcessingJob

class JobRepository(BaseRepository[ProcessingJob]):
    """
    Repository for ProcessingJob operations.
    """
    def __init__(self):
        super().__init__(ProcessingJob)

    def get_by_video(self, db: Session, video_id: str) -> Optional[ProcessingJob]:
        return db.query(ProcessingJob).filter(ProcessingJob.video_id == video_id).first()

    def update_progress(self, db: Session, job_id: str, status: str, progress: float) -> Optional[ProcessingJob]:
        job = self.get(db, job_id)
        if job:
            job.status = status
            job.progress = progress
            db.add(job)
            db.commit()
            db.refresh(job)
        return job

job_repository = JobRepository()
