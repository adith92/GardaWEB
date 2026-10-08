> **ARCHIVED BASELINE NOTICE (2026-10-08):** This file is retained for history or demo only. New authoritative docs are [Decision Register v0.3](docs/GARDA_DECISION_REGISTER_v0.3.md), [Basic PRD v1.0](docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md), [Catalog v0.3](docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md), and [PUSADA KAK Gap Matrix](docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md). Owner now includes Basic person/face-presence/ANPR Lite; face *identity* starts T2; Base recording retention 7d while PUSADA KAK separately requires 90d. Do not use older T1/T2/T3 constraints as current truth.\n\n# GARDA — Tiered PRD & Implementation Specification v0.2
Updated: 2026-10-08 | Status: **Product discovery / pre-KAK** | Customer: government, primarily TNI.

## 0. Scope discipline
- Treat `docs/GARDA_DECISION_REGISTER_v0.2.md` as **owner-confirmed decisions**.
- Treat `docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md` as the **592-feature DRAFT universe** with indicative minimum tier, NOT 592 approved deliverables.
- Initial purchase/contract targets **Tier 1 Basic**. Do not let future-tier roadmap inflate delivery cost or claims.
- Initial development duration and budget previously discussed: **2 months, 15-person team, total ~4,800 person-hours, Rp1.2B planning budget**; these are planning inputs, **not a validated quote or fixed contractual commitment**.
- The existing GardaWEB code is an interactive demo; do not confuse mock functionality with commissioned backend operation.
- Exact acceptance requires customer KAK, legal use case and measured deployment sizing.

## 1. Product vision, personas and outcomes
**Vision**: GARDA is a unified secure on-prem video operations and incident platform that scales from an autonomous site VMS to a classification-aware unified government/TNI Command Center over four tiered deployments.

**Primary roles**: live operator, security supervisor, system administrator, investigator, auditor, unit commander/executive. Future Tier4: regional HQ operator, command approver, cross-unit grant approver, federation administrator, classification officer, incident dispatcher and integration owner.

**Product outcomes**
1. Record reliable camera source independent of AI inference.
2. Find and export evidence with integrity, audit, timestamps and access checks.
3. Maintain operations when site WAN/Internet is unavailable.
4. Restrict sites and organizational units by default, with policy-granted exceptions.
5. Upgrade from Basic to analytics/intelligence/federation *without replacing entire site recorder*.
6. Coordinate external platforms at Tier4 through a governed integration hub.

## 2. Tier positioning and feature delivery gate
| Tier | Product focus | Key distinctive modules | Commercial gate |
|---|---|---|---|
| T1 **BASIC** | Site VMS/NVR | Ingest, live, record, playback, export, device health, incidents, audit, site RBAC, maintenance | Only tier initially eligible for approved contract backlog |
| T2 **SMART** | Active video event monitoring | Object/zone analysis, advanced camera health, alert rules, operational AI analytics, some sensors | New contract/SOW |
| T3 **INTELLIGENCE** | Governed investigation | Face recognition, ANPR, re-ID candidates, semantic search, AI summaries, controlled case intelligence | New contract + biometric legal gate |
| T4 **SOVEREIGN COMMAND** | Full command hierarchy | Top HQ view/control of T1–T4 nodes via policy, classifications, cross-unit grants, integrations, multi-domain COP, HA/DR and digital twin | New contract + architecture/security/KAK gate |

**Critical note**: Suggested `T1` rows in catalog express foundational/tier placement, not 218 immediate implementation commitments. The *initial build* must be reduced to a contract-backed, measurable delivery slice below.

