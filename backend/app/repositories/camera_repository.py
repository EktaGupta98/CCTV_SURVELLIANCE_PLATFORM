from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.camera import Camera

class CameraRepository(BaseRepository[Camera]):
    """
    Repository for Camera operations.
    """
    def __init__(self):
        super().__init__(Camera)

    def get_by_name(self, db: Session, name: str) -> Optional[Camera]:
        return db.query(Camera).filter(Camera.name == name).first()

    def get_by_location(self, db: Session, latitude: float, longitude: float) -> Optional[Camera]:
        return db.query(Camera).filter(
            Camera.latitude == latitude,
            Camera.longitude == longitude
        ).first()

camera_repository = CameraRepository()
