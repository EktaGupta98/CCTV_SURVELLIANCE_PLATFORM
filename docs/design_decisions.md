# Design Decisions - AI Surveillance Platform

This document details the architectural decisions and technology stack selections made for the platform, outlining the technical rationale behind each selection.

## 1. Why FastAPI?
- **High Performance**: FastAPI is one of the fastest Python frameworks available, built on top of Starlette and Pydantic, matching Node.js and Go performance levels.
- **Asynchronous natively**: Supports modern async/await patterns out of the box, which is critical for handling concurrent file uploads and polling requests without blocking worker threads.
- **Automatic OpenAPI Documentation**: Generates interactive Swagger/ReDoc documentation automatically, making it extremely easy for developers to test and integrate APIs.

## 2. Why PostgreSQL?
- **Robustness and Reliability**: PostgreSQL is a highly robust, ACID-compliant relational database, perfect for structured, normalized tracking data (videos, cameras, tracks, detections).
- **Array Support**: Postgres has native support for array types (e.g. `ARRAY(Float)`). This is a clean and lightweight way to store 512-dimensional CLIP embeddings without requiring third-party vector databases.
- **Relational Integrity**: The relational structure allows us to enforce foreign key constraints across cameras, videos, tracks, and detections, which prevents data orphanages and keeps historical traces consistent.

## 3. Why YOLO (YOLOv8)?
- **State-of-the-Art Accuracy & Speed**: YOLOv8 provides real-time detection capabilities with high accuracy on various standard COCO classes (such as people, vehicles, etc.).
- **Ultralytics Ecosystem**: Ultralytics has an exceptionally well-maintained SDK. It loads models easily, runs on CPU/GPU natively, and handles the low-level image conversions automatically.
- **Built-in ByteTrack Support**: Ultralytics bundles ByteTrack directly into the tracking pipeline, avoiding complex dependency compilations.

## 4. Why ByteTrack?
- **Association by Detection Similarity**: ByteTrack is a highly robust tracking algorithm that associates bounding boxes frame-by-frame.
- **Handling Occlusions**: Unlike traditional trackers that discard low-score detections, ByteTrack keeps track of low-confidence boxes to resolve brief occlusions (e.g. person passing behind a pole), maintaining local track continuity.

## 5. Why CLIP?
- **Semantic Richness**: CLIP (Contrastive Language-Image Pre-Training) embeddings capture rich semantic features of image crops.
- **Zero-Shot Transferability**: CLIP performs extremely well on generic re-identification tasks (matching people and cars) without requiring specialized Re-ID training datasets.
- **Cosine Proximity**: Evaluating similarity is as simple as computing a cosine dot product, which is fast and mathematically sound.

## 6. Why Celery & Redis?
- **Asynchronous Task Offloading**: Video file processing is extremely heavy. A 2-hour video cannot be processed synchronously within an HTTP request life-cycle. Celery provides a production-grade task queue.
- **Robust Message Broker**: Redis acts as an in-memory message broker with sub-millisecond latencies, facilitating instant task delivery and status retrieval.
- **Fault-Tolerance & Retries**: Celery supports automatic retries with back-off delays, ensuring transient errors (like DB locks) do not cause data loss.

## 7. Why Docker & Docker Compose?
- **Environment Isolation**: Bundles complex Python dependencies (PyTorch, OpenCV, CUDA/C++ libraries) and system tools into clean container environments.
- **Single Command Orchestration**: Allows developers, QA testers, and interviewers to spin up PostgreSQL, Redis, backend API, Celery worker, and React frontend with a single command: `docker-compose up --build`.