## 3. Tier 1 contract-slice recommendation (proposed; requires KAK sign-off)
### P0: Contract-core acceptance slice
| Module | Necessary behavior | Example acceptance / negative test |
|---|---|---|
| Identity & site access | Login, session, site asset ownership, least-privilege operator/admin/auditor roles, complete server-side authorization | Operator from Unit A cannot view Unit B feed, recordings, thumbs, events, media URLs or exports; stale sessions revoked |
| Camera registration | Add/discover verified ONVIF or RTSP camera, stream URI, codec, camera test, firmware and capability inventory | Actual cameras of at least two agreed models ingest; unsupported PTZ/audio capabilities shown honestly |
| Reliable NVR recorder | Continuous native main-stream recording, indexed segments, storage retention, crash/reconnect behavior | Video persists while AI process is off and WAN is disconnected; segment integrity verifiable |
| Live operations | Authenticated web wall 1/4/9/16, 25 if performance validated; quality selection, full screen, snapshot | No leak of direct camera credentials or unprotected RTSP access |
| Playback/export | Indexed per-camera timeline, time-jump/playback, video clip and snapshot export | Export has accurate camera IDs/times and SHA-256 manifest; access denial is auditable |
| Device & system health | Camera online/offline, disk capacity + SMART, service, CPU/RAM/network, alert queue | Disconnect camera/disk event causes correct state and event; no fake health from demo fixtures |
| Incident & shift workflow | Create/assign/acknowledge/status/notes/evidence/shift log | Every state change retains actor/timestamp and permitted roles |
| Audit & recovery | Audit of login/views/exports/config, backup/restore runbook, retention behavior, VPN/segmentation defaults | Restore and attempted unauthorized access tests recorded with screenshots/logs |

### P1: Basic options only if expressly purchased / after P0 acceptance
PTZ and audio backchannel (tested camera capability), synchronized multi-camera playback, customizable 25+ wall, motion markers, floor-plan sites, richer shift reports, advanced evidence bundle, UPS automation, maintenance history, offline license management, optional limited vault. Keep unapproved P1 rows out of initial KAK price and delivery promise.

### Explicit out-of-scope for initial Basic
Production face recognition; production ANPR; appearance search; cross-camera identity graph; advanced object behavior analysis; Ask GARDA; LLM/VLM incident conclusions; automated physical actuation; digital twin/3D; top HQ federation; official classification ABAC; special cross-unit grants (design hooks only); nationwide SIEM/GIS/radio/IoT command integrations. They require tier upgrade and relevant permissions.

### Basic UX screens
Login; Command Dashboard; Camera Wall; Playback; Camera/Device Inventory; Alerts/Events; Incident Register; Evidence Export History; Health; User/Role Settings; Audit; Retention/Backup Settings. Demo-only FACES/PLATES/ASK screens may remain in sandbox, but must be hidden or clearly labeled nonfunctional and license-gated in commissioned T1 UI.

## 4. Conceptual solution architecture (no tech stack lock)
```text
Cameras/DVR/NVR [VLAN isolated, RTSP/ONVIF]
       |                            Local Site GARDA (T1)
       v
Camera Adapter/Discovery -> Media Gateway --> Authenticated Live Stream
       |                       |
       |                       +--> Independent Recorder -> HDD pool
       |                                                  |
       +--> Metadata/Event API --> PostgreSQL indexes <-- Recording Catalog
                                      |
                 Auth+Policy+Audit ---+--- Incident/Evidence/Export API
                                      |
                                 GARDA Web UI

Future T2: substreams -> detector worker -> normalized events -> approved rules
Future T3: governed recognition/semantic index -> investigation APIs
Future T4: Unit SiteConnector <-> Federation Gateway <-> Hierarchy/Policy/Classification
           -> Command COP + Integration Hub (GIS, AC, radio, alarm, IoT, SIEM ...)
```

Design constraints:
- Site-local recorder is independent from HQ availability, AI uptime, model updates and external connector failures.
- Enforce authorization on media, preview, export, metrics, search, sockets, analytics and object store; UI-only gating is insufficient.
- Separate workloads for recorder/media decode, web API, DB, AI, Vault and optional Windows user VM.
- Use stable IDs for `organization_id`, `unit_id`, `site_id`, `zone_id`, `camera_id`, `recording_id`, `event_id`, `incident_id` and `evidence_id`.
- Prefer PostgreSQL transactional metadata and indexed segment locations, media file/object storage outside SQL.
- Streaming technology candidates include go2rtc/MediaMTX/FFmpeg; NVR candidates include Frigate where licensing/configuration fits. Selection requires benchmark and license review, not asserted as final.

