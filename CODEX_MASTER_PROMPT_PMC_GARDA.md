# CODEX MASTER PROMPT — Build the PMC GARDA Interactive Demo

Build a polished interactive frontend demo for a product named:

**PUSADA MONITORING CENTER | GARDA**  
GARDA = **Garda Analitik, Rekognisi, Deteksi & Automasi**

The product is a unified CCTV monitoring, AI video-intelligence, incident-command, infrastructure-health, and private-cloud storage platform.

## IMPORTANT WORKFLOW

1. First read these project documents:
   - `PRD_PMC_GARDA.md`
   - `MOCKUP_DEMO_SPEC.md`
   - `DEMO_DATA.json`
   - `DESIGN_TOKENS.json`
2. Before coding, create complete visual concept screenshots for the main application using Image Gen according to the frontend-app-builder workflow.
3. The concept must cover the complete primary COMMAND screen and detail concepts for LIVE, INCIDENTS, ASK GARDA, and GARDA Vault where necessary for readable implementation detail.
4. Present the concept for approval before implementation if running in Plan mode.
5. Once approved, implement faithfully. Do not reinterpret the approved concept.
6. Verify the browser implementation against the concept screenshots.

## FRAMEWORK

Use:
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui where it improves consistency
- Lucide icons
- TanStack Query only if useful for mock async behavior
- Zustand or lightweight React state for local demo state
- Recharts or ECharts for analytics

Do not create a marketing landing page. The application should open directly into the operational product shell.

## TARGET

Primary viewport: 1920x1080  
Secondary viewport: 1366x768  
Dark operational command-center UI.

## REQUIRED ROUTES

Create working navigation for:

- `/command`
- `/live`
- `/playback`
- `/events`
- `/faces`
- `/plates`
- `/map`
- `/incidents`
- `/ask-garda`
- `/analytics`
- `/vault`
- `/devices`
- `/system`
- `/audit`
- `/settings`

The root `/` should redirect to `/command`.

## DESIGN CHARACTER

The UI should feel:
- disciplined
- technical
- authoritative
- calm
- modern
- operational

It should NOT look:
- cyberpunk
- gaming HUD
- camouflage
- neon-heavy
- sci-fi decorative

Use a dark graphite/slate base and a restrained military-green operational accent.

## APP SHELL

### Sidebar
Use this order:
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

### Top bar
Include:
- `PUSADA MONITORING CENTER | GARDA`
- site selector: `PUSADA HQ`
- global command/search control
- server/recording/network indicators
- current user

## CORE DEMO STATE

Use deterministic mock data only.

Initial status:
- cameras: 8/8 online
- active incidents: 3
- unknown faces today: 2
- unknown plates today: 1
- storage utilization: 62%
- R630 core server: healthy
- GPU node: not installed / future expansion

Cameras:
- CAM-01 Main Gate
- CAM-02 Front Yard
- CAM-03 Parking East
- CAM-04 Lobby
- CAM-05 Corridor A
- CAM-06 Warehouse
- CAM-07 Rear Gate
- CAM-08 Server Room

## COMMAND SCREEN

This is the most important screen.

Include:
- compact KPI strip
- site map / schematic with camera nodes
- 4-camera live strip
- event timeline
- right active-incident rail
- storage and infrastructure health indicators
- meaningful click states

Do not overfill the top of the screen with cards.

## LIVE SCREEN

- 1/4/9/16 layout selector
- 3x3 default camera grid
- working selection state
- camera detail drawer
- snapshot button
- manual record button
- open playback button
- create incident button
- PTZ control visualization for compatible cameras

The video tiles can use generated/static demo surveillance imagery or synthetic placeholders that look realistic, but never leave blank black rectangles as the finished experience.

## PLAYBACK

- camera selector
- date selector
- large player
- timeline with event markers
- synchronized multi-camera mode mock
- clip export action
- frame/speed controls

## EVENTS

