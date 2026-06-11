import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    PROJECT_NAME: str = "AI Surveillance Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database configurations
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "surveillance")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # File upload configurations
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    THUMBNAIL_DIR: str = os.getenv("THUMBNAIL_DIR", "data/thumbnails")
    
    # Security/limits
    # MAX_UPLOAD_SIZE supports 2-hour videos at typical bitrate (2-5 Mbps = 1.8-4.5 GB)
    # Set to 10GB to handle high-bitrate 2-hour videos with safety margin
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 10737418240))  # 10GB (10 * 1024 * 1024 * 1024)
    ALLOWED_EXTENSIONS: List[str] = ["mp4", "avi", "mkv", "mov"]
    
    # Database capacity
    MAX_CONCURRENT_VIDEOS: int = 500  # System supports up to 500 concurrent videos
    MAX_VIDEO_DURATION_SECONDS: int = 7200  # 2 hours (matches Celery task_time_limit)
    
    # AI models configurations
    YOLO_MODEL: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
    CLIP_MODEL: str = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
    REID_THRESHOLD: float = float(os.getenv("REID_THRESHOLD", 0.75))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.THUMBNAIL_DIR, exist_ok=True)
