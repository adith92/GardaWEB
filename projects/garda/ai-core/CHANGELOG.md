# GARDA AI Core changelog

## v0.2.0 — 2026-11-14 (Windows/Android unified source, for audit)
- Optional consent-based YuNet+SFace identity matching; encrypted gallery in SQLite with Fernet runtime secret, enrollment/revocation CLI, recognition output in face events.
- Windows PowerShell launch/install scripts and Linux shell analog; optional onvif-zeep optical zoom probe/manual pulse with Stop and no motor success claim.
- Desktop PySide6 timeline tab for authenticated plate/face/motion events and evidence screenshots; Android FOLD/Standard Settings GARDA AI panel (encrypted credentials and HTTPS).
- New synthetic biometric/zoom tests, Windows/Linux CI and source archive; model weights, camera credentials, biometric snapshots not committed.
- Related: docs/UNIFIED_HANDOFF_2026-11-14.md, prior ClearCam review (GPL-3.0 source NOT incorporated).
- Outstanding: actual CCTV, Windows installation, optical zoom, Face SFace matching/ANPR performance tests and Windows/Linux GPU benchmarking.

## v0.1.0 | 2026-11-10

- Independent server-side MVP; Android Fold and GARDA Desktop source unchanged.
- Real RTSP ingestion, latest-frame queue for low-latency motion and image analytics.
- OpenCV MOG2 motion events with cooldown and JPEG proof.
- OpenCV face detection, per-camera scene-local position tracking and up to 3 screenshot + crop pairs per new face sighting (NOT biometric person recognition).
- fast-alpr 0.4.0 (MIT Python wrapper) plate detector/OCR with two-read temporal consensus, 60-second per-plate dedup, confidence and JPEG proof.
- Local SQLite WAL event schema and private, indexed media storage; automatic 90-day retention purge.
- Authenticated FastAPI event, evidence and statistics endpoints on loopback, basic audit of API reads.
- Code and 11 locally executed unit/integration tests using synthetic frames and fake AI predictors; live-camera model accuracy not yet validated.
- Explicit two-camera stage-1 limit, later GPU inference pool/PostgreSQL scaling plan; no full 16-site guarantee.
- Optional YuNet weights for improved facial detection, not bundled; initial FastALPR model download/cache needed.
