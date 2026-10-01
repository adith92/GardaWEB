# Mockup Demo Spec — PUSADA MONITORING CENTER | GARDA

## Goal
Create a polished interactive frontend demo suitable for leadership/product review. No real backend, camera, or biometric processing is required in the first demo. Use deterministic mock data and simulated state.

## Primary Screen Concept

### Desktop target
- 1920x1080
- Dark command-center UI
- Left rail: 220–248px
- Top status bar: 52–60px
- Main content: flexible
- Right incident/event rail on COMMAND screen: 340–380px

### App shell
**Top bar**
- Product mark: `PUSADA MONITORING CENTER | GARDA`
- Site selector: `PUSADA HQ`
- Global search / command button
- Connectivity indicator
- Server health
- Recording state
- User profile

**Sidebar**
- COMMAND
- LIVE
- PLAYBACK
- EVENTS
- FACES
- PLATES
- MAP
- INCIDENTS
- ASK GARDA
- ANALYTICS
- VAULT
- DEVICES
- SYSTEM
- AUDIT
- SETTINGS

## Screen 1 — COMMAND

### Layout
Top KPI strip, 4–5 concise metrics only:
- Cameras Online `8/8`
- Active Alerts `3`
- Unknown Faces `2`
- Unknown Plates `1`
- Storage `62%`

Main left area:
- Site map / schematic of compound
- Camera nodes
- Active event pins
- Selecting a camera opens mini live preview

Bottom-left:
- 4-camera live strip

Center-bottom:
- Event timeline for last 60 minutes

Right rail:
- `ACTIVE INCIDENTS`
- severity
- time
- camera
- short title
- acknowledge button

## Screen 2 — LIVE

### Layout
Header row:
- Site dropdown
- Camera search
- Layout selector: 1 / 4 / 9 / 16
- `Auto-cycle`
- Fullscreen

Main:
- 3x3 camera grid by default
- Each tile: camera name, recording dot, online state, bitrate/FPS on hover
- Selected tile uses a subtle green outline

Right drawer when selected:
- PTZ controls
- Snapshot
- Manual record
- Open playback
- Create incident
- Camera metadata

## Screen 3 — PLAYBACK

Top:
- Camera multi-select
- Date picker
- Event filters

Main:
- Large video player
- Synchronized 4-camera option

Bottom:
- 24-hour timeline
- colored markers for person, face, plate, alert, incident
- zoomable time scale

Right panel:
- detected entities near playhead
- bookmarks
- export clip

## Screen 4 — EVENTS

Table-first design, not cards.
Columns:
- Time
- Severity
- Type
- Camera
- Entity
- Confidence
- Status
- Evidence

Left filter rail or top filter row:
- Date
- Camera
- Zone
- Person/Vehicle
- Known/Unknown
- Severity

Click row → evidence drawer with snapshot + clip preview.

## Screen 5 — FACES

Two-panel design:
Left:
- Known persons
- Unknown queue
- Watchlist

Main:
- searchable face gallery
- person detail with reference photo
- latest sightings
- confidence trend
- last seen camera
- journey timeline

Use only fictional synthetic identities.

## Screen 6 — PLATES

Top:
- plate search box
- registered / unknown / watchlist tabs

Main table:
- Plate
- Vehicle
- Status
- First Seen
- Last Seen
- Current State
- Entry Gate

Detail drawer:
- plate crop
- vehicle crop
- entry/exit timeline
- related incidents

## Screen 7 — MAP

Full-screen operational map.
Layers:
- Camera field of view
- Zones
- Device state
- Active alerts
- Person/vehicle event markers

Future-preview toggle in demo:
`Digital Twin Preview`
This may switch to a clean 2.5D schematic with moving synthetic dots and global IDs. Clearly label as preview/demo.

## Screen 8 — INCIDENTS

Left:
- incident queue
- filters by status/severity

Main:
- incident header
- status
- assigned operator
- AI summary
- chronological timeline

Right:
- evidence list
- linked faces
- linked plates
- cameras

Actions:
- acknowledge
- assign
- add note
- attach evidence
- export package
- resolve

## Screen 9 — ASK GARDA

This should feel like an operator command surface, not a general chatbot.

Left 65%:
- conversation / results
- video/search result tiles only when needed

