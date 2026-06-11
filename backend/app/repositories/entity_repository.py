from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.repositories.base import BaseRepository
from app.models.entity import Entity
from app.models.entity_history import EntityHistory
from app.models.camera import Camera
from app.models.detection import Detection

class EntityRepository(BaseRepository[Entity]):
    """
    Repository for Entity and EntityHistory operations.
    """
    def __init__(self):
        super().__init__(Entity)

    def get_entities_by_class(self, db: Session, class_name: str) -> List[Entity]:
        """
        Get all entities with a matching class name (e.g. for Re-ID similarity check).
        """
        return db.query(Entity).filter(Entity.class_name == class_name).all()

    def get_entity_history(self, db: Session, entity_id: UUID) -> List[EntityHistory]:
        """
        Get the chronological tracking history of a specific entity.
        """
        return db.query(EntityHistory)\
            .filter(EntityHistory.entity_id == entity_id)\
            .order_by(EntityHistory.timestamp.asc())\
            .all()

    def search_history(
        self,
        db: Session,
        entity_id: Optional[UUID] = None,
        camera_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        class_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_meters: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[EntityHistory]:
        """
        Advanced dynamic search across entity histories.
        Allows filtering by entity, camera, class name, datetime ranges, and geospatial radius.
        """
        query = db.query(EntityHistory).join(Entity).join(Camera).join(Detection)
        filters = []

        if entity_id:
            filters.append(EntityHistory.entity_id == entity_id)
        if camera_id:
            filters.append(EntityHistory.camera_id == camera_id)
        if start_time:
            filters.append(EntityHistory.timestamp >= start_time)
        if end_time:
            filters.append(EntityHistory.timestamp <= end_time)
        if class_name:
            # Map search queries like "person" or "vehicle"
            if class_name.lower() in ["vehicle", "car", "truck", "bus"]:
                filters.append(Entity.class_name.in_(["car", "truck", "bus", "motorcycle", "vehicle"]))
            elif class_name.lower() in ["person", "pedestrian"]:
                filters.append(Entity.class_name == "person")
            else:
                filters.append(Entity.class_name.ilike(f"%{class_name}%"))

        # Simple geospatial distance filter if coordinates are provided
        if latitude is not None and longitude is not None and radius_meters is not None:
            # Simple approximation of distance (1 degree latitude ~ 111km)
            # distance_deg = radius_meters / 111000
            # A more precise formula is fine, but standard bounding box approximation or Haversine works.
            # Using basic distance check:
            # sqrt((lat - cam.lat)^2 + (lon - cam.lon)^2) * 111000 <= radius
            # Let's approximate using distance squared:
            lat_diff = Camera.latitude - latitude
            lon_diff = Camera.longitude - longitude
            # Simple Euclidean distance squared for database performance
            # (111000 meters per lat deg, 111000 * cos(lat) per lon deg)
            approx_dist = func.sqrt(func.pow(lat_diff, 2) + func.pow(lon_diff, 2)) * 111000
            filters.append(approx_dist <= radius_meters)

        if filters:
            query = query.filter(and_(*filters))

        # Return ordered tracking history chronologically
        return query.order_by(EntityHistory.timestamp.asc())\
            .offset(skip)\
            .limit(limit)\
            .all()

entity_repository = EntityRepository()
