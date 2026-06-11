import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Detection(Base):
    """
    SQLAlchemy model representing a single object detection in a specific video frame.
    """
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="CASCADE"), nullable=True, index=True)
    
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)  # Video start time + frame offset
    confidence = Column(Float, nullable=False)
    
    # Bounding Box coordinates (normalized or pixel space, pixel space is standard)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    
    # Geo location at time of detection (camera location)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Filepath to the visual cropped thumbnail
    thumbnail_path = Column(String(512), nullable=True)

    # Relationships
    video = relationship("Video", back_populates="detections")
    track = relationship("Track", back_populates="detections")
    history_record = relationship("EntityHistory", back_populates="detection", uselist=False, cascade="all, delete-orphan")
