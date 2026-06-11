from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ProcessingJobResponse(BaseModel):
    id: UUID
    video_id: UUID
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    progress: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
