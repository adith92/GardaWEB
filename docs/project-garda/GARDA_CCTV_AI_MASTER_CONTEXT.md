# PROJECT GARDA — CCTV AI / ONVIF / NVR MASTER CONTEXT

_Last updated: 2026-11-03_

## Purpose

This document preserves the working context from the ChatGPT discussion about building **Project GARDA**, a self-hosted CCTV / NVR / video-intelligence system that can ingest consumer and ONVIF IP cameras, record locally, control compatible PTZ/audio features, and later add AI for person, face, vehicle, and Indonesian license-plate detection.

This file is intended as the continuity source for future ChatGPT/Codex sessions.

---

## 1. Project direction

User wants to build a custom CCTV system for learning first, then expand it into a serious self-hosted surveillance/video-intelligence platform.

Core goals:

- Support IP cameras from multiple vendors rather than lock into one cloud app.
- Prefer open standards and local access.
- Use **ONVIF + RTSP** as the main interoperability layer.
- Run a local NVR/server 24/7.
- Record video to local storage/HDD pool.
- Add server-side AI rather than depend entirely on camera AI.
- Later support face recognition and license-plate recognition for authorized/private use.
- Provide web/mobile access to live streams, recordings, search, and events.
- Support PTZ and two-way audio when the camera exposes compatible interfaces.

Project name to use going forward: **GARDA**.

---

## 2. Camera requirements discussed

The desired camera characteristics are:

### Mandatory / preferred

- ONVIF support.
- RTSP support.
- H.264 and preferably H.265.
- Native Ethernet.
- For permanent installations: **true IEEE 802.3af / 802.3at PoE**.
- PTZ via ONVIF when the camera is motorized.
- Microphone/audio stream.
- Speaker/audio backchannel for two-way talk where available.
- ONVIF events if available.
- Outdoor cameras should be IP66/IP67 when needed.

### Dual-lens note

**Dual lens does NOT imply PoE.**

Dual-lens cameras can be Wi-Fi + DC powered, Ethernet + DC powered, passive-PoE, or true IEEE 802.3af/at PoE.

For dual-lens cameras, it is desirable that each lens is exposed as a separate ONVIF media profile / RTSP stream. Some cheap cameras expose only a combined picture, so this must be tested.

---

## 3. PROVIEW SM-PR5260-PT findings

A Shopee listing was examined for:

- PROVIEW SM-PR5260-PT
- Dual lens
- PTZ
- Two-way talk
- Claimed PoE/AC in marketplace listing

Important finding:

- Official product documentation checked during the discussion listed **DC 12V** power.
- The official datasheet did **not** explicitly list **IEEE 802.3af** or **802.3at**.
- Therefore the marketplace "PoE" wording must not be assumed to mean native standards-based PoE.

Decision:

- Do **not** treat this camera as verified true-PoE until the exact hardware variant is confirmed by the seller/manufacturer.
- A seller should explicitly confirm: camera powers directly from a standard 48V IEEE 802.3af/at PoE switch/NVR with no DC adapter or external splitter.

---

## 4. EZVIZ C6N discussion

EZVIZ C6N was considered as a low-cost learning camera.

Observed hardware from listing/image:

- RJ45 Ethernet port.
- Separate micro-USB / 5V power.
- Therefore this model is **not powered over Ethernet** just because it has RJ45.

Possible usage:

- Camera -> LAN/router/switch -> PC/server.
- Camera -> compatible NVR, depending on exact model/firmware and ONVIF support.
- Camera can be useful for learning RTSP streaming, local video processing, and potentially ONVIF functions.

Important rule:

- Exact C6N model/firmware matters. Do not assume every product called "C6N" exposes the same ONVIF features.

For initial GARDA learning, C6N is considered acceptable as a cheap stream source even though it is not PoE.

---

## 5. ONVIF vs RTSP

They solve different parts of the system.

### RTSP

Primary role:

- Live video transport.
- Usually audio transport too.
- Feed for recorder and AI pipeline.

### ONVIF

Primary roles may include:

- LAN device discovery.
- Camera information/capabilities.
- Media profiles / stream URI discovery.
- PTZ commands.
- Presets.
- Events.
- Some audio features.
- Configuration depending on supported profile and vendor implementation.

### Important limitation

"Supports ONVIF" does **not** mean every vendor-specific feature is available.

