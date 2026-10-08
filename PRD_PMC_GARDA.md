> **ARCHIVED BASELINE NOTICE (2026-10-08):** This file is retained for history or demo only. New authoritative docs are [Decision Register v0.3](docs/docs/GARDA_DECISION_REGISTER_v0.3.md), [Basic PRD v1.0](docs/docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md), [Catalog v0.3](docs/docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md), and [PUSADA KAK Gap Matrix](docs/docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md). Owner now includes Basic person/face-presence/ANPR Lite; face *identity* starts T2; Base recording retention 7d while PUSADA KAK separately requires 90d. Do not use older T1/T2/T3 constraints as current truth.\n\n# PRD — PUSADA MONITORING CENTER (PMC GARDA)

## 1. Product Identity

**Formal name:** PUSADA MONITORING CENTER  
**Short name:** PMC  
**Platform codename / brand:** **GARDA**  
**Expansion:** **Garda Analitik, Rekognisi, Deteksi & Automasi**  
**Recommended lockup:** `PUSADA MONITORING CENTER | GARDA`

### Product statement
PMC GARDA is a unified video-intelligence, security-operations, storage, and incident-command platform for live CCTV monitoring, video recording, AI detection, face and license-plate recognition, searchable evidence, private-cloud storage, and command-center workflows.

### Product principles
1. **Local-first, cloud-ready.** Critical recording continues on-premise even when internet connectivity fails.
2. **Evidence before spectacle.** AI results always link back to video, snapshots, timestamps, and source cameras.
3. **Human control for critical actions.** AI may recommend or verify; irreversible physical actions require deterministic rules and/or operator approval.
4. **Security by default.** RBAC, audit logs, encryption, retention policies, and network segmentation are core features.
5. **Modular growth.** Start on Dell PowerEdge R630 and add a dedicated GPU inference node later without redesigning the whole platform.

---

## 2. Problem to Solve

Typical CCTV/NVR systems are fragmented: live video is separated from access logs, plate recognition, face recognition, incidents, storage, analytics, and operational reporting. Operators must manually inspect many camera feeds and search long recordings.

PMC GARDA turns camera streams into structured events and searchable evidence while remaining a normal CCTV monitoring and recording system.

---

## 3. Target Users

### Primary
- Command center / security operator
- Security supervisor
- System administrator
- Operations manager

### Secondary
- Executive / command leadership viewer
- Investigator / evidence reviewer
- IT / infrastructure team
- Facility / fleet / gate operator

---

## 4. High-Level Architecture

### Phase 1 — Core node
**Dell PowerEdge R630**
- Proxmox VE
- Ubuntu Server VM(s)
- Frigate NVR / video analytics
- MediaMTX for low-latency stream distribution
- PostgreSQL + pgvector
- MQTT broker
- Redis
- MinIO S3-compatible object storage
- API backend
- Web application
- Prometheus/Grafana or equivalent infrastructure telemetry

### Phase 2 — AI acceleration node
Dedicated GPU server added to the same rack/network:
- NVIDIA GPU
- DeepStream / TensorRT / compatible inference stack
- VLM / embeddings / advanced re-identification
- Multi-camera tracking / higher-throughput inference

### Camera ingestion
- RTSP / ONVIF from IP cameras
- RTSP restream from existing DVR/NVR where available
- Camera sub-stream for detection
- Camera main stream for high-quality recording/evidence

---

## 5. Storage Architecture

PMC GARDA should also function as a secure private-cloud storage platform.

### 5.1 Storage tiers
**Hot storage**
- Local NVMe/SSD for database, thumbnails, event cache, indexes

**Warm storage**
- Local surveillance HDD pool for recent CCTV recording

**Cold/archive storage**
- Optional remote S3-compatible object storage for long-term evidence/archive

### 5.2 PUSADA Vault module
Working name: **GARDA Vault**

Features:
- Personal/team folders
- Upload/download files
- Drag-and-drop uploads
- Folder tree
- Search
- Tags
- File preview
- Version history
- Share links with expiration
- Role-based permissions
- Quotas
- Retention policy
- Recycle bin
- Audit log
- Server-side checksum
- Optional encryption at rest
- S3-compatible backend

