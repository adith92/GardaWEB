# GARDA AI Core v0.1.0 (Server, Stage 1)

## Unified development source v0.2.0 (2026-11-14)

Windows 11/PC-first with Linux-compatible Python code and native Android viewer integration. [Full handoff and audit checklist](docs/UNIFIED_HANDOFF_2026-11-14.md).

- **Plate recognition:** existing FastALPR 0.4.0 license-plate detection + OCR, two-read agreement, SQLite plate events, evidence photos. Requires live lens-level accuracy audit.
- **Face recognition:** opt-in official OpenCV Zoo YuNet + SFace ONNX. The face gallery encrypts embeddings with a Fernet key supplied by GARDA_FACE_KEY; enroll requires a local reference image and consent reference. No automatic identity naming for an unknown person.
- **Face screenshots:** existing scene appearance tracker saves up to three original frames and three face crops if detections persist. Separate scene sightings may re-identify same person as a new sighting.
- **Manual zoom:** onvif-zeep optical zoom CLI (optional dependency); verifies ONVIF PTZ profile and ContinuousZoomVelocitySpace before a short bounded zoom pulse. Motor functionality is unverified.
- **Desktop:** existing PySide6 GARDA app gains AI Events tab (stats, plate history, recognized labels, evidence JPEG) via a background worker and private API key.
- **Android:** existing Fold/Standard shared Compose app gains Settings > GARDA AI, with encrypted server key, authenticated event filtering and evidence thumbnails. HTTPS required from the phone; loopback HTTP on the same machine only.
- **Setup:** PowerShell scripts INSTALL-WINDOWS.ps1 and START-WINDOWS.ps1 in scripts/. Linux equivalent scripts/install-linux.sh and scripts/start-linux.sh; config.example.json must be copied to ignored config.json.
- **Source archive:** GitHub Actions packages the existing desktop, Android, AI Core, and supporting firmware reference into a ZIP for Google Drive; no binaries, biometric data, API keys or camera passwords included.

To enroll a consented subject (after local model files and env variables are configured):

    python -m garda_ai face-keygen
    python -m garda_ai enroll --config config.json --name "Visitor with consent" --image C:\path\consented.jpg --consent-ref "consent-ticket-123"

Never commit GARDA_FACE_KEY. The key is critical for decrypting stored templates. Use Windows BitLocker and a secure key store. To revoke: python -m garda_ai revoke --face-id THE_ID. Results are probabilistic; audit confidence and camera lighting before operational use.

**Runnable development baseline** for native RTSP/ONVIF cameras and the GARDA CCTV FOLD project. The server handles on-prem AI and storage. **This is not an Android APK, not a firmware image and not production-certified.** It does not modify camera firmware or the existing Android app.

## What works

- Motion detection (OpenCV MOG2) with initial warm-up, sensitivity threshold and 15s cooldown.
- Face **detection**, new face *sighting* tracking within a video scene, with **up to 3 scene screenshots + 3 face crops** as long as the face remains visible. No biometric identity matching.
- License plate detector + OCR (FastALPR/ONNX), conservative 2-read consensus, dedup and timestamped searchable plate history.
- Local evidence storage, SQLite WAL, default 90-day purge, LAN source reconnect, bounded latest-frame queue and slow inference off any client UI.
- Authenticated FastAPI event catalog for future Desktop and Fold Android integration. No credentials in source or API.

## Install (Windows 11, Ubuntu; Python 3.11-3.13)

```bash
cd projects/garda/ai-core
python -m venv .venv
# PowerShell: .venv\\Scripts\\Activate.ps1
# Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
cp config.example.json config.json
```

Edit `config.json` to select 1-2 streams; **do not commit it**. Supply the URLs as process environment variables rather than embedding passwords in files:

```powershell
$env:GARDA_CAMERA_PTZ_RTSP="rtsp://192.168.18.249:1234/"
$env:GARDA_CAMERA_WIDE_RTSP="rtsp://192.168.18.249:1235/"
$env:GARDA_AI_DATA_DIR="C:\\GardaPrivateData"
python -m garda_ai check --config config.json
python -m garda_ai run --config config.json
```

For better face detection, download the official OpenCV Zoo YuNet ONNX weight under an audited local model directory and set `GARDA_FACE_YUNET_MODEL` to its path. Without it, the default detector uses an OpenCV Haar cascade (basic quality). The FastALPR models can download on first use; ensure correct licenses and model provenance and cache them offline for secure deployment. CPU install as above; for a CUDA-configured GPU, use `fast-alpr[onnx-gpu]` **instead of** `fast-alpr[onnx]` and validate matching ONNX Runtime, CUDA and cuDNN versions first.

### Local REST API for event browser

In a second terminal, set the same `GARDA_AI_DATA_DIR` plus a strong random API key (at least 24 characters):

```powershell
$env:GARDA_AI_DATA_DIR="C:\\GardaPrivateData"
$env:GARDA_AI_API_KEY="REPLACE_WITH_GENERATED_RANDOM_32_PLUS_CHARS"
python -m garda_ai api --listen 127.0.0.1 --port 8808
curl.exe -H "X-GARDA-KEY: YOUR_SECRET" "http://127.0.0.1:8808/api/events?kind=plate&limit=20"
```

The API deliberately binds to loopback only. To access from Galaxy Z Fold, add **Tailscale/VPN + authenticated TLS reverse proxy** in stage 2. Do not simply bind the private event API to `0.0.0.0` on a camera LAN.

## Verify tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests run with injected fake detectors and synthetic frames; **they do not prove camera capture/optical accuracy**. Check live on `FH8852V201`, and evaluate face/LPR false detections, PTZ motion artifacts, disk use, and GDPR/Indonesia PDP/organization privacy and storage requirements before rollout.

## Next stages

1. **Stage 1 now:** database, basic face sightings/3 captures, motion, plate OCR and searchable local API.
2. **Stage 2:** integrate event timeline/search/snapshot into GARDA Desktop and GARDA CCTV FOLD edition APK; HTTPS auth and read permissions.
3. **Stage 3:** improve faces using YuNet, Indonesian LPR data, polygons/ROI, event rules, alert notifications, benchmarking.
4. **Stage 4:** 16 points, pooled inference GPU, PostgreSQL, NAS/RAID, signed backups, encrypted biometrics only if separately authorized and governance is approved.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for operational/security details.