Potentially proprietary features include:

- Siren.
- White-light controls.
- Vendor-specific AI.
- SD-card playback.
- Auto tracking.
- Two-way audio on cameras that do not expose a standard backchannel.

Therefore GARDA should use standards when available and allow vendor-specific adapters only when justified.

---

## 6. ONVIF profiles relevant to GARDA

### Profile S

Commonly used for IP video streaming/discovery and basic interoperability.

### Profile T

Preferred for modern cameras when available. Relevant for:

- H.264/H.265.
- Metadata/events.
- Modern media handling.
- Bidirectional audio/backchannel support where implemented.

### Profile G

Useful for recording/search/playback stored on the camera (for example microSD). Less important if GARDA records everything on its own server.

### Profile M

Relevant to analytics metadata/events.

---

## 7. What GARDA should do server-side

Even a basic RTSP camera can become much smarter when analytics happen on the server.

Planned capabilities:

- Live multi-camera viewer.
- Continuous recording.
- Motion/event recording.
- Timeline playback.
- Snapshots.
- Clip export.
- Camera health monitoring.
- User accounts / RBAC.
- Audit logs.
- PTZ control.
- PTZ presets/patrol.
- Audio listen.
- Push-to-talk where supported.
- Person detection.
- Vehicle detection.
- Face detection.
- Face recognition for enrolled/authorized subjects.
- License-plate detection.
- Plate OCR / ANPR.
- Zone intrusion.
- Loitering detection.
- People counting.
- Vehicle entry/exit events.
- Notifications.
- Search by time/event/person/vehicle/plate.

Example future searches:

- Find all appearances of plate `B 1234 XYZ` between two dates.
- Show unknown people seen between 00:00 and 06:00.
- Jump directly from an event to the relevant recording timestamp.

---

## 8. AI pipeline plan

### General object pipeline

Camera substream -> decode -> object detection -> event -> high-quality snapshot/clip from main stream.

### Face pipeline

Person -> face detector -> face alignment -> embedding -> similarity/vector lookup -> Known / Unknown.

Recommended concept:

- Store biometric embeddings and metadata with strict access control.
- Avoid unnecessary retention of raw face imagery.

### Plate pipeline

Vehicle detection -> license-plate detection -> plate crop -> perspective/quality correction -> OCR -> normalized plate text -> event/database.

Potential software stack discussed:

- YOLO for object/person/vehicle/plate detection.
- InsightFace for face embeddings/recognition.
- PaddleOCR or similar for OCR.
- OpenCV for image processing.

---

## 9. Recording architecture

Key design decision:

**Record the original camera stream separately from the AI pipeline.**

Concept:

Camera -> RTSP -> streaming layer

From there:

- path A -> recorder/storage
- path B -> AI processing

This ensures AI errors or downtime do not corrupt the original evidence stream.

Suggested recording scheme:

- Segment recordings into manageable files, e.g. 5-minute segments.
- Database stores recording index and event offsets.
- Video files remain in filesystem/storage pool, not inside the SQL database.

Example:

- `cam01_20261002_203000.mp4`
- `cam01_20261002_203500.mp4`

Event record can point to the relevant file and timestamp offset.

---

## 10. Main stream vs substream strategy

Do not run full AI inference on every full-resolution frame from every camera.

Preferred strategy:

### Main stream

- Higher resolution/bitrate.
- Used for recording.
- Used for high-quality event snapshots/clips.

### Substream

- Lower resolution.
- Lower FPS, e.g. around 5-10 FPS depending on need.
- Used for continuous AI detection.

When an event is detected on the substream, GARDA can fetch/use the main stream for higher-quality recognition or evidence.

This is especially important when scaling to many cameras.

---

## 11. Recommended GARDA server OS

Decision from discussion:

**Use Linux for the 24/7 server.**

Preferred initial OS:

- Ubuntu Server LTS.

Reasons discussed:

- Better fit for headless 24/7 service.
- Good Docker support.
- Good NVIDIA/CUDA support.
- Strong FFmpeg / media tooling.
- Easier automation and service management.
- Lower GUI overhead.
- Good storage/server ecosystem.

Mac remains suitable as the development/control workstation.

Windows can still be used for client/admin workloads or special software, but is not the preferred GARDA host OS.

---

## 12. Recommended GARDA software stack

### Host OS

