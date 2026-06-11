import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.processing_job import ProcessingJobResponse
from app.repositories.job_repository import job_repository

router = APIRouter(prefix="/processing", tags=["Processing"])

@router.get("/{id}", response_model=ProcessingJobResponse)
def get_processing_status(id: str, db: Session = Depends(get_db)):
    """
    Retrieve current status and progress of a background video processing job.
    """
    try:
        job_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format. Must be a valid UUID."
        )

    job = job_repository.get(db, job_uuid)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processing job with ID {id} not found."
        )
        
    return job
