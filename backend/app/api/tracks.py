from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.track import TrackResponse
from app.models.track import Track

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.get("", response_model=List[TrackResponse])
def get_all_tracks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve list of all local tracks across CCTV videos.
    """
    tracks = db.query(Track).offset(skip).limit(limit).all()
    return tracks
