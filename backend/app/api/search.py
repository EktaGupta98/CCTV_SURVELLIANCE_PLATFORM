from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.entity import EntitySearchRequest, EntityHistoryResponse
from app.repositories.entity_repository import entity_repository

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=List[EntityHistoryResponse], status_code=status.HTTP_200_OK)
def search_entities_history(
    filters: EntitySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search and filter identified entity movement logs by multiple optional criteria:
    Entity ID, Camera, Date Range, Class Type, and Geo Coordinate Radius.
    Returns tracking logs ordered chronologically.
    """
    history_records = entity_repository.search_history(
        db=db,
        entity_id=filters.entity_id,
        camera_id=filters.camera_id,
        start_time=filters.start_time,
        end_time=filters.end_time,
        class_name=filters.class_name,
        latitude=filters.latitude,
        longitude=filters.longitude,
        radius_meters=filters.radius_meters,
        skip=filters.skip,
        limit=filters.limit
    )

    response = []
    for record in history_records:
        response.append(EntityHistoryResponse(
            id=record.id,
            entity_id=record.entity_id,
            video_id=record.video_id,
            camera_id=record.camera_id,
            camera_name=record.camera.name if record.camera else "Unknown Camera",
            detection_id=record.detection_id,
            timestamp=record.timestamp,
            latitude=record.latitude,
            longitude=record.longitude,
            thumbnail_path=record.detection.thumbnail_path if record.detection else None,
            class_name=record.entity.class_name if record.entity else "Unknown"
        ))
    return response