Right 35%:
- active context
- selected site
- date range
- cameras
- entities

Seeded prompts:
- `Apa yang terjadi setelah jam 23:00 tadi malam?`
- `Cari kendaraan yang masuk tapi belum keluar.`
- `Kapan terakhir B 1234 GAR terlihat?`
- `Tampilkan unknown face hari ini.`
- `Buat laporan shift malam.`

Responses should include clickable evidence references.

## Screen 10 — VAULT

Product name inside app: `GARDA Vault`

Layout:
- left folder tree
- top breadcrumb
- central file table
- right metadata/activity drawer

Columns:
- Name
- Type
- Owner
- Size
- Modified
- Retention
- Access

Top actions:
- New folder
- Upload
- Share
- Archive

Special folders:
- Incident Evidence
- CCTV Exports
- Command Reports
- Shared Operations
- Personal

Storage usage card:
- Hot
- Warm
- Archive

## Screen 11 — ANALYTICS

Charts:
- People detected by hour
- Vehicles by hour
- Known vs unknown
- Incident severity trend
- Camera uptime
- Storage growth

Use clean operational charts, not a colorful BI dashboard.

## Screen 12 — SYSTEM / DEVICES

Device table:
- Name
- Type
- IP
- State
- Health
- Uptime
- Temperature
- Stream state
- Firmware

System cards:
- R630 CPU
- RAM
- Storage pool
- Database
- Frigate service
- MediaMTX
- MQTT
- GPU Node (shown as `Not Installed` in V1 demo)

## Interaction Simulation

### Simulated event ticker
Every 20–40 seconds, add one deterministic event from a finite queue.
Do not use randomness that makes screenshots unstable unless a seed is fixed.

Example event queue:
1. `22:14:03 — CAM-07 — Unknown Plate — B 1234 GAR`
2. `22:15:22 — CAM-06 — Restricted Zone Entry`
3. `22:16:01 — CAM-04 — Known Face — Arif Pratama`
4. `22:18:17 — CAM-03 — Vehicle Dwell > 10m`
5. `22:22:08 — CAM-08 — Camera Blur Warning`

### Demo state
- 8 cameras total
- 8 online initially
- 3 active incidents
- 2 unknown faces today
- 1 unknown plate today
- 62% storage utilization

### Event severity
- Critical: red
- High: red-orange
- Medium: amber
- Low/info: cool gray/blue

## Visual Design Direction

### Mood
- disciplined
- technical
- confident
- operational
- calm under pressure

### Avoid
- cyberpunk neon
- video-game HUD overload
- camouflage UI
- giant gradients
- decorative hexagons everywhere
- excessive glassmorphism

### Colors
Suggested starting tokens:
- `bg`: #0B0F12
- `surface-1`: #11171C
- `surface-2`: #161E24
- `border`: #273139
- `text`: #E8EEF2
- `muted`: #8E9BA5
- `primary`: #5E8C61
- `primary-strong`: #79A77B
- `critical`: #D44A4A
- `warning`: #D39A3A
- `info`: #4F89A8

These are starting points for concepting, not an irreversible color lock.

### Typography
- UI: Inter / Geist / IBM Plex Sans
- Optional headings: IBM Plex Sans Condensed or another disciplined condensed sans

### Icons
- Lucide-style outline icons, consistent stroke
- no cartoon imagery

## Responsive Behavior

Primary: desktop/command display.

At 1366px:
- collapse right incident rail into drawer
- sidebar may shrink to icon + label compact mode

Mobile is not required for first Codex demo.

## Demo Copy

Logo line:
`PUSADA MONITORING CENTER`
Submark:
`GARDA`
Caption when needed:
`Garda Analitik, Rekognisi, Deteksi & Automasi`

Suggested welcome title:
`Command Overview`

Suggested operational status:
`All core services operational`

## Demo Acceptance Checklist

- Visual hierarchy is instantly understandable
- No fake marketing hero page
- Main product opens directly into COMMAND
- At least 8 functional routes
- Sidebar navigation works
- Selected states work
- Search/filter controls update local data
- Incident acknowledgement updates state
- Ask GARDA seeded queries return contextually relevant simulated responses
- Vault upload UI works locally or simulates success
- Charts render
- Camera tiles have realistic controls
- No lorem ipsum
- No external paid API required
