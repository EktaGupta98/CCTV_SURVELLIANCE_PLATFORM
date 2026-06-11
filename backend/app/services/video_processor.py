import os
import uuid
import cv2
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from PIL import Image
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.video import Video
from app.models.camera import Camera
from app.models.processing_job import ProcessingJob
from app.models.entity import Entity
from app.models.track import Track
from app.models.detection import Detection
from app.models.entity_history import EntityHistory
from app.repositories.video_repository import video_repository
from app.repositories.job_repository import job_repository
from app.repositories.camera_repository import camera_repository
from app.repositories.entity_repository import entity_repository
from app.services.yolo_tracker import get_yolo_tracker
from app.services.clip_embedder import get_clip_embedder
from app.services.reid_service import reid_service

logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Orchestration service to process video streams.
    Extracts frames, runs YOLO + ByteTrack, generates crops and CLIP embeddings,
    performs cross-camera Re-ID, and stores metadata in PostgreSQL.
    """
    
    def process_video(self, db: Session, video_id: uuid.UUID, job_id: uuid.UUID) -> None:
        """
        Executes the video pipeline asynchronously.
        """
        logger.info(f"Starting pipeline processing for video ID: {video_id}, job ID: {job_id}")
        
        # 1. Update job to PROCESSING
        job = job_repository.update_progress(db, str(job_id), "PROCESSING", 0.0)
        video = db.query(Video).filter(Video.id == video_id).first()
        
        if not video:
            error_msg = f"Video with ID {video_id} not found."
            logger.error(error_msg)
            job_repository.update_progress(db, str(job_id), "FAILED", 0.0)
            return
            
        video.status = "PROCESSING"
        db.add(video)
        db.commit()
        
        try:
            # Get video metadata details
            cap = cv2.VideoCapture(video.filepath)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            if fps <= 0:
                fps = 30.0
                
            if total_frames <= 0:
                total_frames = 1000  # Fallback approximation if metadata read failed
                
            logger.info(f"Video specs: {total_frames} total frames, {fps} FPS, path: {video.filepath}")
            
            # Temporary storage to aggregate crops and details for each track in this video
            # local_track_id -> { "class_name": str, "crops": [PIL.Image], "detections": [dict] }
            tracks_accumulator: Dict[int, Dict[str, Any]] = {}
            
            # 2. Run Frame Extraction + YOLO Detection + ByteTrack
            frame_generator = get_yolo_tracker().track_video(video.filepath)
            
            for step_idx, frame_data in enumerate(frame_generator):
                frame_number = frame_data["frame_number"]
                frame_img = frame_data["frame_img"]  # BGR Image
                detections = frame_data["detections"]
                
                # Calculate real-world timestamp for this frame
                frame_offset_seconds = (frame_number - 1) / fps
                frame_timestamp = video.video_timestamp + timedelta(seconds=frame_offset_seconds)
                
                for det in detections:
                    track_id = det["local_track_id"]
                    class_name = det["class_name"]
                    confidence = det["confidence"]
                    bbox = det["bbox"]  # [x1, y1, x2, y2]
                    
                    # Crop image from frame
                    h, w = frame_img.shape[:2]
                    x1, y1, x2, y2 = map(int, bbox)
                    # Clip coordinates to frame boundaries
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    
                    if (x2 - x1) <= 0 or (y2 - y1) <= 0:
                        continue
                        
                    crop_img_bgr = frame_img[y1:y2, x1:x2]
                    
                    # Convert to PIL Image for CLIP
                    crop_img_rgb = cv2.cvtColor(crop_img_bgr, cv2.COLOR_BGR2RGB)
                    pil_crop = Image.fromarray(crop_img_rgb)
                    
                    # Accumulate track data
                    if track_id not in tracks_accumulator:
                        tracks_accumulator[track_id] = {
                            "class_name": class_name,
                            "crops": [],
                            "detections": []
                        }
                        
                    # Save crop image to file system as thumbnail
                    thumbnail_filename = f"{uuid.uuid4()}.jpg"
                    thumbnail_filepath = os.path.join(settings.THUMBNAIL_DIR, thumbnail_filename)
                    cv2.imwrite(thumbnail_filepath, crop_img_bgr)
                    thumbnail_url = f"/thumbnails/{thumbnail_filename}"
                    
                    tracks_accumulator[track_id]["crops"].append(pil_crop)
                    tracks_accumulator[track_id]["detections"].append({
                        "frame_number": frame_number,
                        "timestamp": frame_timestamp,
                        "confidence": confidence,
                        "bbox": bbox,
                        "thumbnail_path": thumbnail_url
                    })
                    
                # Update progress in DB every 10 frames to avoid DB overhead
                if frame_number % 20 == 0 or frame_number == total_frames:
                    progress_pct = min(100.0, (frame_number / total_frames) * 80.0)  # Reserve 20% for Re-ID/DB inserts
                    job_repository.update_progress(db, str(job_id), "PROCESSING", progress_pct)
            
            # 3. CLIP Embedding Generation + Cross Camera Re-ID + Database Insertions
            total_tracks = len(tracks_accumulator)
            logger.info(f"Finished tracking. Found {total_tracks} unique local tracks to process.")
            
            # Fetch camera metadata for coordinate assignments
            camera = camera_repository.get(db, video.camera_id)
            lat = camera.latitude if camera else 0.0
            lon = camera.longitude if camera else 0.0
            
            for track_idx, (local_track_id, track_data) in enumerate(tracks_accumulator.items()):
                class_name = track_data["class_name"]
                crops = track_data["crops"]
                detections = track_data["detections"]
                
                # Subsample crops to generate embeddings (maximum 5 evenly spaced crops to optimize execution speed)
                num_crops = len(crops)
                step = max(1, num_crops // 5)
                subsampled_crops = [crops[i] for i in range(0, num_crops, step)][:5]
                
                embeddings = []
                for crop in subsampled_crops:
                    emb = get_clip_embedder().generate_embedding(crop)
                    embeddings.append(emb)
                    
                # Compute average embedding for this track
                if embeddings:
                    avg_embedding = np.mean(embeddings, axis=0).tolist()
                else:
                    avg_embedding = [0.0] * 512
                    
                # Perform Re-ID matching against existing database entities
                matched_entity = reid_service.match_entity(db, class_name, avg_embedding)
                
                if matched_entity:
                    # Link to existing entity
                    entity_id = matched_entity.id
                    # Optionally update entity embedding by averaging (running average or keep original)
                    # For simplicity, we keep original, or we can update it. Let's keep original to avoid drift
                else:
                    # Create new global entity
                    new_entity = Entity(
                        class_name=class_name,
                        embedding=avg_embedding
                    )
                    db.add(new_entity)
                    db.commit()
                    db.refresh(new_entity)
                    entity_id = new_entity.id
                    
                # Insert Track record
                new_track = Track(
                    video_id=video_id,
                    entity_id=entity_id,
                    local_track_id=local_track_id,
                    class_name=class_name
                )
                db.add(new_track)
                db.commit()
                db.refresh(new_track)
                
                # Insert Detections and Entity History records
                for det in detections:
                    new_detection = Detection(
                        video_id=video_id,
                        track_id=new_track.id,
                        frame_number=det["frame_number"],
                        timestamp=det["timestamp"],
                        confidence=det["confidence"],
                        bbox_x1=det["bbox"][0],
                        bbox_y1=det["bbox"][1],
                        bbox_x2=det["bbox"][2],
                        bbox_y2=det["bbox"][3],
                        latitude=lat,
                        longitude=lon,
                        thumbnail_path=det["thumbnail_path"]
                    )
                    db.add(new_detection)
                    db.commit()
                    db.refresh(new_detection)
                    
                    # Create matching Entity History entry for tracing
                    new_history = EntityHistory(
                        entity_id=entity_id,
                        video_id=video_id,
                        camera_id=video.camera_id,
                        detection_id=new_detection.id,
                        timestamp=det["timestamp"],
                        latitude=lat,
                        longitude=lon
                    )
                    db.add(new_history)
                    
                # Update progress
                db.commit()
                progress_pct = 80.0 + ( (track_idx + 1) / total_tracks * 20.0 )
                job_repository.update_progress(db, str(job_id), "PROCESSING", progress_pct)
                
            # Completed
            video.status = "COMPLETED"
            db.add(video)
            db.commit()
            job_repository.update_progress(db, str(job_id), "COMPLETED", 100.0)
            logger.info(f"Video {video_id} processing successfully completed.")
            
        except Exception as e:
            logger.error(f"Pipeline processing failed for video ID {video_id}: {e}", exc_info=True)
            video.status = "FAILED"
            video.error_message = str(e)
            db.add(video)
            db.commit()
            
            # Retrieve active session
            job_repository.update_progress(db, str(job_id), "FAILED", 100.0)

video_processor = VideoProcessor()
