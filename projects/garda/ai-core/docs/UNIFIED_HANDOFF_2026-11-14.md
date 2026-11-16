# GARDA Unified Source Handoff — Windows first, Linux next, Android clients
Revision: 2026-11-14 | Status: development/audit candidate, NOT hardware certified.

## Canonical source
- Python AI: projects/garda/ai-core/garda_ai (existing FastALPR plate OCR, motion, face sightings and JPEG screenshots, plus new consent-based SFace recognition and zoom probe).
- Windows/Linux PySide6 operator: projects/garda/desktop (existing RTSP/PTZ view plus new AI Events/Photo tab).
- Android native: projects/foldview-cctv/android (existing Gradle FOLD + Standard flavors, plus new GardaAiClient.kt, GardaAiPanel.kt and Settings integration).
- Existing independent Android source: projects/garda/mobile/android (unchanged).
- Experimental FH8852V201 firmware: projects/cctv-firmware/fh8852v201-onvif (motor firmware PTZ not verified).
- ClearCam upstream roryclear/clearcam (GPL-3.0) reviewed for architecture; NO upstream ClearCam code copied or statically integrated.

## Pipeline
1. RTSP input from authorized local camera, 1-2 streams. Credentials only through process environment.
2. OpenCV FFmpeg capture, queue of latest frame only, reconnect, bounded sampling.
3. OpenCV MOG2 motion; YuNet optional (Haar fallback) face detection; FastALPR ONNX OCR with two-read 7s consensus and 60s dedup.
4. FaceSession: new scene appearance, up to 3 independent scene/face screenshot pairs. Scene presence is NOT evidence of biological identity.
5. Optional identity matching: OpenCV YuNet landmarks + SFace ONNX embeddings; compare against local consent-enrolled templates encrypted with Fernet. Unknown faces stay unlabeled.
6. SQLite WAL metadata (plate, label, timestamps, camera, confidence), private JPEG evidence, 90-day default expiry.
7. Key-protected FastAPI (loopback 127.0.0.1 only) exposes event/photos/statistics; PySide6 and Kotlin clients fetch asynchronously.
8. ONVIF Optical Zoom is manual-only CLI; must pass capability GetConfigurationOptions and PTZConfiguration check. Brief bounded ContinuousMove plus Stop, but SOAP response does not prove motor movement.

## Windows 11 first-run
- Prerequisites: verified Python 3.11 64-bit and FFmpeg accessible in PATH. Use PowerShell from projects/garda/ai-core.
- Step 1: .\scripts\INSTALL-WINDOWS.ps1 (creates virtual environment, installs CPU requirements).
- Step 2: set GARDA_CAMERA_PTZ_RTSP and GARDA_CAMERA_WIDE_RTSP to actual local RTSP URLs in process environment; do not commit passwords to .env or git.
- Step 3: set GARDA_AI_API_KEY to a cryptographically random secret length >=24; copy config.example.json to config.json as performed by install script.
- Step 4: .\scripts\START-WINDOWS.ps1 launches workers plus loopback API port 8808. Test local API GET /api/stats using X-GARDA-KEY header.
- Step 5: from projects/garda/desktop, install PySide6 dependencies, run python app.py. AI Events tab uses local GARDA_AI_URL and GARDA_AI_API_KEY.
- Step 6: Android FOLD/Standard Settings > GARDA AI: input a trusted HTTPS endpoint and API key; client rejects off-device plain HTTP. Use Tailscale with secure TLS reverse proxy, do not expose local AI to public Internet.
- Step 7 optional: pip install -r requirements-ptz.txt, set GARDA_ONVIF_USER/GARDA_ONVIF_PASS, run .\scripts\ZOOM-WINDOWS.ps1 -CameraIp <private camera IP> -Action check, then explicit bounded in/out if supported.

## Consent-based face enrollment
- Set GARDA_FACE_YUNET_MODEL and GARDA_FACE_SFACE_MODEL pointing to official audited ONNX model files (not packaged; verify license and SHA256).
- Run python -m garda_ai face-keygen and save GARDA_FACE_KEY securely in runtime secret store. Losing this key makes enrolled templates unreadable.
- Enroll with python -m garda_ai enroll --config config.json --name "Person label" --image "consented_image.jpg" --consent-ref "policy-or-consent-ticket".
- Each enrollment requires EXACTLY one clear face. Models are absent by default so recognition is disabled until configured. Revoke with python -m garda_ai revoke --face-id ID.
- Identity results are probabilistic, not proof of real-world identity. Threshold default 0.55 must be validated on site camera images. Consent logs and personal data governance are mandatory.

## Security/privacy and limitations
- Recognition templates encrypted in SQLite using Fernet with separate GARDA_FACE_KEY. User labels and consent references are non-encrypted, so filesystem BitLocker/ACLs are still required.
- The operator enrolls from local CLI only; no public enrollment/write API. Revocation does not retroactively delete historical events; review retention/privacy policy.
- Windows API binds loopback only, shared API key is checked in constant time. Production remote access needs HTTPS/TLS gateway, RBAC, authorization audit and key rotation; no camera passwords in GitHub or Android event API.
- FastALPR=0.4.0 is verified on PyPI, model weights auto-download on first use, so air-gapped operation needs a verified offline model cache.
- onvif-zeep=0.2.12 is from 2018 and is unproven on this user's firmware and modern Python. Zoom may fail or be digital-only; must check profile and physical output.
- ClearCam GPL-3.0 source is NOT embedded. Current production-grade performance, security, Windows runtime, Android Fold7 UI, native PTZ motor and OCR accuracy are NOT verified until real tests pass.
- This code does not implement automatic camera movement based on face/plate detection, public Internet camera access, 16 concurrent streams, Postgres, GPU pooling or a full commercial release signing pipeline.
- Existing Android debug APK signing certificates may vary by build; source is supplied for audit, not a new production APK.

## Audit checklist for next model
P0: Verify install on Windows 11 with Python 3.11 64bit; inspect dependency tree and transitive model-weight provenance.
P0: Run Python unit tests and Android unit+compile tests both flavors in CI; check all Kotlin Compose imports.
P0: Field-test camera zoom/PTZ profile with physical motor hardware; do not rely on HTTP 200.
P0: Validate API ingress auth, TLS proxy, camera credentials, keys, encrypted-template loss and evidence paths.
P1: Benchmark RTX 3080 Ti vs CPU and Linux NVIDIA providers; measure VRAM/FPS/inference latency with 1 vs 2 RTSP streams.
P1: Audit false matches, low light faces, Indonesian plates, OCR confidence, consent/retention/privacy controls.
P1: Add clip storage, event annotation, operator review workflow, Windows background service and improved model downloader.
P2: Scale to GPU inference pool, PostgreSQL, NAS, RBAC, signed backups for multiple sites.

Reference documentation:
- https://fastapi.tiangolo.com/advanced/events/
- https://docs.opencv.org/4.13.0/d0/dd4/tutorial_dnn_face.html
- https://onnxruntime.ai/docs/execution-providers/
- https://pypi.org/project/fast-alpr/
- https://pypi.org/project/onvif-zeep/
- https://github.com/roryclear/clearcam/blob/main/LICENSE.md
