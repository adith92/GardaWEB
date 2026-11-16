# GARDA AI Core stage-1 architecture

CCTV RTSP video -> capture thread (latest-frame queue size=1) -> per-camera processor -> OpenCV MOG2 / face detection / FastALPR OCR -> SQLite WAL -> JPEG evidence. A separate FastAPI HTTP process provides **authenticated** event search and photos on loopback only. Data is never uploaded to GitHub or a third-party cloud.

## Face semantics

A **new face** means a new *appearance within one camera scene*, detected with bounding-box overlap tracking. This is intentionally **not face recognition or a biometric identity database**. One sighting produces up to 3 scene frames and up to 3 face crops (if the face stays visible for the sample intervals), at 0.00/0.55/1.10+ sec. Faces disappearing for more than 4 seconds may count as new sightings if they return. Camera movement and changes in face pose can break tracking. Full identity enrollment/recognition, encryption of embeddings, watchlist permissions and formal accuracy testing require a separate phase.

## Plate semantics

FastALPR v0.4.0 combines an ONNX plate detector with OCR. An observed plate is only saved after **two matching OCR reads in a 7-second window**, confidence threshold >= 0.70. Same plate on same camera is deduplicated for 60 seconds; a later sighting is logged again. That is a consensus heuristic, not an identification guarantee. Low-light / dirty / angled plates and Indonesian format should be evaluated with a labeled local dataset before production.

## Motion semantics

MOG2 background subtraction on <=640px frames, 18 warmup frames, threshold >=1.6% foreground. Motion events have 15-second cooldown. Camera PTZ movement, rain, lights and sun/shadow can cause false positives. ROIs and camera-tamper logic will follow.

## API and database

- SQLite database `var/garda.db` in WAL mode, indexed for date + kind + camera + plate; photos stored under `var/evidence/<date>/<camera>`, **not in SQLite blobs**.
- Default retention 90 days. Scheduler performs deletion at startup + every 24 hours while running; `python -m garda_ai purge` removes older events and JPEGs. Database/WAL and media directories need disk encryption, restricted access and backup handling before real use.
- `GET /health` public minimal health, `GET /api/events`, `/api/stats`, `/api/events/{id}/photos`, and `/api/events/{id}/photos/{photo_id}` guarded by `X-GARDA-KEY` constant-time comparison. Bind only to `127.0.0.1`; use HTTPS/VPN proxy if exposed to mobile.
- Access reads are audited, but production RBAC/MFA and complete audit for edits/deletions aren't implemented.
- No person names, face embeddings or cross-day biometric identity inference in stage 1.

## Scale to KAK target

Stage 1 is explicitly capped at 2 streams. For 16 sites, switch to a centralized RTSP ingestion gateway (GStreamer/FFmpeg), GPU inference worker pool, PostgreSQL time-indexed metadata, MinIO/NAS object retention, per-role access control and queue-backed event processing. Do not multiply full-resolution decoder/ONNX model instances per camera.

## Model license considerations

- OpenCV 4.5+ code: Apache-2.0; YuNet face detector: MIT (retain notices).
- `fast-alpr` code: MIT (verify transitive model weights/licenses independently before procurement/commercial use). The package auto-downloads model weights on first run and therefore requires initial internet access or an offline model cache strategy.
- Ultralytics is **not** a runtime dependency in this stage due to AGPL-3.0 / commercial license requirements, even though Context7 verified its APIs. Switching to an Ultralytics inference pipeline needs license review.
- User's GitHub starred collection could not be fetched through available GitHub connector endpoint; no claim of having verified which projects they starred.
