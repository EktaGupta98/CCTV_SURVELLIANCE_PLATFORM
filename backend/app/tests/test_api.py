import os
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# Mock the database engine creation and metadata on import
with patch("app.core.database.create_engine"), \
     patch("app.core.database.declarative_base"), \
     patch("app.core.database.sessionmaker"), \
     patch("app.core.database.Base.metadata.create_all"):
    from app.main import app
    from app.core.database import get_db

client = TestClient(app)

# Helper mock for DB session dependency override
@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()

def test_health_endpoint():
    """
    Test that the /health endpoint is live and returns healthy status.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("app.api.videos.process_video_task.delay")
@patch("app.api.videos.camera_repository")
@patch("app.api.videos.video_repository")
@patch("app.api.videos.job_repository")
def test_video_upload(
    mock_job_repo,
    mock_video_repo,
    mock_camera_repo,
    mock_celery_task,
    mock_db
):
    """
    Test uploading a video. Verifies validations, camera resolution, job creation, and Celery task dispatch.
    """
    # 1. Configure mocks
    mock_camera = MagicMock()
    mock_camera.id = uuid.uuid4()
    mock_camera_repo.get_by_location.return_value = mock_camera
    
    mock_video = MagicMock()
    mock_video.id = uuid.uuid4()
    mock_video_repo.create.return_value = mock_video
    
    mock_job = MagicMock()
    mock_job.id = uuid.uuid4()
    mock_job_repo.create.return_value = mock_job

    # Create dummy video content (bytes)
    video_content = b"fake video data content for testing upload limits"
    
    # 2. Call endpoint
    response = client.post(
        "/api/v1/videos/upload",
        data={
            "camera_name": "Main Gate Cam 1",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "video_timestamp": "2026-06-09T12:00:00"
        },
        files={"file": ("test_video.mp4", video_content, "video/mp4")}
    )
    
    # 3. Assertions
    assert response.status_code == 202
    res_json = response.json()
    assert "video_id" in res_json
    assert "job_id" in res_json
    assert res_json["status"] == "PENDING"
    
    # Check that celery task was dispatched
    mock_celery_task.assert_called_once()

@patch("app.api.processing.job_repository.get")
def test_processing_status(mock_job_get, mock_db):
    """
    Test retrieving processing job status.
    """
    job_id = uuid.uuid4()
    video_id = uuid.uuid4()
    mock_job = MagicMock()
    mock_job.id = job_id
    mock_job.video_id = video_id
    mock_job.status = "PROCESSING"
    mock_job.progress = 45.5
    mock_job.created_at = datetime.utcnow()
    mock_job.updated_at = datetime.utcnow()
    
    mock_job_get.return_value = mock_job
    
    response = client.get(f"/api/v1/processing/{job_id}")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["id"] == str(job_id)
    assert res_json["status"] == "PROCESSING"
    assert res_json["progress"] == 45.5

@patch("app.api.entities.entity_repository.get")
@patch("app.api.entities.entity_repository.get_entity_history")
def test_entity_tracking_history(mock_history, mock_entity, mock_db):
    """
    Test retrieving tracking history for a specific entity.
    """
    entity_id = uuid.uuid4()
    video_id = uuid.uuid4()
    camera_id = uuid.uuid4()
    
    mock_ent = MagicMock()
    mock_ent.id = entity_id
    mock_ent.class_name = "person"
    mock_entity.return_value = mock_ent
    
    # Mock history records
    record = MagicMock()
    record.id = uuid.uuid4()
    record.entity_id = entity_id
    record.video_id = video_id
    record.camera_id = camera_id
    record.camera.name = "North Exit"
    record.detection_id = uuid.uuid4()
    record.timestamp = datetime.utcnow()
    record.latitude = 37.7749
    record.longitude = -122.4194
    record.detection.thumbnail_path = "/thumbnails/crop.jpg"
    
    mock_history.return_value = [record]
    
    response = client.get(f"/api/v1/entities/{entity_id}/history")
    assert response.status_code == 200
    res_json = response.json()
    assert len(res_json) == 1
    assert res_json[0]["camera_name"] == "North Exit"
    assert res_json[0]["class_name"] == "person"
    assert res_json[0]["thumbnail_path"] == "/thumbnails/crop.jpg"

@patch("app.api.entities.entity_repository.get")
@patch("app.api.entities.entity_repository.get_entity_history")
def test_entity_map_path(mock_history, mock_entity, mock_db):
    """
    Test retrieving Leaflet map formatted path tracking logs.
    """
    entity_id = uuid.uuid4()
    
    mock_ent = MagicMock()
    mock_ent.id = entity_id
    mock_ent.class_name = "car"
    mock_entity.return_value = mock_ent
    
    record = MagicMock()
    record.latitude = 34.0522
    record.longitude = -118.2437
    record.camera_id = uuid.uuid4()
    record.camera.name = "South Lane 2"
    record.timestamp = datetime.utcnow()
    record.detection.thumbnail_path = "/thumbnails/car_crop.jpg"
    
    mock_history.return_value = [record]
    
    response = client.get(f"/api/v1/entities/{entity_id}/map")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["entity_id"] == str(entity_id)
    assert res_json["class_name"] == "car"
    assert len(res_json["path"]) == 1
    assert res_json["path"][0]["latitude"] == 34.0522
    assert res_json["path"][0]["camera_name"] == "South Lane 2"

@patch("app.api.search.entity_repository.search_history")
def test_search_endpoint(mock_search_history, mock_db):
    """
    Test dynamic search API.
    """
    record = MagicMock()
    record.id = uuid.uuid4()
    record.entity_id = uuid.uuid4()
    record.video_id = uuid.uuid4()
    record.camera_id = uuid.uuid4()
    record.camera.name = "East Wall Cam"
    record.detection_id = uuid.uuid4()
    record.timestamp = datetime.utcnow()
    record.latitude = 37.7749
    record.longitude = -122.4194
    record.detection.thumbnail_path = "/thumbnails/search_crop.jpg"
    record.entity.class_name = "person"
    
    mock_search_history.return_value = [record]
    
    response = client.post(
        "/api/v1/search",
        json={
            "class_name": "person",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "radius_meters": 1000
        }
    )
    assert response.status_code == 200
    res_json = response.json()
    assert len(res_json) == 1
    assert res_json[0]["camera_name"] == "East Wall Cam"
    assert res_json[0]["class_name"] == "person"
