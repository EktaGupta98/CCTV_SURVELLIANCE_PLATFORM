import uuid
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Camera(Base):
    """
    SQLAlchemy model representing a physical CCTV camera.
    """
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    videos = relationship("Video", back_populates="camera", cascade="all, delete-orphan")
    history_records = relationship("EntityHistory", back_populates="camera", cascade="all, delete-orphan")