- Ubuntu Server LTS.

### Camera streaming / protocol gateway

- **go2rtc**.

Roles:

- RTSP ingest.
- ONVIF-assisted stream discovery where appropriate.
- Restreaming.
- WebRTC delivery to browser clients.
- Audio/two-way audio where supported.
- Protocol translation/transcoding only when necessary.

### Media processing

- FFmpeg.

Roles:

- recording/remuxing.
- codec handling.
- snapshots.
- clips.
- transcoding when unavoidable.

### Backend API

- Python + FastAPI.

### Database

- PostgreSQL.

Database stores metadata only:

- cameras.
- events.
- users.
- recognized entities.
- plate text.
- recording index.
- audit records.

### Frontend

- React / Next.js considered appropriate for the GARDA web application.

### Deployment

- Docker Compose initially.

### Remote access

- Tailscale or WireGuard.

Do not directly expose camera ONVIF or RTSP ports to the public internet.

---

## 13. Open-source software found on GitHub

### OpenIPC/viewer

Considered the best immediate GUI tool on macOS to test cameras.

Relevant capabilities found during research:

- macOS build.
- RTSP H.264/H.265.
- VideoToolbox hardware decode on macOS.
- ONVIF discovery.
- PTZ controls/presets.
- Multi-camera grid.
- Recording.
- Local object detection.
- Audio listen.
- Push-to-talk for cameras exposing RTSP backchannel.

Use case in GARDA:

- Camera capability testing.
- Quick manual verification before implementing features ourselves.

### AlexxIT/go2rtc

Chosen as a strong candidate for GARDA's streaming/protocol layer.

Relevant capabilities:

- macOS / Linux / Windows binaries.
- RTSP.
- ONVIF.
- WebRTC.
- HLS/RTMP/MJPEG and other formats.
- HTTP/WebSocket APIs.
- two-way audio support for multiple camera protocols.
- FFmpeg integration when required.

### dicroce/revere

Interesting reference/open-source NVR project.

Features observed:

- ONVIF discovery.
- H.264/H.265.
- audio codecs.
- recording and playback.
- motion detection.
- RTSP restreaming.
- API/Web UI.
- YOLOv8 object detection.

Use primarily as architecture/reference inspiration unless later selected as a component.

### steelbrain/LemurCam

macOS-focused application that turns RTSP/ONVIF cameras into a macOS virtual camera/microphone.

Not intended as the core GARDA NVR, but useful for testing and Mac webcam use cases.

---

## 14. Network architecture

Preferred future physical topology:

- Router/firewall.
- Managed switch, ideally 2.5G/10G uplink where useful.
- Dedicated PoE switch for true-PoE cameras.
- GARDA Linux server on wired LAN.
- Separate camera network/VLAN.

Suggested segmentation:

- VLAN 10: main/user network.
- VLAN 20: CCTV network.
- VLAN 30: IoT.

Desired policy:

- Cameras -> GARDA server: allowed.
- GARDA server -> cameras: allowed.
- User devices -> GARDA server: allowed as authorized.
- Cameras -> unrestricted internet: preferably denied unless required.
- Direct internet -> camera RTSP/ONVIF: denied.

Remote access should terminate at VPN/server level rather than exposing individual cameras.

---

## 15. Hardware direction discussed

Potential server build previously considered:

- Ryzen 9-class CPU.
- 64-128 GB RAM.
- One or more NVIDIA GPUs, example RTX 3060.
- NVMe for OS/database/cache.
- Large HDD pool for recordings.

If multiple GPUs are used, workloads can be partitioned by camera groups or AI roles.

A simple scalable approach is to assign camera groups to specific GPUs.

---

## 16. Storage layout concept

Example:

```text
/data/cctv/
├── cam01/
│   └── 2026/10/02/
├── cam02/
│   └── 2026/10/02/
└── cam03/
    └── 2026/10/02/
```

Possible storage tiers:

- NVMe: OS, database, application, indexes/cache.
- HDD array/pool: continuous video recordings.

Retention policy should be configurable by camera and storage capacity.

---

## 17. Initial development phases

### Phase 1 — Camera ingest

- One EZVIZ/IP camera.
- Obtain stable RTSP stream.
- Feed into go2rtc.
- Display live view in web interface.

### Phase 2 — NVR basics