## 5. High-tier structure: hierarchical multi-tier Command Center
**Owner decision**: Full highest tier combines management of all Tier1/2/3/4 sites, under hierarchical organizational commands. Data and live camera access do **not** automatically inherit from higher rank. Command scope must be explicitly assigned and audited.

### Federation components (T4 candidates)
- `OrgDirectory`: configurable tree (illustrative Mabes > Kotama > Satker > Site) and command relationships.
- `SiteConnector`: compatible with Basic, Smart, Intelligence and Sovereign nodes using one versioned federation protocol and declared capabilities.
- `AssetDirectory`: federated camera/site health and metadata as allowed by policy.
- `PolicyDecisionService`: RBAC + ABAC plus classification + tenant/site scoping, deny-by-default, ownership and need-to-know.
- `AccessGrantService`: exceptional requests + time-limited special code as second authorization artifact; named approving authorities, dual control, MFA, expiry/revoke, full audit and approval reason.
- `ClassificationService`: labels `Biasa`, `Terbatas`, `Rahasia` (taxonomy TBD), marking, inheritance, export, redaction and classified storage boundaries.
- `CommandCOP`: Common Operating Picture with high-level summaries from authorized sites and optional policy-gated live detail.
- `IntegrationHub`: standardized sensor and software adapters, bidirectional controls only with safe approvals.

### Cross-unit grant example (proposed)
1. Unit A requests to view specified Unit B cameras due to an incident; provides case number, justification, actions, requested window.
2. Unit B asset owner and designated command approver validate; for sensitive assets require two-person approval/MFA and applicable clearance.
3. System issues single-use/short-duration proof/code that is bound to named user, camera list, permitted operations, purpose, expiry and device/session.
4. Backend checks user rights, unit ownership, classification and grant at every stream/open/export action.
5. Visible banner/watermark and audit event track use; owning unit can revoke instantly. Copying code cannot grant a new user access.
6. When disconnected, denied by default except specifically approved and locally enforceable emergency policy.

## 6. TNI/government data classification design (Tier4)
Classification examples requested by owner: `Biasa / Terbatas / Rahasia`; official vocabulary and whether further levels are required: OPEN. Applies to site/camera/video/event/evidence/incident/AI derived data and exports.
- Clearance **and** need-to-know, not rank alone; owners and policy enforcement always active.
- Inherited sensitivity labels for derived frames, AI results, thumbnails and exports; no silent declassification.
- Secure storage domains/key management, watermark/anti-exfiltration mechanisms where validated.
- Mask/withhold aggregates where they could indirectly reveal classified operations.
- Retrieval, copying, sharing and export must be classification-aware and recorded.
- Newer customer security policy may require offline/air-gapped environments and formal certification; do not claim compliance without assessment.

## 7. Interoperability and smart system platform
Interfaces to plan, not all in Tier1:
- **Video**: ONVIF/RTSP, ONVIF Profile T preferred, metadata Profile M when supported, H.264/H.265, vendor adapters and honest per-feature probing.
- **Alarm/security**: fire/security alarms, access control and visitor management, perimeter sensor, LPR barrier, intercom/PA.
- **IoT**: MQTT/HTTP gateways, door sensors, UPS, environmental, thermal.
- **Operations**: GIS, dispatch/radio, ticketing/ERP, government-approved systems, SIEM/SOC, secured data export.
- **Advanced feed**: radar, drone/UAS, thermal-optical and body-worn streams subject to authorization.
- **Platform**: REST/open API + webhooks + versioned plugin adapter SDK + event bus + OAuth2/mTLS-style connector auth options + rate limits + per-site secrets and revocation.
- Mapping to human actionable SOP: event -> verification -> priority -> assigned team -> approved response -> acknowledgement -> evidence -> incident resolution.
- Emergency/physical actions MUST have explicit authorization, deterministic safety limits, dry-run and rollback where possible. LLM output never directly unlocks a door or activates a relay.

