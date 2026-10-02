# PROJECT GARDA — Conversation Log

Date: 2026-10-02

This is a structured turn-by-turn preservation of the CCTV / ONVIF / AI-server discussion. The companion file `GARDA_CCTV_AI_MASTER_CONTEXT.md` is the canonical distilled context.

## 1. Camera search goal

User requested a marketplace search for a CCTV camera with:

- dual lens
- PoE without an extra adapter at the camera
- price below Rp1,000,000

Discussion established that true PoE must be verified as IEEE 802.3af/802.3at rather than trusting marketplace wording.

## 2. PROVIEW SM-PR5260-PT

User showed a Shopee listing for PROVIEW SM-PR5260-PT and asked whether remote access, ONVIF, audio, and PTZ could be controlled by custom software.

Discussion outcome:

- ONVIF/RTSP can potentially expose live video, PTZ, media profiles, audio, and events.
- Two-way talk depends on audio backchannel/vendor implementation.
- Dual-lens cameras may expose two independent media profiles, or may expose only one combined stream.
- Vendor-specific functions may require proprietary APIs.

User then asked to verify IEEE 802.3af.

Finding:

- official documentation checked in the discussion listed DC 12V
- IEEE 802.3af/at was not explicitly documented
- marketplace "PoE/AC" text was therefore not accepted as proof of standards-based PoE

## 3. ONVIF capabilities

User asked what becomes possible on a custom server when a camera supports ONVIF.

Discussed capabilities included:

- camera discovery
- stream/profile enumeration
- live viewing
- multi-camera dashboard
- snapshots
- recording
- PTZ and presets when supported
- microphone audio
- two-way audio when backchannel is exposed
- events/motion metadata
- server-side AI independent of camera AI

ONVIF Profiles S/T/G/M were discussed at a high level.

## 4. ONVIF vs RTSP

User asked about protocols besides ONVIF, including RTSP, and whether it is better to search only for ONVIF cameras.

Discussion outcome:

- ONVIF and RTSP are complementary.
- RTSP primarily carries live video/audio.
- ONVIF handles discovery, capabilities, media profiles, PTZ, events, etc.
- Best target for GARDA is camera support for **ONVIF + RTSP + true IEEE 802.3af/at PoE**.
- Dual lens does not guarantee PoE.

## 5. EZVIZ C6N

User showed an EZVIZ C6N 2MP listing and asked whether it can connect directly to a PC or NVR.

Discussion outcome:

- unit shown has RJ45 plus separate USB/DC power
- Ethernet does not mean PoE
- it can be used over LAN with a PC/server
- NVR interoperability depends on exact model/firmware and ONVIF support
- exact C6N hardware revision matters

## 6. Learning project: face + plate detector

User asked whether EZVIZ could be used to build a custom CCTV application for learning that detects faces and license plates.

Answer: yes.

Proposed pipeline:

EZVIZ -> RTSP -> GARDA server -> AI pipeline -> events/database/dashboard.

Suggested technologies:

- Python/FastAPI
- OpenCV
- FFmpeg
- YOLO
- InsightFace
- PaddleOCR or similar
- PostgreSQL

Important distinction discussed:

- face detection != face recognition
- plate detection != plate OCR/ANPR

## 7. Open-source macOS ONVIF tools from GitHub

User asked for good open-source ONVIF software for macOS and explicitly requested GitHub research.

Projects examined:

### OpenIPC/viewer

Recommended as the immediate GUI test tool.

Relevant features found:

- macOS build
- ONVIF discovery
- RTSP live view
- H.264/H.265
- PTZ/presets
- recording
- local object detection
- audio
- RTSP backchannel push-to-talk where supported

### AlexxIT/go2rtc

Recommended as a strong candidate for GARDA's future streaming layer.

Relevant features:

- ONVIF
- RTSP
- WebRTC
- HTTP/WebSocket API
- multiple streaming formats
- two-way audio support for multiple camera ecosystems
- cross-platform binaries

### dicroce/revere

Considered an interesting open-source NVR/reference architecture with ONVIF, recording, playback, motion detection, Web UI/API, and YOLOv8 object detection.

### steelbrain/LemurCam

macOS utility that turns ONVIF/RTSP IP cameras into a virtual Mac camera/microphone. Useful but not intended as GARDA's core NVR.

## 8. GARDA server OS decision

User asked whether Windows or Linux is better for the server.

Recommended direction:

- Linux for 24/7 GARDA server
- Ubuntu Server LTS as initial bare-metal recommendation
- Mac as development/control workstation

Reasons discussed:

- headless operation
- Docker ecosystem
- FFmpeg/media tooling
- NVIDIA/CUDA support
- service automation
- lower GUI overhead
- easier server/storage administration

## 9. Proposed GARDA server stack

- Linux / Ubuntu Server LTS
- go2rtc
- FFmpeg
- Python + FastAPI
- YOLO
- InsightFace
- PaddleOCR
- OpenCV
- PostgreSQL
- React / Next.js
- Docker Compose
- Tailscale or WireGuard for remote access
- NVIDIA CUDA GPU(s)

Storage concept:

- NVMe for OS/application/database/cache
- HDD pool for video recordings

## 10. AI efficiency strategy

Avoid sending every full-resolution frame to AI.

Preferred approach:

- main stream: recording and high-quality evidence
- substream: lower-resolution 5-10 FPS analytics
- detection on substream triggers higher-quality snapshot/recognition from main stream

## 11. Recording principle

Original camera stream should be recorded independently of AI processing.

Camera -> RTSP -> streaming layer ->

- recorder/storage
- AI pipeline

This keeps original footage available even if AI fails.

## 12. Network/security direction

Future design discussed:

- dedicated CCTV VLAN
- separate IoT/user networks
- camera communication limited primarily to GARDA server
- avoid exposing RTSP/ONVIF directly to the internet
- use VPN such as Tailscale/WireGuard for remote management/access

## 13. Development phases

1. One EZVIZ/IP camera -> RTSP -> go2rtc -> web live view.
2. ONVIF discovery, PTZ, audio, recording/playback.
3. Person/vehicle detection.
4. Face detection/recognition.
5. License-plate detection/OCR.
6. Multi-camera UI, RBAC, notifications, remote access.
7. Advanced PTZ tracking, system health, storage health, event/video search.

## 14. Current follow-up

User has accepted Linux as the primary direction and now wants to understand how Windows access fits into the same physical server.

Next architecture question:

- Linux bare metal + Windows VM via KVM/QEMU/libvirt, or
- Proxmox VE (Linux/Debian-based hypervisor) as the physical host, with separate Ubuntu GARDA and Windows VM guests.

The virtualization decision should consider GPU allocation because the same consumer GPU generally cannot simply be dedicated simultaneously to Linux AI workloads and passed through exclusively to a Windows VM.
