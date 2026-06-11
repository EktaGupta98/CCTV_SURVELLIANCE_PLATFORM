import logging
import cv2
from typing import Generator, Dict, Any, List
from ultralytics import YOLO
from app.core.config import settings

logger = logging.getLogger(__name__)

class YOLOTracker:
    """
    Service to perform object detection and tracking on video streams using YOLOv8 and ByteTrack.
    """
    def __init__(self):
        self.model_name = settings.YOLO_MODEL
        logger.info(f"Initializing YOLO model: {self.model_name}")
        try:
            # Load YOLO model (downloads weights if not cached)
            self.model = YOLO(self.model_name)
            logger.info("YOLO model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise e

    def track_video(self, filepath: str) -> Generator[Dict[str, Any], None, None]:
        """
        Processes a video file frame by frame using YOLOv8 + ByteTrack.
        Yields detections and metadata for each frame.
        """
        logger.info(f"Starting tracking on video: {filepath}")
        try:
            # Run tracking with ByteTrack persistence
            # classes: 0 is person, 1-3/5/7 are vehicles (bicycle, car, motorcycle, bus, truck)
            # We track these to avoid tracking random background noise
            results = self.model.track(
                source=filepath,
                stream=True,
                persist=True,
                tracker="bytetrack.yaml",
                conf=0.25,
                iou=0.45,
                classes=[0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck
            )

            for frame_idx, r in enumerate(results):
                # Check if boxes are found and have track IDs
                boxes = r.boxes
                if boxes is None or len(boxes) == 0:
                    continue

                detections_in_frame = []
                orig_img = r.orig_img  # NumPy BGR frame

                for box in boxes:
                    # Check if tracker ID is assigned
                    if box.id is None:
                        continue
                    
                    track_id = int(box.id[0].item())
                    cls_idx = int(box.cls[0].item())
                    class_name = r.names[cls_idx]
                    confidence = float(box.conf[0].item())
                    
                    # Coordinates: [x1, y1, x2, y2]
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    x1, y1, x2, y2 = xyxy

                    detections_in_frame.append({
                        "local_track_id": track_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2]
                    })

                yield {
                    "frame_number": frame_idx + 1,
                    "frame_img": orig_img,
                    "detections": detections_in_frame
                }

        except Exception as e:
            logger.error(f"Error during YOLO tracking execution: {e}")
            raise e

_yolo_tracker_instance = None


def get_yolo_tracker() -> YOLOTracker:
    global _yolo_tracker_instance
    if _yolo_tracker_instance is None:
        _yolo_tracker_instance = YOLOTracker()
    return _yolo_tracker_instance
