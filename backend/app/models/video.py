import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Video(Base):
    """
    SQLAlchemy model representing a recorded or uploaded CCTV video.
    """
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    video_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)  # Real-world video start time

    # Relationships
    camera = relationship("Camera", back_populates="videos")
    jobs = relationship("ProcessingJob", back_populates="video", cascade="all, delete-orphan")
    tracks = relationship("Track", back_populates="video", cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="video", cascade="all, delete-orphan")
    history_records = relationship("EntityHistory", back_populates="video", cascade="all, delete-orphan")
