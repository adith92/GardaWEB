# GARDA AI Vision LAB (Windows-first / Linux-ready)

Experimental, on-premises API: RTSP frame reading, optional OCR plate candidates, face presence, optional licensed ONNX face identity, operator-only ONVIF zoom, ClearCam multipart notifications and encrypted metadata. **NOT** production deployment, legal authorization, model accuracy certification, or KAK acceptance.

## Run on Windows 11 (PowerShell)

```powershell
cd services/garda-ai-vision
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install easyocr onvif-zeep
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Define these in your protected shell or local secret manager; do NOT paste real values into Git.
$env:GARDA_DATA_KEY = '<generated-key>'
$env:GARDA_VIEWER_TOKEN = '<random-at-least-24-chars>'
$env:GARDA_OPERATOR_TOKEN = '<different-random-at-least-24-chars>'
$env:GARDA_ADMIN_TOKEN = '<third-random-at-least-24-chars>'
$env:GARDA_CLEARCAM_TOKEN = '<fourth-random-at-least-24-chars>'
$env:GARDA_CAM01_RTSP = '<camera-rtsp-url>'
python -m garda_vision.api
```

Use `http://127.0.0.1:8765/docs` for the local OpenAPI docs. Default API is loopback-only. Windows Firewall must not expose this service to the Internet. Run web demo with `VITE_GARDA_AI_LAB=true npm run dev` (PowerShell `$env:VITE_GARDA_AI_LAB='true'; npm run dev`). In browser, enter the **operator/admin test token only on trusted localhost**, not public Vercel. `http://127.0.0.1:5173/ai-vision` is the optional React lab page.

## Recognition status
- **Plate recognition**: `easyocr` is optional. With `GARDA_PLATE_ONNX` pointing to an independently licensed **single-class YOLOv8 ONNX** plate detector, text spotting runs on proposed plate ROIs; without weights it falls back to whole-frame text spotting. Neither mode is accuracy-validated. For reliable ANPR, add licensed plate ROI detection/tracking, high-resolution snapshots and calibrated tests.
- **Face presence**: OpenCV Haar cascade. This is NOT identification.
- **Face ID**: disabled by default. To enable in an authorized PUSADA contract lab, set `GARDA_CONTRACT_BUNDLE=pusada`, `GARDA_FACE_ID_ENABLED=1` and `GARDA_FACE_ONNX` to a separately licensed, validated ArcFace-style ONNX model file. This template assumes 112x112 RGB preprocessing and MUST be tested against that model. Enroll only with a documented legal authority reference; system does not independently verify that authority. Threshold 0.60 is illustrative, not validated. No reference photos/weights are bundled.
- **ClearCam**: DO NOT import/copy its GPL-3.0 server into GARDA proprietary code. Configure ClearCam's custom notification URL to a separate local trusted relay that adds `Authorization: Bearer ...`, then forwards its multipart fields to `/api/v1/clearcam/notification?camera=LAB-CAM-01`. A tiny relay example is in `clearcam_relay.py`; the original ClearCam sample sends multipart fields `text`, `body_text`, and `img`, no bearer header. This prototype discards the image.
- **PTZ optical zoom**: optional `onvif-zeep` package, compatible camera, user/password via environment; speed -1 to +1 and 0.05..2s; command automatically sends Stop. Operator authorization and audit; requires a camera capability test.

## Linux migration
Same Python runtime, camera environment variables and API. Use isolated systemd/Docker deployment with GPU acceleration **only after** throughput tests. Do not run multiple uvicorn workers against one SQLite or RTSP engine without redesign; migrate to PostgreSQL and supervised per-camera workers first. External NVR/video gateway must record independently; these files do NOT implement 90-day DVR redundancy.

## Tests
`python -m pytest -q tests` after `pip install pytest httpx`.

## Security and release gates
- Keep `.env`, database, real RTSP URLs, network drawings, faces, license plates, camera firmware and ONNX models out of Git. Fernet key loss makes event/template data unrecoverable.
- Development tokens are static and role-only; production requires named accounts, MFA, short-lived scoped credentials, device enrollment, TLS, per-site RBAC, encryption-key rotation, access logging, backup and tamper-evident audit export.
- Do not use face/plate scores for automatic adverse decisions; require authorized human review. Viewers get redacted event details.
- Data retention defaults are **not automatically enforced**; wire approved policy + scheduled prune and backup. KAK video and metadata retention 90d, redundant enterprise hardware and 16-site acceptance remain open.
- License compliance: ClearCam is GPL-3.0 and its README excludes Windows; keep it as separate process and obtain licensing counsel review before combining/distributing. Separation by HTTP is not itself a guaranteed legal exemption.

## Handoff
Audit TODO: robust plate localization (ONNX inference provider), face alignment+anti-spoof, quality metrics and validated thresholds, PTZ presets/pan/tilt with per-device tests, audit tamper resistance, event/outbox delivery and offline mobile device enrollment, GDPR/UU PDP basis, 90-day retention enforcement and evidence manifest checksum, model provenance and licenses, NVR failover, load tests for 16 concurrent channels. See `docs/GARDA_AI_VISION_AUDIT_HANDOFF_2026-11-14.md`.

## Fetch upstream ClearCam separately
From the source bundle root, `powershell -ExecutionPolicy Bypass -File scripts/fetch_clearcam.ps1` on Windows, or `sh scripts/fetch_clearcam.sh` on Linux. This only checks out the GPL-3.0 source at a reviewed commit, and **does not** assert original ClearCam can execute on Windows. Keep vendor checkout separate from proprietary GARDA.