### 5.3 Video-specific storage
- Continuous recording
- Event clips
- Snapshots
- Face crops
- Plate crops
- Audio event snippets where permitted
- Incident evidence package
- Configurable retention by camera/zone/event severity

### 5.4 Recommended redundancy
For evidence-critical use, avoid a single HDD as the only copy. Recommended baseline:
- At least 2 x surveillance HDD in RAID1 / mirror for important video
- UPS-backed writes
- Optional offsite/archive copy for critical incidents

---

## 6. Product Modules

### 6.1 COMMAND — Main Dashboard
Purpose: real-time situational overview.

Widgets:
- Camera online/offline status
- Active alerts
- Current persons/vehicles detected
- Unknown faces
- Unknown plates
- Storage usage
- Server/GPU health
- Network status
- UPS status
- Incident queue
- Live event ticker
- Site map / floor map

### 6.2 LIVE — Camera Wall
Layouts:
- 1, 4, 9, 16, 25 feeds
- Custom layout
- Drag/reorder
- Full screen
- Digital zoom
- Snapshot
- Start manual recording
- PTZ controls if supported
- Mute/unmute
- Stream quality selector
- Camera metadata overlay

### 6.3 PLAYBACK — Recording Timeline
- 24/7 timeline
- Multi-camera synchronized playback
- Event markers
- Person/vehicle/plate/face markers
- Speed controls
- Frame-step
- Clip export
- Snapshot export
- Bookmark incident

### 6.4 EVENTS — Detection Feed
Event types:
- Person
- Vehicle
- Animal
- Plate detected
- Known face
- Unknown face
- Restricted-zone entry
- Loitering
- Line crossing
- Crowd threshold
- Camera tamper
- Audio alert
- Device offline

Filters:
- Date/time
- Camera
- Zone
- Event class
- Severity
- Person identity
- Plate
- Status

### 6.5 FACES — Face Intelligence
- Known persons directory
- Enrollment from approved reference images
- Unknown-face queue
- Last seen
- Appearance history
- Camera journey
- Confidence score display
- Manual confirm/reject
- Watchlist / priority tagging
- Retention and deletion controls

### 6.6 PLATES — Vehicle Intelligence
- Plate recognition log
- Registered vehicle directory
- Unknown plates
- Last seen
- Entry/exit history
- Parking duration
- Whitelist/blacklist status
- Vehicle photo and metadata
- Gate association

### 6.7 MAP — Site Digital Twin
Phase-based capability:
- Floor/site map with camera icons
- Live camera health
- Active incident pins
- Zone overlays
- Person/vehicle event positions where available
- Future: multi-camera 3D/world-coordinate tracking

### 6.8 INCIDENTS — Incident Command
Incident record includes:
- Incident ID
- Severity
- Status
- Timeline
- Associated people
- Associated vehicles
- Cameras
- Evidence clips
- Snapshots
- Notes
- Assigned operator
- Acknowledged by
- Resolution
- AI-generated summary marked as AI-generated

Actions:
- Assign
- Escalate
- Add evidence
- Export evidence package
- Close/reopen

### 6.9 ASK GARDA — Security Copilot
Natural-language examples:
- “Cari mobil putih yang masuk antara jam 19:00–22:00.”
- “Kapan terakhir B 1234 ABC terlihat?”
- “Tampilkan unknown face tadi malam.”
- “Ada kejadian penting setelah jam 23:00?”
- “Buat ringkasan shift malam.”
- “Tampilkan kamera yang offline.”

Principle:
Every answer must show source evidence links when available.

### 6.10 RULES — Automation Engine
Rule builder supports:
- Time schedules
- Camera/zone
- Detection class
- Known/unknown identity
- Plate list
- Duration threshold
- Count threshold
- Device-health state

Actions:
- Create alert
- Save clip
- Save snapshot
- Open incident
- Notify operator
- Send webhook
- Send email/Telegram/approved messaging integration
- Future gate/relay action only with strict safety controls

### 6.11 ANALYTICS
- People count
- Vehicle count
- Entry/exit trend
- Peak hours
- Dwell/loiter duration
- Plate frequency
- Incident frequency
- Camera uptime
- Storage growth
- Alert false-positive rate
- Operator response time

