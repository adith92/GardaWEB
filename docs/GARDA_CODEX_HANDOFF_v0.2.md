> **ARCHIVED BASELINE NOTICE (2026-10-08):** This file is retained for history or demo only. New authoritative docs are [Decision Register v0.3](docs/GARDA_DECISION_REGISTER_v0.3.md), [Basic PRD v1.0](docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md), [Catalog v0.3](docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md), and [PUSADA KAK Gap Matrix](docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md). Owner now includes Basic person/face-presence/ANPR Lite; face *identity* starts T2; Base recording retention 7d while PUSADA KAK separately requires 90d. Do not use older T1/T2/T3 constraints as current truth.\n\n# GARDA — Codex Handoff & Implementation Workflow v0.2
Updated: 2026-10-08 | Audience: Codex implementation team.

## Product-owner brief
GARDA / PUSADA MONITORING CENTER is a private, on-prem-first government/TNI video monitoring and security operations platform. There are four cumulative commercial tiers. The **first contract builds Tier 1 Basic only**, while **the full feature universe** is maintained as a roadmap. The top-tier Command Center unifies independent site/unit deployments, integrates other software/sensors and enforces command hierarchy, classification and exceptional audited cross-unit grants.

## Codex bootstrap
Read `AGENTS.md`, then `docs/GARDA_DECISION_REGISTER_v0.2.md`, `docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md`, `docs/GARDA_TIER_IMPLEMENTATION_SPEC_v0.2.md`, and the current demo README before altering code. Do not start building the full feature catalog. Verify the frontend baseline separately from production backend requirements. **Do not invent answers to the open owner questions.**

## Tier contract guardrails
| Tier | Build authority today | Objective |
|---|---|---|
| 1 BASIC | Candidate initial implementation after KAK scope lock | NVR/VMS reliability, incident/evidence/audit |
| 2 SMART | Roadmap only | AI video events, rules, analytics |
| 3 INTELLIGENCE | Roadmap only | Governed recognition and investigation |
| 4 SOVEREIGN COMMAND | Roadmap only | Hierarchical full command hub, classification, integrated smart system |

### Feature status language
- `DRAFT`: idea listed and tier suggested
- `APPROVED`: owner + KAK included and acceptance defined
- `IN_PROGRESS`: code being developed
- `DEMO_ONLY`: simulated UI without real security semantics
- `IMPLEMENTED`: implemented, not necessarily tested in production
- `TESTED`: automated + hardware validation performed, evidence linked
- `ACCEPTED`: formally signed-off under contract

Never infer `APPROVED` or `ACCEPTED` from being in a document.

## Practical backlog in recommended order (Tier 1)
1. Repository quality gate: environment sample without credentials, typed configs, CI lints/test/build, safe defaults, test fixtures.
2. Organizational model (even if only one site initially): `organization / unit / site / zone / device` IDs, ownership tags, deny-by-default role policy, user/membership/session/service account.
3. Auth + policy API + audit service: identity, MFA-ready configuration, export permission, last-access records, immutable/tamper-evident audit plan.
4. Camera discovery/register & capability probe: ONVIF/RTSP credentials in vault, codec/media profiles, PTZ support probing, offline status.
5. Reliable ingest/record: main stream continuous capture, rolling segments, checksums and retention, substream fallback, loss/reconnect and clock normalization. Original recording independent of AI.
6. Live wall + stream access service: time-limited signed media authorization, layout and low-latency browser fallback, stream isolation tests.
7. Playback/search by camera and timestamp; export snapshots/video with watermark and hash manifest.
8. Device & system health: server, disk SMART/capacity, camera uptime/frame loss, UPS and storage alarms.
9. Incident workflow: create, assign, acknowledge, notes, attach evidence, resolve, basic shift handover and reports.
10. Recovery drills: backup/restore, offline operation, retention pruning, user revocation, evidence package verification.
11. Customer KAK traceability and measured scale testing with real camera compatibility matrix.

## Deliverables to attach per feature
- Unique `VID-nnn` ID linked to issue and PR.
- Scope statement, minimum tier, role/permission policy, API/UI/backend boundary.
- Threat/privacy assessment where relevant.
- Test plan: unit, integration, role isolation, reconnect, retention, export integrity and usability.
- User-facing docs, admin runbook, migration and rollback plan.
- Recorded support matrix of exact device firmware, PTZ/audio, ONVIF profile and protocol capabilities.
- Do not claim a physical integration works until hardware tests prove it.

## Sensitive design constraints
### Cross-unit special code
This is NOT a backdoor. Build `AccessGrantRequest` and `AccessGrant` model with requester, target asset scope, actions, reason, case/ticket, owning-unit approval, command approval when required, MFA confirmation, one-time or bounded credential, expiry, revoke and immutable audit. Gate media and evidence APIs on effective policy and grant. Design in Basic for isolation, but **cross-unit grant orchestration is not a Basic delivery claim**.

### HQ hierarchy and Tier 4 command
Tier 4 aggregates local nodes from any tier via versioned `SiteConnector`, `OrganizationDirectory`, `FederationGateway`, `PolicyDecisionService`, `CommandWorkflow` and `IntegrationHub`. Site nodes stay autonomous. HQ receives only permitted summaries and approved content; a superior user does not bypass ownership/classification.

### Client deliverable source
Distribute only owner-approved `viewer/basic-client` source or source package built from allowlisted files. Exclude core backend, inference pipeline, server config, secrets and proprietary algorithms. Guard licensing/authorization in backend, not UI. The current repository remains PRIVATE. IP/legal protection strategy needs qualified counsel.

### On-prem hardware
Use newest procurement context: Threadripper 1950X/X399/128GB compatible UDIMM, up-to-four GPU objective, rack/storage and Linux server. Validate drive counts, video write throughput, network, decode sessions, PCIe spacing, PSU, cooling and 24/7 reliability. Avoid coupling NVR recording to Windows GPU workloads. No guaranteed camera count before benchmarks.

## Definition of done for initial Tier 1
- Multiple real ONVIF/RTSP camera models monitored and recorded without proprietary lock-in, exact models documented.
- Stream drop/recovery doesn't lose unrelated camera recording; offline WAN doesn't interrupt local operations.
- Every live/playback/media/export path enforces organizational ownership and RBAC with negative tests.
- Playback timeline and evidence export are verified from actual retained recordings, with hash manifests and accurate timestamps.
- Incident life-cycle and audit events work end-to-end.
- Restore and storage-full/failure drills recorded with results; retention measurable.
- Performance/availability only claimed after benchmark vs accepted KAK; never from fabricated default fixtures.

## Open questions for owner before contract lock
See Decision Register section `Still open from questions 1–20`. Codex may scaffold flexible options, but MUST NOT hardcode unconfirmed counts, classification schedules, biometrics use, customer infrastructure or SLA.

## Documentation discipline
- Every product discussion that changes a decision: append dated decision entry. Keep changelog.
- Every new proposed capability: allocate stable new VID and minimum tier; never reuse an ID.
- Link issues/PRs, tests and KAK clauses once available.
- Maintain a current `PRD`, `FEATURE_CATALOG`, `DECISION_REGISTER`, `KAK_TRACEABILITY` and `ARCHITECTURE_ADR` set as phase matures.