Use a serious data table.
Filters must work locally.
Click a row to open an evidence drawer.

## FACES

Use fictional synthetic people only.
Include:
- Known
- Unknown Queue
- Watchlist
- Person detail
- Last seen
- Camera journey timeline
- confidence

## PLATES

Include:
- searchable plate log
- registered/unknown/watchlist
- entry/exit history
- parking duration
- related incidents

Use fictional plate examples only.

## MAP

Create a clean operational site schematic with cameras and zones.
Add a demo-only toggle named `Digital Twin Preview` that visualizes synthetic tracked entities on the map. Clearly mark it as a preview.

## INCIDENTS

Build a convincing case-management screen with:
- queue
- status
- severity
- assignee
- AI summary
- timeline
- evidence
- people
- vehicles
- cameras
- notes

Working actions:
- acknowledge
- assign
- add note
- attach evidence
- export simulated package
- resolve

## ASK GARDA

Treat this as an operational command surface, not a generic chatbot.

Seed these queries:
- `Apa yang terjadi setelah jam 23:00 tadi malam?`
- `Cari kendaraan yang masuk tapi belum keluar.`
- `Kapan terakhir B 1234 GAR terlihat?`
- `Tampilkan unknown face hari ini.`
- `Buat laporan shift malam.`

Return deterministic simulated answers with clickable evidence references.

## GARDA VAULT

Build a private-cloud storage UI with:
- folders
- breadcrumb
- file table
- metadata drawer
- upload
- new folder
- share
- archive
- storage tier usage

Special folders:
- Incident Evidence
- CCTV Exports
- Command Reports
- Shared Operations
- Personal

Simulate upload success locally.

## DEVICES / SYSTEM

Show:
- Dell PowerEdge R630 core server
- camera devices
- DVR/NVR placeholder device
- managed switch
- UPS
- storage drives

Metrics:
- CPU
- RAM
- storage
- uptime
- temperature
- RTSP health
- network
- dropped frames

GPU node should visibly show `Future Expansion / Not Installed`.

## ANALYTICS

Create clean operational charts for:
- people by hour
- vehicles by hour
- known vs unknown
- incident trend
- camera uptime
- storage growth

## INTERACTIONS

Implement meaningful local state:
- navigation
- filtering
- selecting cameras
- incident acknowledgement
- incident resolution
- event drawer
- simulated upload
- Ask GARDA canned questions
- layout switching
- Digital Twin Preview toggle

No dead controls for primary actions.

## SIMULATED LIVE EVENT FEED

Use a deterministic event sequence. It may advance with a timer, but keep seed/order stable.

Events:
1. `22:14:03 — CAM-07 — Unknown Plate — B 1234 GAR`
2. `22:15:22 — CAM-06 — Restricted Zone Entry`
3. `22:16:01 — CAM-04 — Known Face — Arif Pratama`
4. `22:18:17 — CAM-03 — Vehicle Dwell > 10m`
5. `22:22:08 — CAM-08 — Camera Blur Warning`

## QUALITY BAR

This should look like a serious product demo that could be shown to leadership.

Avoid:
- lorem ipsum
- random filler widgets
- excessive cards
- childish icons
- fake marketing copy
- giant rounded containers everywhere
- gradients unless they are subtle and purposeful

Typography, spacing, table density, icon consistency, and status color semantics must be deliberate.

## RESPONSIVE

At 1366x768:
- right incident rail becomes a drawer or collapsible panel
- sidebar may become compact
- preserve command-center usability

Mobile is not required for this version.

## DELIVERABLE

A working local frontend demo with:
- all routes above
- deterministic mock data
- polished visuals
- functional core interactions
- no paid external API dependency
- README with run instructions
- screenshots for COMMAND, LIVE, INCIDENTS, ASK GARDA, and VAULT

Before handoff, verify the app in-browser at 1920x1080 and 1366x768 and compare the rendered result against the approved concept screenshots.
