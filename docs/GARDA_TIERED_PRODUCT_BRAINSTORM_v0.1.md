# GARDA — Tiered Product Strategy & Brainstorm Baseline v0.1

Status: Brainstorming baseline, not yet KAK-aligned.
Primary target: Indonesian government institutions, especially TNI.
Repository rule: Product decisions, PRD changes, tier definitions, architecture and roadmap are versioned in GitHub.

## Product Strategy

GARDA will be packaged into 4 cumulative tiers. Each higher tier contains the capabilities of the lower tier plus additional modules.

### Tier 1 — BASIC / Core Monitoring
Contract-entry tier. Objective: reliable monitoring, recording, evidence retrieval, device health, access control and incident handling without making the first deployment dependent on heavy AI infrastructure.

Candidate scope:
- Multi-vendor IP camera ingest
- ONVIF Profile T preferred; RTSP fallback
- H.264/H.265
- Camera discovery/onboarding
- Live wall: 1/4/9/16/25/custom layouts
- Multi-monitor / video-wall ready operator UI
- Main/sub stream selection
- PTZ control where supported
- Snapshot and manual recording
- 24/7 recording
- Configurable retention
- Recording calendar
- Playback timeline
- Multi-camera synchronized playback
- Event bookmarks
- Clip/snapshot export
- Basic motion events
- Camera tamper/offline/stream-failure alerts
- Device inventory
- Camera/server/storage/UPS/network health
- Storage capacity and retention estimation
- User management
- RBAC
- MFA-ready authentication
- Operator/supervisor/admin/auditor roles
- Audit trail for login, playback, export and configuration changes
- Incident register and basic case workflow
- Evidence attachment to incident
- Evidence package with checksums
- Site/floor map with camera pins
- Operator acknowledgement and escalation
- Shift notes / handover log
- Basic dashboards and reports
- Local-first operation
- Backup/restore
- VLAN/VPN-oriented deployment
- No direct public camera exposure
- API/webhook foundation for future tiers
- Indonesian localization
- Time synchronization and timestamp integrity
- Maintenance mode and camera maintenance history

Basic should deliberately exclude:
- Production face recognition
- Production ANPR/LPR
- Cross-camera person re-identification
- Behavioral AI
- VLM/LLM autonomous conclusions
- Automatic physical access actuation
- Digital twin / 3D tracking
These remain upgrade differentiators.

### Tier 2 — SMART / Video Analytics
Everything in Tier 1 plus operational computer vision.

Candidate capabilities:
- Person/vehicle/object detection
- Zone intrusion
- Line crossing
- Loitering/dwell
- Direction/wrong-way detection
- Object left/removed
- Crowd density and people counting
- Queue analytics
- PPE / uniform / configurable visual-class analytics where applicable
- Fire/smoke visual detection as assisted alert, subject to validation
- Advanced camera health: blur, covered lens, frozen image, view shift, extreme brightness/darkness
- ONVIF Profile M metadata/event integration
- Rules engine
- Scheduled and conditional alert rules
- Notification routing
- Event prioritization and suppression
- Analytics dashboards
- False-positive feedback loop
- Alert SLA / response-time tracking
- Edge AI or central GPU inference options
- Thermal camera integration when supported
- Sensor/IoT event ingestion foundation

### Tier 3 — INTELLIGENCE / Recognition & Investigation
Everything in Tier 2 plus identity/vehicle intelligence and investigation tooling.

Candidate capabilities:
- Face recognition for authorized use cases
- Known/unknown person directory
- Watchlists with controlled permissions
- ANPR/LPR
- Vehicle whitelist/watchlist
- Vehicle attributes
- Face/plate confidence and manual verification
- Entity timeline
- Cross-camera search
- Appearance search
- Person/vehicle re-identification
- Journey reconstruction
- Semantic video/event search
- Ask GARDA natural-language investigation
- AI-generated incident/shift summaries clearly marked as AI output
- Evidence-linked answers
- Advanced case management
- Chain-of-custody metadata
- Saved searches
- Investigation workspace
- Multi-site federation
- Central command dashboard across sites
- GIS integration
- Access-control integration
- Visitor/vehicle correlation
- IoT/sensor correlation
- Mobile supervisor/investigator application
- Secure remote live/playback subject to RBAC

### Tier 4 — SOVEREIGN COMMAND / Advanced Command Center
Everything in Tier 3 plus flagship, high-availability and multi-domain command capabilities.

