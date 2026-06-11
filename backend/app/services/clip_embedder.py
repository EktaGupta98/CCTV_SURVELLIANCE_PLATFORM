import logging
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from app.core.config import settings

logger = logging.getLogger(__name__)

class CLIPEmbedder:
    """
    Service to generate CLIP embeddings for image crops.
    Used in cross-camera re-identification.
    """
    def __init__(self):
        self.model_name = settings.CLIP_MODEL
        self.device = "cpu"  # Keep CPU for container/local compatibility by default
        logger.info(f"Initializing CLIP model: {self.model_name} on {self.device}")
        try:
            self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model.eval()
            logger.info("CLIP model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise e

    def generate_embedding(self, image: Image.Image) -> list:
        """
        Generates a 512-dimensional CLIP embedding vector for a PIL image crop.
        Normalizes the output vector.
        """
        try:
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            # L2 Normalize the embedding
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            # Convert to list
            embedding_vector = image_features[0].cpu().tolist()
            return embedding_vector
        except Exception as e:
            logger.error(f"Error generating CLIP embedding: {e}")
            # Return a dummy vector of 512 dimensions in case of failure to prevent pipeline breakage
            return [0.0] * 512

_clip_embedder_instance = None


def get_clip_embedder() -> CLIPEmbedder:
    global _clip_embedder_instance
    if _clip_embedder_instance is None:
        _clip_embedder_instance = CLIPEmbedder()
    return _clip_embedder_instance
