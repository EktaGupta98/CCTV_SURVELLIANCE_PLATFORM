from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.camera import CameraResponse, CameraCreate
from app.models.camera import Camera
from app.repositories.camera_repository import camera_repository

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.get("", response_model=List[CameraResponse])
def get_cameras(db: Session = Depends(get_db)):
    """
    Retrieve all registered camera locations.
    """
    return camera_repository.get_multi(db, limit=500)

@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(camera_in: CameraCreate, db: Session = Depends(get_db)):
    """
    Register a new camera location.
    """
    # Check if a camera exists at this location
    existing = camera_repository.get_by_location(db, camera_in.latitude, camera_in.longitude)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A camera already exists at this location."
        )
        
    camera = Camera(
        name=camera_in.name,
        latitude=camera_in.latitude,
        longitude=camera_in.longitude
    )
    return camera_repository.create(db, camera)
