from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

class VideoBase(BaseModel):
    camera_id: UUID = Field(..., description="Foreign key reference to Camera ID")
    filename: str = Field(..., max_length=255, description="Original filename")
    video_timestamp: datetime = Field(..., description="Real-world start timestamp of the CCTV recording")

class VideoCreate(VideoBase):
    filepath: str

class VideoResponse(VideoBase):
    id: UUID
    status: str
    error_message: Optional[str] = None
    upload_timestamp: datetime

    class Config:
        from_attributes = True

class VideoUploadResponse(BaseModel):
    video_id: UUID = Field(..., description="Database record ID for the uploaded video")
    job_id: UUID = Field(..., description="Celery background task processing job ID")
    status: str = Field("PENDING", description="Initial status of the video job")