## 8. Privacy, AI quality and safeguards
- Only legitimate/authorized biometric cases. Face identification and ANPR are fallible candidates and always preserve confidence + raw evidence + operator verification before adverse decisions.
- Anti-bias/quality monitoring, documented intended use, operator recourse, false-positive handling, retention and deletion control.
- Sensitive searches and recognition access logged at higher assurance.
- Data minimization; avoid putting production footage or classified site configuration in public model endpoints or external AI services.

## 9. IP and customer source delivery
**Owner decision**: Never provide complete proprietary GARDA backend or AI source to the customer. Separate a **viewer/basic-client** distribution with contractual license and approve a precise file allowlist for delivery. Even minified frontend code is visible and must not contain secrets, authorization decisions, algorithms or private integration endpoints. All core policy/entitlements reside on controlled backend nodes. Only explicitly permitted artifacts are exported. Software IP/patentability/third-party license and public-procurement commitments need legal counsel review; no patent claim before protection is actually secured.

## 10. Hardware and deployment assumptions
Current procurement plan: Threadripper 1950X + X399 platform, 128 GB DDR4 **UDIMM**, up to 4 GPUs (model/PSU/cooling pending), Linux on-prem 24/7, CCTV HDD pool, UPS, segregated PoE network, VPN. This is a **proposed build**, not validated mission-critical enterprise sizing.
- CPU/PCIe, NVENC/NVDEC sessions, network bitrate, RAID/write performance, 4 GPU lane topology and airflow must be benchmarked.
- Never allocate game/editing Windows VM to the same GPU/IO budget as camera recording without reserved resources and explicit failure testing.
- Some prospective TNI environments may require high-availability server-grade hardware, ECC, hot-swap drives, redundant PSU, signed firmware and certification; the cost-optimized X399 workstation is not automatically compliant.
- Recording storage planning formula: cameras * average Mbps * 86400 seconds/day * retention days / 8, plus filesystem/redundancy and safety margin; calculate exact requirement after camera counts/bitrates and retention are confirmed.
- No statement that 4 GPUs or 128 GB automatically support a specific channel count.

## 11. Non-functional requirements and validation
- 24/7 local record/monitor principle; measured SLO/Tier-by-tier SLA pending.
- Threat model for camera streams, leaked signed URLs, RBAC bypass, stolen code/grants, insider exports, compromised sensor integrations and site-to-hub impersonation.
- Continuous audit with synchronized timestamps and integrity protection.
- HA/DR only when contracted; document RPO/RTO after measurement.
- Test transport loss, stream recovery, NVR disk full, corrupt segment, one camera bad, offline license and clock drift.
- Load test actual cameras in expected codecs/fps/bitrate and realistic concurrent viewers; keep evidence of benchmarks.
- Evaluate accessibility, shift operator ergonomics, site-specific language and screen-size constraints.

## 12. KAK alignment and implementation tracking
Future traceability table to populate, never fill with invented requirements:
| Feature ID | Tier | KAK clause | Acceptance test | Security/clearance | Owner sign-off | Implementation PR | Test evidence |
|---|---|---|---|---|---|---|---|
| VID-TBD | T1 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |

### Immediately outstanding product questions
1. Cameras, sites, brands, DVR/NVR retained vs replaced; storage retention and quality.
2. Basic AI inclusion, ANPR early demand and biometrics tier.
3. Number of operators, live viewers and command hierarchies in initial phase.
4. Exact offline, air-gap, encrypted backup and compliance needs.
5. Mobile in Basic, Vault in Basic vs add-on.
6. Export format/legal evidence requirements, classification official policy and approval authority.
7. SLA/RPO/RTO, licensing model and offline entitlement limits.
8. UI languages, source handover contractual wording and legal IP protection approach.

### Decision milestones
M0: owner inputs + KAK mapping -> M1: Basic scope and hardware sign-off -> M2: subsystem proof of concept & camera interoperability -> M3: Basic production iteration + security tests -> M4: operational acceptance -> M5: separately contracted Tier 2/3 upgrades -> M6: Tier4 federation/command platform.
