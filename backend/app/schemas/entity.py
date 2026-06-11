from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class EntityResponse(BaseModel):
    id: UUID
    class_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EntityHistoryResponse(BaseModel):
    id: UUID
    entity_id: UUID
    video_id: UUID
    camera_id: UUID
    camera_name: str
    detection_id: UUID
    timestamp: datetime
    latitude: float
    longitude: float
    thumbnail_path: Optional[str] = None
    class_name: str

    class Config:
        from_attributes = True

class EntityMapMarker(BaseModel):
    latitude: float
    longitude: float
    camera_id: UUID
    camera_name: str
    timestamp: datetime
    thumbnail_path: Optional[str] = None
    class_name: str

class EntityMapPathResponse(BaseModel):
    entity_id: UUID
    class_name: str
    path: List[EntityMapMarker]

    class Config:
        from_attributes = True

class EntitySearchRequest(BaseModel):
    entity_id: Optional[UUID] = None
    camera_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    class_name: Optional[str] = None  # e.g., 'person', 'vehicle', etc.
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[float] = Field(None, description="Search radius in meters around latitude/longitude")
    skip: int = 0
    limit: int = 100
