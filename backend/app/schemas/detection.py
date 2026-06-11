from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class DetectionResponse(BaseModel):
    id: UUID
    video_id: UUID
    track_id: Optional[UUID] = None
    frame_number: int
    timestamp: datetime
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    latitude: float
    longitude: float
    thumbnail_path: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }
