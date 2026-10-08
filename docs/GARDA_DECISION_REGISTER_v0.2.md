> **ARCHIVED BASELINE NOTICE (2026-10-08):** This file is retained for history or demo only. New authoritative docs are [Decision Register v0.3](GARDA_DECISION_REGISTER_v0.3.md), [Basic PRD v1.0](GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md), [Catalog v0.3](GARDA_MASTER_FEATURE_CATALOG_v0.3.md), and [PUSADA KAK Gap Matrix](GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md). Owner now includes Basic person/face-presence/ANPR Lite; face *identity* starts T2; Base recording retention 7d while PUSADA KAK separately requires 90d. Do not use older T1/T2/T3 constraints as current truth.\n\n# GARDA — Product Owner Decision Register v0.2
Updated: 2026-10-08 | Status: **brainstorm accepted inputs**, not final KAK or procurement acceptance.
Owner: GARDA / PUSADA MONITORING CENTER; primary clients Indonesian government including TNI.
Repository: `adith92/GardaWEB` (PRIVATE).

## Precedence and decision statuses
- **DECIDED** = explicit product-owner intent, subject to law, contracting and security assessment.
- **PROPOSED** = architect/PM recommendation; must not be silently turned into contract deliverable.
- **OPEN** = requires confirmation and KAK mapping.
- Newer explicit owner decisions supersede older illustrative demo docs. `PRD_PMC_GARDA.md` and `CODEX_MASTER_PROMPT_PMC_GARDA.md` were initially **demo** specifications, **not** current production deployment promises.
- Nothing here grants Codex permission to deploy, disclose source, connect actual government networks, process real biometric data, or commit secrets.

## Decided: product strategy and customer
| ID | Status | Decision | Consequence |
|---|---|---|---|
| D-001 | DECIDED | Four **cumulative** tiers. | Higher tier includes the contracted modules of lower tiers, subject to per-installation licensing and site permissions. |
| D-002 | DECIDED | Initial contract is **Tier 1 Basic**; Tier 2/3/4 are future contract upgrades. | Product catalog can be broad; Basic delivery scope must remain finite and testable. |
| D-003 | DECIDED | Government/TNI is the primary customer domain. | On-premise, operational audit, security and mission continuity are first-class requirements. |
| D-004 | DECIDED | All feature discussions, decisions, architecture, PRD and roadmap should be versioned in GitHub for Codex. | Use this private repository as the development knowledge base. |
| D-005 | DECIDED | At the **highest tier**, a higher-order Command Center combines and coordinates subordinate GARDA deployments from all tiers. | Plan federated hierarchy, cross-tier interoperability, delegation and central operational view/control. No implicit omnipotent access. |
| D-006 | DECIDED | Inter-unit camera visibility is **DENY by default**; no unit may see another unit's feeds without an authorized special grant. | Implement server-side tenant/organizational isolation and policy checks across live, playback, exports, events, maps, search and APIs. |
| D-007 | DECIDED | Exceptional cross-unit viewing requires a **special code/authorization**. | Implement as short-lived scoped, auditable access grant workflow, *not* a reusable bypass code. |
| D-008 | DECIDED | Highest tier presents **data classification** and classification-aware authorization. | Model classifications, clearance, compartments, ownership, purpose and export constraints. |
| D-009 | DECIDED | GARDA should connect to GIS, access control, radio/dispatch, alarms, IoT, SIEM and diverse external software; target is an integrated smart system. | Build integration framework, adapters, event bus, catalog and secure bidirectional actions where permitted. |
| D-010 | DECIDED | **Do not deliver complete/proprietary backend or AI source to client**. Any source distribution is limited to approved viewing/basic client-side functionality. | Separate distributable viewer code from private server-side code, license boundaries and trade-secret/IP handling. |
| D-011 | DECIDED | Owner intends to pursue IP protection/patent strategy. | Document inventions, authorship, dependencies and legal review; patent registration/protection is NOT automatic. |
| D-012 | DECIDED | Hardware direction evolved to custom Threadripper platform, 128 GB RAM, up to four GPUs and Linux 24/7 core; Windows for optional remote workloads. | Capacity design must be benchmarked and physically validated. Older R630 is legacy proposal, not current selected direction. |

## Proposed: tier names and scope boundaries
- Tier 1 **GARDA BASIC**: dependable VMS/NVR, live, playback, evidence, incident operations, telemetry, RBAC, audit, on-premise resilience, foundational integration API.
- Tier 2 **GARDA SMART**: computer vision / spatial object analytics, analytics rules, alert routing, IoT event foundation.
- Tier 3 **GARDA INTELLIGENCE**: tightly-governed face and license plate recognition, entity/cross-camera investigation, semantic search and intelligence.
- Tier 4 **GARDA SOVEREIGN COMMAND**: top command center/federation, multi-unit hierarchy, data classification, central orchestration, multi-domain sensor integration, digital twin and enterprise resilience.
- Name, quotas, acceptance and licensing remain **PROPOSED** until commercial/KAK lock. See `GARDA_MASTER_FEATURE_CATALOG_v0.2.md` for individual minimum-tier suggestions.

## Hierarchy and isolation policy (implementation intent)
Proposed hierarchy: `National/Top HQ (if approved) > Mabes > Kotama > Satker > Site > Zone > Camera`.
These names are **illustrative**, not a canonical TNI command structure; allow configurable org trees, alias labels and changes without data migration.
- Every principal and asset has organization ownership and scope. Enforce both hierarchical **RBAC** and contextual **ABAC** (clearance, classification, purpose, time, unit, device posture, case).
- Deny by default. A superior organizational position **does not by itself override** camera classification or owning-unit restrictions.
- No inherited right to another unit's streams, recordings, biometrics, incident evidence or exports merely because a central dashboard can display aggregate counts.
- Tier 4 HQ federates Tier 1/2/3/4 nodes via local site connectors, metadata/event sync and **policy-gated** approved live/control sessions. Lower-tier nodes stay operable offline and enforce local policy.
- Central dashboard may receive aggregated non-sensitive operational health by policy while content remains segregated.
- Exceptional cross-unit grant flow proposal: named requestor + reason/ticket + resource/camera IDs + intended actions + expiry + owner/command approval (two-person control for classified assets) + MFA + **single-use short-lived code or signed token** + server-side verification + immediate revoke + searchable immutable audit + recording/watermark/alert of sensitive viewing where approved. Never store a code in source control. A code by itself is insufficient.
- Emergency/break-glass must be separately approved in policy, time-limited, recorded, post-reviewed and never circumvent higher classification restrictions or applicable law.
- A tenant/organization `id` must be enforced at data/query/stream authorization layers, not merely hidden UI navigation.

## Classification (Tier 4 advanced)
- Requested examples from owner: **Biasa**, **Terbatas**, **Rahasia**. Precise government classification taxonomy, mappings and any **Sangat Rahasia** level require customer policy confirmation.
- Proposed labels on assets, camera feeds, sites, recordings, snapshots, incidents, people/vehicle records, AI output, exported files and derivative summaries.
- Rules: no automatic downgrade, default highest applicable inherited classification, clearance plus need-to-know required, classification-aware search and export, separate storage/key domains where required, downgrade via dual approval if permitted, watermark/redaction and exhaustive audit.
- Classifications are policy metadata and enforcement controls; UI badges alone do not provide protection.

## Integration and smart-command platform architecture (proposed)
- Southbound camera standard adapters (ONVIF/RTSP), access-control connectors, alarms, intercom/PA, fire safety, perimeter, sensors, thermal, CCTV DVR/NVR, drones/bodycam/radar only when authorized.
- Northbound GIS, radio/dispatch, SIEM/SOC, ERP/asset management, dashboard, ticketing, document systems, authorized government APIs, webhooks, SDK and secure exports.
- Adapter/plugin SDK; capability discovery; per-site credentials vaulted, per-integration scopes, mutual TLS when feasible, event bus + normalized event envelope, retries/dead-letter queue, idempotency, observability and versioned schemas.
- Commands affecting physical access, alarms, public messaging or security must use explicit human approval/safety interlocks; do not allow LLM to actuate directly.
- Integrations must support offline queues and site-local autonomy, and respect inter-unit/classification boundaries.

