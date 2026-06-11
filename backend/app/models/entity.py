import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Entity(Base):
    """
    SQLAlchemy model representing a unique tracked physical entity (e.g., person, vehicle).
    Maintains a global identity across different cameras/videos using a CLIP embedding.
    """
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    class_name = Column(String(50), nullable=False, index=True)  # person, vehicle, bicycle, etc.
    embedding = Column(ARRAY(Float), nullable=False)  # CLIP 512-dimensional feature vector
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tracks = relationship("Track", back_populates="entity", cascade="all, delete-orphan")
    history_records = relationship("EntityHistory", back_populates="entity", cascade="all, delete-orphan")