### 6.12 VAULT — Private Cloud Storage
- Files
- Evidence
- Shared folders
- Team folders
- Uploads
- Archive
- Retention
- Search
- Permission management

### 6.13 DEVICES
- Cameras
- DVR/NVR
- Switches
- Servers
- UPS
- Storage drives
- Optional sensors/controllers

Each device:
- Online state
- IP
- Model
- Firmware
- Uptime
- Last heartbeat
- Temperature where available
- Stream health
- Storage health

### 6.14 SYSTEM HEALTH
- CPU
- RAM
- Disk
- SMART status
- RAID status
- GPU utilization if present
- Network throughput
- Dropped frames
- RTSP failures
- Camera FPS
- Bitrate
- UPS runtime
- Service health

### 6.15 AUDIT
Log:
- Login/logout
- Video viewed
- Evidence exported
- Face enrollment changes
- Plate list changes
- Permission changes
- Rule changes
- File shares
- Deleted items
- Admin actions

---

## 7. Advanced / Flagship Features

### 7.1 Verified AI Alerts
Two-stage flow:
1. detector identifies candidate event
2. visual-language model verifies and explains event
3. only verified event becomes high-priority alert

### 7.2 Cross-Camera Re-Identification
Maintain a global entity identity across multiple cameras where technically possible.

### 7.3 Entity Timeline
Merge related evidence around a person or vehicle:
- face
- plate
- camera appearances
- access event
- incident links

### 7.4 Journey Reconstruction
Visual sequence such as:
Gate → Parking → Lobby → Floor 2

### 7.5 Natural-Language Rule Creation
Example:
“Alert saya jika ada orang masuk gudang setelah 22:00 dan bertahan lebih dari 2 menit.”

System converts this into a proposed rule and requires confirmation before activation.

### 7.6 Smart Camera Health
Detect:
- black/covered lens
- blur
- drastic view shift
- frozen frame
- unusual darkness/brightness
- frame-rate degradation
- prolonged stream interruption

### 7.7 Audio Intelligence
Where legal and supported:
- alarm
- glass break
- shouting/screaming
- siren
- horn
- other configurable acoustic events

### 7.8 Executive / Shift Report
Auto-generated daily/shift summary containing:
- camera uptime
- incident count
- notable events
- unknown face count
- unknown plate count
- after-hours activity
- storage health
- outstanding incidents

### 7.9 Evidence Integrity
Evidence export contains:
- report PDF
- source clips
- snapshots
- metadata JSON
- audit entries
- SHA-256 checksums

### 7.10 Future Digital Twin / 3D Tracking
For calibrated overlapping cameras and GPU infrastructure:
- world-coordinate position
- trajectory
- direction
- speed
- global object ID
- map visualization

---

## 8. User Roles & RBAC

Suggested roles:
1. Super Admin
2. System Admin
3. Command Supervisor
4. Operator
5. Investigator
6. Executive Viewer
7. Gate Operator
8. Storage User
9. Auditor

Example restrictions:
- Executive viewer: dashboards/reports only
- Operator: live/events/incidents, no system config
- Investigator: playback/evidence/export
- Auditor: audit logs read-only
- System admin: devices/network/services

---

## 9. Security Requirements

- HTTPS everywhere
- MFA-ready authentication
- RBAC
- Session management
- Audit trails
- Encryption at rest where practical
- Encrypted remote backup
- CCTV VLAN isolation
- Management VLAN
- No direct public exposure of camera RTSP ports
- VPN / zero-trust remote access preferred
- Signed or checksummed evidence exports
- Account lockout / rate limiting
- Backup and restore workflow
- Secrets stored outside source code

Privacy controls:
- retention policy
- face-record deletion
- role restrictions for biometric search
- visible audit trail for sensitive searches/exports

---

## 10. MVP Scope for Demo

The Codex demo should simulate the finished product visually without requiring real cameras.

### Must-have demo screens
1. Login
2. Command Dashboard
3. Live Camera Wall
4. Playback Timeline
5. Events
6. Face Intelligence
7. Plate Intelligence
8. Incidents
9. GARDA Vault
10. Ask GARDA
11. Site Map
12. System Health
13. Devices
14. Settings / Roles

