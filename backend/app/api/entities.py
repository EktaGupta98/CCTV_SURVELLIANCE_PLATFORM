import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.entity import EntityResponse, EntityHistoryResponse, EntityMapPathResponse, EntityMapMarker
from app.repositories.entity_repository import entity_repository
from app.models.entity import Entity
from app.models.entity_history import EntityHistory
from app.models.camera import Camera
from app.models.detection import Detection

router = APIRouter(prefix="/entities", tags=["Entities"])

@router.get("", response_model=List[EntityResponse])
def get_all_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve list of all unique global entities identified across all cameras.
    """
    return entity_repository.get_multi(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=EntityResponse)
def get_entity_by_id(id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific global entity's basic details.
    """
    try:
        entity_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entity ID format. Must be a valid UUID."
        )

    entity = entity_repository.get(db, entity_uuid)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {id} not found."
        )
    return entity

@router.get("/{id}/history", response_model=List[EntityHistoryResponse])
def get_entity_history(id: str, db: Session = Depends(get_db)):
    """
    Retrieve the ordered, chronological movement history of a specific entity.
    """
    try:
        entity_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entity ID format. Must be a valid UUID."
        )

    entity = entity_repository.get(db, entity_uuid)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {id} not found."
        )

    history_records = entity_repository.get_entity_history(db, entity_uuid)
    
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
            class_name=entity.class_name
        ))
    return response

@router.get("/{id}/map", response_model=EntityMapPathResponse)
def get_entity_map_path(id: str, db: Session = Depends(get_db)):
    """
    Retrieve tracking coordinate path details formatted specifically for Leaflet map polylines and markers.
    """
    try:
        entity_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entity ID format. Must be a valid UUID."
        )

    entity = entity_repository.get(db, entity_uuid)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {id} not found."
        )

    history_records = entity_repository.get_entity_history(db, entity_uuid)
    
    path_markers = []
    for record in history_records:
        path_markers.append(EntityMapMarker(
            latitude=record.latitude,
            longitude=record.longitude,
            camera_id=record.camera_id,
            camera_name=record.camera.name if record.camera else "Unknown Camera",
            timestamp=record.timestamp,
            thumbnail_path=record.detection.thumbnail_path if record.detection else None,
            class_name=entity.class_name
        ))

    return EntityMapPathResponse(
        entity_id=entity.id,
        class_name=entity.class_name,
        path=path_markers
    )
