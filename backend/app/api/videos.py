import os
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.video import Video
from app.models.camera import Camera
from app.models.processing_job import ProcessingJob
from app.schemas.video import VideoResponse, VideoUploadResponse
from app.repositories.video_repository import video_repository
from app.repositories.camera_repository import camera_repository
from app.repositories.job_repository import job_repository
from app.workers.tasks import process_video_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    camera_name: str = Form(..., description="Name of the CCTV camera"),
    latitude: float = Form(..., description="Latitude coordinate of camera"),
    longitude: float = Form(..., description="Longitude coordinate of camera"),
    video_timestamp: str = Form(..., description="Real-world start ISO datetime of video recording"),
    camera_id: Optional[str] = Form(None, description="Optional existing camera UUID string"),
    file: UploadFile = File(..., description="CCTV MP4/AVI/MKV/MOV video file"),
    db: Session = Depends(get_db)
):
    """
    Ingest a CCTV footage video file.
    Validates limits (500MB), extensions, maps camera, saves under UUID,
    immediately returns a Processing Job ID, and triggers background tracking task.
    """
    logger.info(f"Received video upload request for Camera: {camera_name}")
    
    # 1. Parse video timestamp
    try:
        parsed_timestamp = datetime.fromisoformat(video_timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid video_timestamp format. Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SS)."
        )

    # 2. Validate file extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension .{file_ext} is not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 3. Validate file size and save upload in chunks
    file_size = 0
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    saved_filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(saved_filepath, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > settings.MAX_UPLOAD_SIZE:
                    max_size_gb = settings.MAX_UPLOAD_SIZE / (1024*1024*1024)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {max_size_gb:.1f} GB. Supports up to 2-hour videos at typical bitrate (2-5 Mbps)."
                    )
                f.write(chunk)
    except HTTPException:
        if os.path.exists(saved_filepath):
            os.remove(saved_filepath)
        raise
    except Exception as e:
        if os.path.exists(saved_filepath):
            os.remove(saved_filepath)
        logger.error(f"Failed to write uploaded file to disk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file to server filesystem."
        )

    # 4. Resolve Camera
    camera = None
    if camera_id:
        try:
            cam_uuid = uuid.UUID(camera_id)
            camera = camera_repository.get(db, cam_uuid)
        except ValueError:
            pass
            
    if not camera:
        # Fallback to look up by coordinate proximity or create
        camera = camera_repository.get_by_location(db, latitude, longitude)
        
    if not camera:
        # Create new Camera
        camera = Camera(
            name=camera_name,
            latitude=latitude,
            longitude=longitude
        )
        db.add(camera)
        db.commit()
        db.refresh(camera)
        logger.info(f"Registered new camera: {camera.id}")

    # 6. Create Video Database record
    new_video = Video(
        camera_id=camera.id,
        filename=file.filename,
        filepath=saved_filepath,
        status="PENDING",
        video_timestamp=parsed_timestamp
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    # 7. Create Job Database record
    new_job = ProcessingJob(
        video_id=new_video.id,
        status="PENDING",
        progress=0.0
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 8. Trigger Celery Asynchronous task
    process_video_task.delay(str(new_video.id), str(new_job.id))
    logger.info(f"Dispatched background processing job: {new_job.id} for video: {new_video.id}")

    return VideoUploadResponse(
        video_id=new_video.id,
        job_id=new_job.id,
        status="PENDING"
    )

@router.get("", response_model=List[VideoResponse])
def get_all_videos(db: Session = Depends(get_db)):
    """
    Retrieve list of all ingested CCTV videos and their processing statuses.
    """
    return video_repository.get_multi(db, limit=500)