### Demo interactions
- Change camera-wall layout
- Open camera detail
- Simulate live event arrival
- Search events
- Click a person and view timeline
- Click a plate and view entry/exit history
- Open incident detail
- Add evidence to incident
- Export simulated incident
- Ask pre-seeded natural-language questions
- Upload a demo file into GARDA Vault
- Switch between site map and camera view
- Acknowledge an alert

---

## 11. Demo Data

Use fictional / synthetic demo data only.

Suggested cameras:
- CAM-01 Main Gate
- CAM-02 Front Yard
- CAM-03 Parking East
- CAM-04 Lobby
- CAM-05 Corridor A
- CAM-06 Warehouse
- CAM-07 Rear Gate
- CAM-08 Server Room

Suggested incident examples:
- Unknown person after hours
- Unknown plate at rear gate
- Camera blur/tamper warning
- Restricted-zone entry
- Vehicle dwell > 10 minutes

---

## 12. UI / Brand Direction

### Visual character
A modern command-center interface rather than a game-like “military UI”.

Recommended palette:
- Background: near-black charcoal / graphite
- Surfaces: dark slate
- Primary accent: muted army green / emerald
- Secondary accent: steel / cool gray
- Critical: red
- Warning: amber
- Normal: green
- Information: cyan/blue used sparingly

Avoid:
- camouflage backgrounds
- excessive glowing neon
- sci-fi clutter
- fake radar decorations
- overly dense borders

### Typography
- Clean condensed or technical heading style
- Highly readable sans-serif for UI and data

### Signature UI motifs
- left navigation rail
- compact top status bar
- central operational canvas
- live event ticker
- severity-coded incident rail
- camera health dots
- evidence drawer
- command palette / Ask GARDA input

---

## 13. Primary Navigation

Suggested sidebar order:
1. COMMAND
2. LIVE
3. PLAYBACK
4. EVENTS
5. FACES
6. PLATES
7. MAP
8. INCIDENTS
9. ASK GARDA
10. ANALYTICS
11. VAULT
12. DEVICES
13. SYSTEM
14. AUDIT
15. SETTINGS

---

## 14. Technical Stack Recommendation

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui where appropriate
- TanStack Query
- Zustand or equivalent small client-state layer
- Recharts/ECharts for analytics
- MapLibre / Leaflet for site/map views where relevant

### Backend
- FastAPI or NestJS
- PostgreSQL
- pgvector
- Redis
- MQTT
- MinIO

### Video
- Frigate
- MediaMTX
- WebRTC for low-latency browser live view
- HLS fallback

### Deployment
- Docker Compose initially
- Proxmox VMs/LXC on R630
- Later Kubernetes only if scale truly requires it

---

## 15. Non-Functional Requirements

- Responsive from 1366x768 upward
- Primary design target: 1920x1080 command-center display
- Secondary target: 2560x1440
- Tablet read-only support later
- Dark mode is the primary mode
- Keyboard navigation for operators
- Fast navigation between alert → camera → recording → incident
- No modal-heavy workflow for frequently used actions

---

## 16. Roadmap

### V1 — Core Monitoring
Live, recording, playback, events, device health, storage, incidents.

### V2 — Recognition
Face, plates, zones, rules, notifications, analytics.

### V3 — Intelligence
Ask GARDA, semantic search, AI summaries, verified alerts.

### V4 — Command Automation
Advanced rule orchestration, executive/shift reports, evidence automation.

### V5 — Multi-Camera Intelligence
Re-identification, journey reconstruction, advanced behavior analytics.

### V6 — Digital Twin
Calibrated multi-camera world model, 3D object tracking, unified entity graph.

---

## 17. Demo Success Criteria

The demo is successful if a first-time viewer can understand within 60 seconds that PMC GARDA combines:
1. CCTV monitoring
2. AI recognition
3. incident command
4. searchable evidence
5. private cloud storage
6. infrastructure monitoring
7. an AI security copilot

The demo should feel like one coherent operational product, not a collection of dashboards.