## Intellectual property and source distribution policy
- **PRIVATE by default**: GARDA core backend, inference pipeline, model training/tuning, orchestration, secret configs, infrastructure code, internal adapters, licensing, proprietary algorithms and full repositories.
- **Potentially deliverable only after explicit owner-approved contract/legal/security review**: separate viewer/basic client source, UI components, documented client SDK, integration API specification, compiled clients, non-sensitive example configurations and permitted docs.
- Viewer/frontend source (and any browser-delivered JavaScript) is inspectable by recipients. **Never rely on hiding UI source to protect authorization**; all policies must be enforced server-side.
- Separate `viewer-sdk`/distribution package from private `core`; consider separate customer-facing repository/package with explicit release allowlist and automated leak/license scan.
- Source distribution requires third-party license and dependency review, copyright/trademark/trade-secret strategy, contract ownership/licenses, patentability assessment by qualified Indonesia IP counsel. **Calling software 'patented' or assuming software patents automatically protect it is prohibited.**
- Never hand over proprietary source to counterparties through GitHub collaborator invitation as a shortcut.

## Current technical baseline and historical changes
- Linux/Ubuntu Server LTS 24/7, ONVIF + RTSP, recording original source independently of AI processing, main/substream strategy, no direct camera internet exposure.
- Camera procurement: verify true 802.3af/at PoE and vendor/model ONVIF capabilities rather than trust marketplace claims.
- Most recent hardware shortlist (2026-10-07): Threadripper 1950X, X399 AORUS PRO, 128 GB compatible **UDIMM** DDR4 (NOT RDIMM), four-GPU expansion **target** (GPU exact models pending), Phanteks Enthoo Pro II Server Edition, disk pool initially six HDD **candidate**. This is procurement planning, not a confirmed deployed/benchmarked server. See `docs/project-garda/GARDA_HARDWARE_PROCUREMENT_2026-10-07.md`.
- Optional Windows remote work/gaming/media workloads **must be isolated** (VM/dedicated GPU/host) and never starve CCTV recording or command services. GPU switching is not automatically assumed to be live, transparent or universally supported.
- Earlier `PRD_PMC_GARDA.md` assumed R630 + optional inference server for a frontend demo. That phase architecture is superseded by the latest hardware plan for procurement discussions. Keep demo historical docs intact.

## Still open from questions 1–20 (must NOT invent answers)
Camera/site quantities, existing DVR/NVR takeover policy, brands/models, retention days, whether Basic includes general AI, early ANPR, face tier confirmation, exact offline/air-gap requirements, concurrent operators, central site requirements by phase, mobile timing, GARDA Vault Basic vs add-on, evidence formats, availability SLA/RTO/RPO, pricing by camera/site vs features, offline licensing, authorized exporter/watchlist roles, Indonesian-only vs bilingual UI.

## Risks and approval gates
- Biometric tracking and watchlists require legal authority, documented purpose, accuracy and bias evaluation, oversight, retention/deletion rights and human review of matches. Never label a match or anomaly as conclusive proof.
- TNI/government classification, local cybersecurity and procurement requirements must be validated against the actual customer's KAK and policies.
- No actual camera connectivity, live biometric enrollment, access actuation or cross-organization sharing until written authorized scope and acceptance criteria.
- Changes to DECIDED items require a new dated Decision Register entry rather than silently rewriting history.

## Source links
- `docs/GARDA_TIERED_PRODUCT_BRAINSTORM_v0.1.md`
- `PRD_PMC_GARDA.md` (original demo PRD)
- `docs/project-garda/GARDA_CCTV_AI_MASTER_CONTEXT.md`
- `docs/project-garda/GARDA_HARDWARE_PROCUREMENT_2026-10-07.md`
