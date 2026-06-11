import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Track(Base):
    """
    SQLAlchemy model representing a local trajectory track inside a specific video.
    """
    __tablename__ = "tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    local_track_id = Column(Integer, nullable=False)  # Track ID assigned by ByteTrack in this video
    class_name = Column(String(50), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    video = relationship("Video", back_populates="tracks")
    entity = relationship("Entity", back_populates="tracks")
    detections = relationship("Detection", back_populates="track", cascade="all, delete-orphan")
