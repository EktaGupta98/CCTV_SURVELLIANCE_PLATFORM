import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class EntityHistory(Base):
    """
    SQLAlchemy model representing the movement history of a global entity across cameras and timestamps.
    Used for drawing trajectory maps and tracking lists.
    """
    __tablename__ = "entity_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Relationships
    entity = relationship("Entity", back_populates="history_records")
    video = relationship("Video", back_populates="history_records")
    camera = relationship("Camera", back_populates="history_records")
    detection = relationship("Detection", back_populates="history_record")
