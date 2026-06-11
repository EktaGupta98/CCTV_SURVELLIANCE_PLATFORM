import logging
import numpy as np
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repositories.entity_repository import entity_repository
from app.models.entity import Entity

logger = logging.getLogger(__name__)

class ReIDService:
    """
    Service to perform cross-camera re-identification using cosine similarity of CLIP embeddings.
    """
    def __init__(self):
        self.threshold = settings.REID_THRESHOLD

    def match_entity(
        self,
        db: Session,
        class_name: str,
        track_embedding: List[float]
    ) -> Optional[Entity]:
        """
        Compares a local track embedding against all existing database entities of the same class.
        Returns the matching Entity if similarity is above the threshold, else None.
        """
        # Retrieve all entities of the same class
        existing_entities = entity_repository.get_entities_by_class(db, class_name)
        if not existing_entities:
            return None

        # Convert track embedding to numpy array
        track_arr = np.array(track_embedding, dtype=np.float32)
        track_norm = np.linalg.norm(track_arr)
        
        if track_norm == 0:
            logger.warning("Empty local track embedding vector.")
            return None

        best_similarity = -1.0
        best_match_entity = None

        # Calculate cosine similarity with each existing entity
        for entity in existing_entities:
            entity_arr = np.array(entity.embedding, dtype=np.float32)
            entity_norm = np.linalg.norm(entity_arr)
            
            if entity_norm == 0:
                continue

            similarity = np.dot(track_arr, entity_arr) / (track_norm * entity_norm)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_entity = entity

        logger.info(f"Re-ID matching for {class_name}: highest similarity = {best_similarity:.4f} (threshold = {self.threshold})")

        if best_similarity >= self.threshold:
            logger.info(f"Match found! Entity ID: {best_match_entity.id}")
            return best_match_entity

        logger.info("No similarity match above threshold. A new entity ID will be created.")
        return None

reid_service = ReIDService()
