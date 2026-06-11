from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class TrackResponse(BaseModel):
    id: UUID
    video_id: UUID
    entity_id: UUID
    local_track_id: int
    class_name: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }
