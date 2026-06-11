from fastapi import APIRouter, status
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def check_health():
    """
    Simple health check endpoint returning API status.
    """
    return HealthResponse(status="healthy")
