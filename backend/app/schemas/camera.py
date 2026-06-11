from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class CameraBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name or identifier of the camera")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }
