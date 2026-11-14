# GARDA AI Vision — source and audit handoff

Date: 2026-11-14 | Status: **IMPLEMENTED DEV SCAFFOLD**, not deployed; tests are limited to isolated logic / mock API.

## Mandatory project boundaries
- Target repository: `adith92/GardaWEB`, React 19 + Vite 6 demo, source instructions in `AGENTS.md`; preserve existing simulated data and app routes.
- Proposed source branch: `feature/ai-vision-clearcam-win-lab-20261114`. Do NOT merge into main without review.
- ClearCam upstream: `roryclear/clearcam`, branch main HEAD inspected in this session: `553be39ba6f20ce055a7418ed54636b32059b4ad`, GPL-3.0. README says Windows requires FFmpeg fix; tinygrad pinned by upstream git commit and OpenCV 4.10.0.84. Never falsely claim their original server works on Windows.
- Distinguish our independent adapter from copied ClearCam source. Wire their custom notification endpoint through trusted loopback relay; do not assert generic ClearCam REST endpoints that were not verified.
- GARDA generic Basic: 1 site/1–49 channels, face **presence only**, simple ANPR. Face identity is enabled only under separately authorized PUSADA contractual entitlement. Mobile native starts T3 per existing decision register (T2 viewer exception unapproved).
- Owner-confirmed schedule: **8 implementation weeks + 2 testing/commissioning weeks, 12 months support**. The uploaded KAK text contradicts itself on months/weeks and warranty 12 weeks vs 12 months; reconcile formally before contractual use.

## In-scope development code
1. FastAPI REST service that binds to localhost by default; three distinct bearer tokens; encrypted SQLite event payload and face template table; audit rows; role-based denial and redaction.
2. OpenCV RTSP read-only substream sampler (inference every ~2s); candidate face presence + optional license-provided YOLOv8 plate ROI detector + EasyOCR; whole-frame fallback; decoupled from NVR recording. No main-stream evidence extraction, tracking, or 16-channel optimization yet.
3. Optional licensed ONNX face-embedding provider with explicit contract gate; face enrollment restricted to admin, reference only, manual human review required. This does not establish legal/consent verification by itself.
4. PTZ ONVIF zoom ± speed with 2s maximum command and Stop on exit; only after camera-specific capability verification.
5. ClearCam multipart notification compatibility via local forwarding relay (no image persistence).
6. An opt-in React local AI workbench plus Kotlin Android API-read starter. There is no finished native Android app.

## High-priority audit failures to look for
| Priority | Area | Required next action |
| --- | --- | --- |
| BLOCKER | Authorization | Replace static role tokens with named user JWT/OIDC, MFA, scoped site policy, device binding, short TTL/revocation; TLS and audit token use. |
| BLOCKER | Face identity | Validate model provenance/license, embedding preprocess + alignment + liveness/quality, false-match thresholds, ground truth, encrypted retention and deletion. Validate authority and legal basis before collecting templates. |
| BLOCKER | Privacy | Defined retention policy for plate and face, data minimization, incident response, key rotation, access review, encrypted storage, backup, chain of custody. |
| HIGH | ANPR | Validate licensed plate ONNX detector, vehicle tracking/ROI, optical-zoom to native pixels (not digital crop), high-res dual-stream verification, glare/night/angle test matrix, plate OCR benchmark. |
| HIGH | PTZ | ONVIF WSDL packaging Windows, GetConfigurations/Status, camera limits, preset recall, profiles, safety stop recovery and no concurrent commands. |
| HIGH | ClearCam | Run upstream separately on supported Linux/Mac; confirm real multipart notification paths, trigger rules and availability; review GPL-3.0 distribution and upstream model licenses. |
| HIGH | Evidence | Separate recorder + playback index, watermarked export + SHA256 manifest, time sync, video retention >=90 days per PUSADA, NVR failover, immutable logs. |
| HIGH | Scale | 16 camera parallel ingest, timed reconnection, per-stream backpressure, CPU/GPU benchmark, hardware and inference scheduling, queues; no throughput SLA inferred. |
| MEDIUM | Android | Build proper T3/KAK-authorized Android project, credential handling, device enrollment, offline sync plan, secure notification policy. |
| MEDIUM | CI | pytest and frontend build in controlled runner, dependency pin and CVE scan, functional PTZ tests on authorized physical hardware only. |

## Audit prompts to external model

Read `AGENTS.md`, `docs/GARDA_DECISION_REGISTER_v0.3.md`, KAK, and `services/garda-ai-vision` end to end. Do not rewrite or distribute the upstream ClearCam GPL code inside GARDA. Audit implementation for Windows 11 / Python 3.11 and Linux: dependency and licensing compatibility, invalid FastAPI dependencies, race conditions in threaded OpenCV inference and SQLite, camera secrets/SSRF, privacy/RBAC/site isolation, actual ONVIF zoom and stop, license plate detection accuracy gaps and ONNX preprocessing assumptions. Provide prioritized findings with file:line references and corrected code with tests. Do not invent model weights, successful camera PTZ tests, hardware frame rates or procurement acceptance.

## Source status and verification
- Local logical unit/API tests: `tests/test_core.py`, `tests/test_api.py`, five tests passed in isolated test environment on 2026-11-14.
- No real RTSP, FFmpeg, physical PTZ, licensed ONNX embedding, OCR recognition benchmark, Android APK build, NVR, or 16-camera soak test conducted.
- Any identified issue must be fixed in reviewed PR without deleting existing GARDA functionality.