- ONVIF discovery/capability query.
- PTZ where supported.
- audio where supported.
- recording.
- playback/timeline.

### Phase 3 — General AI

- YOLO.
- person detection.
- vehicle detection.
- motion/event model.

### Phase 4 — Face

- face detection.
- enrolled face recognition.
- known/unknown event handling.

### Phase 5 — ANPR

- plate detection.
- plate crop/cleanup.
- OCR.
- searchable plate events.

### Phase 6 — Multi-camera application

- multi-camera dashboard.
- users/RBAC.
- mobile-friendly UI.
- remote access.
- notifications.

### Phase 7 — Advanced GARDA intelligence

- smart PTZ tracking.
- health monitoring.
- storage health.
- semantic/event search.
- automation and alerts.

---

## 18. Immediate next technical question

User has chosen Linux for the GARDA server and asked how Windows workloads can still be accessed or integrated.

Important distinction for the next architecture decision:

- A Linux host can provide SSH, web UI, file shares, and Linux remote desktop.
- Native Windows RDP sessions require a Windows OS somewhere.
- If Windows software is required, GARDA can run a Windows VM on the Linux server using KVM/QEMU/Proxmox-style virtualization, then users RDP into that Windows VM.
- Another option is a separate Windows machine/VM on the same LAN while GARDA core services remain Linux.

Recommended architecture to evaluate next:

Linux host as the primary GARDA hypervisor/server, with optional Windows VM(s) only for workloads that truly require Windows.

---

## 19. Working principles for future GARDA decisions

1. Prefer open standards over vendor cloud lock-in.
2. Separate camera ingest, recording, AI, and UI into modular services.
3. Keep original video independent of AI inference.
4. Use substreams for continuous AI when possible.
5. Keep camera networks isolated.
6. Do not expose camera RTSP/ONVIF directly to the public internet.
7. Treat marketplace "PoE" claims skeptically unless IEEE 802.3af/at is explicitly documented.
8. Test exact camera model/firmware because ONVIF capability varies widely.
9. Build GARDA so changing camera brands does not require rewriting the entire platform.
10. Use Linux as the 24/7 server baseline; use Windows only where a specific application requires it.


---

## 20. Virtualization, 4-GPU, and Windows interactive workloads

Latest architecture decision:

- Use **Proxmox VE** as the preferred physical host/hypervisor rather than Ubuntu bare metal when Windows workloads must coexist on the same physical server.
- Run the core GARDA services in an Ubuntu/Linux VM or dedicated Linux guest.
- Run a separate Windows VM for interactive Windows workloads.
- Windows users may connect with:
  - RDP for administration, office, and light desktop use.
  - Sunshine + Moonlight or Parsec-class low-latency streaming for gaming and GPU-accelerated interactive work.
- Windows may be used for gaming, Photoshop, Premiere, Resolve, Blender, OBS, and other Windows applications when a physical GPU is passed through.

Important GPU ownership rule:

- A normal consumer NVIDIA GPU passed through with VFIO is normally owned exclusively by one VM while attached.
- Do not design around one RTX-class consumer GPU being simultaneously used by Linux GARDA and a Windows VM.
- GPU reassignment can be automated, but it is not a seamless live hot-swap. The current workload/VM must safely release the GPU before another VM takes ownership.

Possible GARDA resource modes:

### GARDA MAX

- Ubuntu GARDA: 4 GPUs.
- Windows VM: off or no passed-through GPU.
- Intended for maximum AI throughput / overnight processing.

### BALANCED

- Ubuntu GARDA: 3 GPUs.
- Windows VM: 1 GPU.
- Intended for normal operation when Windows access is needed but GARDA remains primary.

### WINDOWS GAMING / EDITING

- Ubuntu GARDA: 2 GPUs.
- Windows VM: up to 2 GPUs if the software/use case benefits and passthrough topology is validated.
- Intended for gaming, editing, rendering, or other GPU-heavy Windows sessions.

Automation concept:

1. Stop or drain GARDA AI workers using a GPU that is about to be reassigned.
2. Detach/rebind the PCIe device as required by the Proxmox/VFIO configuration.
3. Start/restart the target Windows VM with the selected GPU(s).
4. When the Windows session ends, shut down the VM cleanly.
5. Reattach the GPU to the GARDA Linux workload.
6. Restart the corresponding AI workers.

