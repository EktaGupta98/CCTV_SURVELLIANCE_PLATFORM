from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.video import Video

class VideoRepository(BaseRepository[Video]):
    """
    Repository for Video operations.
    """
    def __init__(self):
        super().__init__(Video)

    def get_by_camera(self, db: Session, camera_id: str) -> List[Video]:
        return db.query(Video).filter(Video.camera_id == camera_id).all()

video_repository = VideoRepository()