Candidate capabilities:
- Multi-site / regional federation at large scale
- Active-active / HA control plane options
- Disaster recovery site
- Edge-cluster orchestration
- AI model registry and governed deployment
- VLM-assisted alert verification
- Natural-language rule authoring with human approval
- Cross-camera global entity graph
- Multi-camera tracking
- Digital twin / calibrated world-coordinate tracking
- 2D/3D operational map
- Radar integration
- Thermal + visible fusion
- Drone/UAS video ingest and map correlation where authorized
- Body-worn/mobile camera ingest where authorized
- Perimeter sensor integration
- Access control, alarms, intercom and PA integration
- Emergency/SOP orchestration
- Operator dispatch workflows
- Command escalation tree
- Mass-notification integrations
- Offline/degraded-mode command workflows
- Executive common operating picture
- Predictive capacity and maintenance analytics
- Evidence media signing / stronger authenticity controls as standards and devices permit
- Sovereign/private-cloud deployment patterns
- Air-gapped / disconnected deployment option
- Hardware security module / key-management integration option
- SIEM/SOC integration
- Zero-trust identity and device posture integration
- API/SDK ecosystem
- Multi-tenant or multi-command structure if governance requires
- Fine-grained data-domain segregation
- Data diode / controlled export patterns where required

## Standards & Architecture Guardrails

- Prefer ONVIF Profile T over new Profile S-only deployments.
- Plan for ONVIF Profile M for analytics metadata/events.
- Preserve RTSP interoperability as fallback.
- Keep vendor-specific adapters isolated from core domain logic.
- Local recording must continue during WAN loss.
- AI must never be the sole source of evidentiary truth.
- Every material alert should retain source camera/time/evidence linkage.
- Critical automation requires policy, deterministic constraints and human authorization.
- Architecture must support on-premise and private-cloud patterns.
- All biometric and sensitive searches require explicit RBAC and auditable access.
- Security controls are product features, not deployment afterthoughts.

## Government/TNI-Specific Product Considerations

To be resolved before KAK lock:
- Data classification levels
- Whether the system must be fully on-premise or may use a government/private cloud
- Air-gap or disconnected operation requirements
- Inter-unit/site federation rules
- Biometric policy
- Data residency
- Retention periods by camera/event/classification
- Evidence admissibility / chain-of-custody requirements
- Encryption and key ownership
- Operator clearance mapping
- Integration with existing NVR/VMS/cameras
- Integration with command center, access control, GIS, radio/dispatch, SIEM
- Availability/SLA targets
- DR/RPO/RTO
- Cybersecurity assessment / hardening standards
- Procurement preferences for open standards and vendor independence

## Brainstorm Feature Universe

Feature domains to keep expanding:
1. Video ingestion & interoperability
2. Recording & retention
3. Live monitoring & video walls
4. Playback & forensic search
5. AI detection
6. Recognition
7. Cross-camera intelligence
8. Incident/case management
9. Evidence integrity
10. Maps/GIS/digital twin
11. Sensor/IoT integration
12. Access-control integration
13. Drone/mobile/thermal/radar integration
14. Operator collaboration & shift handover
15. Notifications & dispatch
16. Reporting & executive dashboards
17. Device & infrastructure health
18. Storage/private cloud
19. Cybersecurity
20. Identity/RBAC/audit
21. HA/DR/resilience
22. API/SDK/integrations
23. Mobile applications
24. AI copilot & semantic search
25. AI governance/model governance
26. Data governance/privacy/retention
27. Multi-site federation
28. Maintenance/asset lifecycle
29. Configuration/change management
30. SOP/workflow automation

## Open Questions for Product Owner

1. Tier 1 first contract: how many cameras and how many physical sites must be supported?
2. Must existing DVR/NVR remain in use, or may GARDA replace recording?
3. Are camera brands/models already known?
4. Required retention: 7/14/30/60/90 days or other?
5. Is Tier 1 allowed to include basic AI such as person/vehicle detection, or should Tier 1 be intentionally AI-light?
6. Is face recognition allowed by policy, and if yes from which tier?
7. Is ANPR a mandatory early requirement?
8. Does the customer require fully offline/on-premise operation?
9. Does any site require air-gap or no Internet access?
10. Required operator count and simultaneous viewers?
11. Is there a central HQ command center federating multiple units/sites?
12. Must GARDA integrate existing access control, alarms, IoT, GIS, radio/dispatch, or SIEM?
13. Is mobile Android/iOS required in the first contract?
14. Is GARDA Vault/private cloud still part of the product contract, or should it be a separate optional module?
15. Required evidence export format and legal/audit requirements?
16. Desired SLA, HA, RPO, and RTO?
17. Should tiers be sold by feature set only, or feature set plus camera/site limits?
18. Do we need licensing to work completely offline?
19. Who is authorized to create watchlists, export video and search biometrics?
20. Should the UI and documentation use only Indonesian, or bilingual Indonesian/English?

## Proposed next step

After product-owner answers, convert this baseline into:
- PRD v1.0
- Feature matrix Tier 1–4
- Tier 1 acceptance criteria
- KAK traceability matrix
- Architecture per tier
- Hardware sizing assumptions
- Security baseline
- Delivery roadmap and upgrade path