This should be exposed later in the GARDA admin UI as explicit resource modes rather than attempting unsafe GPU hot removal.

---

## 21. Current hardware direction

Current user-selected direction for the GARDA lab/workstation build:

- **AMD Threadripper platform**.
- **128 GB RAM**.
- **4 NVIDIA GPUs** target.
- X399/TR4 used-market platform has been investigated as the value baseline.
- Threadripper 1950X + Gigabyte X399 AORUS PRO is currently documented as a preferred value combination in the hardware plan.
- Exact four-GPU model is still pending unless superseded by a later decision.
- 2 x NVMe plus a multi-HDD CCTV storage pool is the current storage direction.
- Proxmox VE is the preferred virtualization layer when Linux GARDA and Windows interactive workloads share the machine.

Physical design requirements remain critical:

- Four usable PCIe slots with appropriate electrical lane allocation.
- Sufficient slot spacing or quality risers for four GPUs.
- High-airflow chassis.
- PSU sized only after exact GPU power requirements are known.
- Separate consideration for NVMe, 10GbE, HBA/storage expansion, and IOMMU grouping.

---

## 22. Procurement-spec separation

The Threadripper/X399 machine above is a **GARDA development/lab/value workstation direction** discussed in chat.

Do not automatically treat it as compliant with the formal PUSADA TNI production procurement specification.

The formal KAK currently specifies, for the AI server, a rack 2U/4U system with Xeon/EPYC CPU, minimum 128 GB ECC RAM, NVIDIA enterprise CUDA-compatible GPU, NVMe OS RAID 1, redundant PSU, 10GbE, rail kit, monitoring, and minimum three-year onsite warranty.

Therefore:

- Threadripper/X399 can be used for development, prototype, integration lab, or internal testing when appropriate.
- If the same machine is intended to satisfy the formal KAK AI-server line item, the hardware specification must be reconciled or formally amended before procurement.
- Keep the development hardware decision separate from the contractual production-server requirement unless the procurement documents are changed.

---

## 23. Continuity rule

For future GARDA sessions, this file is the canonical architecture/context summary.

When a major decision changes any of the following, update this file and add a dated conversation log:

- camera/protocol strategy
- server OS/hypervisor
- CPU/motherboard/RAM/GPU selection
- storage topology
- Windows virtualization/passthrough strategy
- AI pipeline
- production procurement requirements
- security/network architecture


---

## 24. Camera lab procurement update — 2026-11-03

User selected **NEXTCAM NC-858** as a GARDA lab camera.

Verified marketplace specification available during research:

- ONVIF support is explicitly advertised.
- RJ45 LAN port is present for wired network use.
- Wi-Fi 2.4 GHz is also supported.
- PTZ is advertised at approximately 320° pan / 90° tilt.
- Built-in microphone and speaker with two-way audio are advertised.
- Motion/human detection and human tracking are advertised.
- H.264 is listed.
- microSD up to 128 GB is listed.
- Outdoor/IP66 is advertised.
- Power remains **12V 1A via separate adapter**, so this camera must **not** be treated as native IEEE 802.3af/802.3at PoE.

Purpose in GARDA:

- Use NC-858 as the primary inexpensive interoperability lab camera for ONVIF discovery, RTSP/media-profile probing, PTZ, audio, and event testing.
- Validate actual exposed ONVIF capabilities on the purchased unit/firmware rather than assuming every advertised feature is exposed through ONVIF.

User also wants a second ultra-low-cost camera at **<= Rp250,000** for compatibility testing.

Current market candidates observed around this budget include:

- **YOOSEE JW28 PTZ** around Rp220,000, explicitly advertised as ONVIF.
- Generic YOOSEE PTZ/5-antenna ONVIF units around Rp200,000-Rp205,000.
- **DINGS Smart CCTV WiFi 2K PTZ** around Rp225,900, advertised with ONVIF/NVR support.
- Some generic YOOSEE outdoor ONVIF listings around Rp246,000 or lower.

Important qualification:

- For the second cheap camera, do not assume RJ45, RTSP, or PoE solely from the word ONVIF in a marketplace title.
- Prefer a unit where the seller can show the physical RJ45 port and confirm wired LAN use.
- True IEEE 802.3af/at PoE at <= Rp250,000 was not verified in the current market check.
- The goal of this second camera is interoperability stress testing, not production deployment quality.

