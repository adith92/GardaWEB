# GARDA Tier 1 — LAN video toolchain

This directory prepares the local/on-premise services for the T1 Basic implementation. It contains no customer camera URLs, credentials, biometric samples, or classified data.

## Components

| Component | Role | T1 status | License / note |
|---|---|---|---|
| MediaMTX | LAN media gateway: RTSP/RTSPS, HLS, WebRTC, relay | Recommended baseline | MIT |
| `onvif` Node package | ONVIF discovery, profiles, PTZ and device capability adapter | Backend adapter to build | MIT |
| go2rtc | Optional restream compatibility layer | Optional; avoid duplicate paths | MIT |
| Frigate | Optional NVR/object detection service for evaluation | Benchmark/profile only | MIT repository; audit images/models |
| CompreFace | Face recognition API | T2/add-on, not enabled in T1 | Apache-2.0 |
| OpenALPR | ANPR engine | Candidate with legal review | AGPL-3.0 |

## Local start

1. Install Docker Desktop or Docker Engine on the on-prem host.
2. Copy `mediamtx.yml` and start the baseline profile:

   `docker compose -f infra/tier1/docker-compose.yml up -d mediamtx`

3. Publish a test stream into MediaMTX, then verify the LAN endpoints listed in the compose file.
4. Enable `bridge` or `analytics` profiles only after the camera inventory and hardware benchmark are approved.

The compose file is a development harness. It is not a production KAK deployment: it does not configure RAID, redundant NVR, 90-day retention, enterprise GPU, UPS, VLAN policy, credentials, TLS certificates, or customer-specific camera paths.

## Security rules

- Keep camera credentials in the backend secret store; never put them in the browser or Git.
- Bind development services to the CCTV/management VLAN and do not expose camera ports publicly.
- Use one tested RTSP path per camera and record capability results for `DISCOVER`, `LIVE`, `RECORD`, `PLAYBACK`, `PTZ`, `AUDIO`, and `METADATA`.
- Keep face identification disabled for T1. Face presence and ANPR events must carry camera/time/evidence provenance.
- Pin image tags and record third-party notices before a customer deployment.
