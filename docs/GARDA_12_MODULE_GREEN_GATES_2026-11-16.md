# GARDA — 12-module GREEN gate and Codex handoff

**Branch:** `feat/incident-lifecycle-prod-gates-20261116`  
**Base:** `main` @ `4cfd013e60424e91e19cd12410928a1e7d4a60f7`  
**Status:** REVIEW / TEST REQUIRED. This is not a PUSADA acceptance, customer deployment or feature-tier approval.

## Change set delivered for code review

1. **Real incident API, not demo state:** `garda_ai/incidents.py` persists incident state to existing local SQLite WAL DB. Only `admin/operator` can create/list/inspect/acknowledge/resolve/add notes/link real events. Transitions are `open -> acknowledged -> resolved`; resolved incidents reject edits. An event belongs to no more than one incident. Linked evidence must belong to the incident's camera.
2. **Evidence inventory (not GARDA Vault):** `GET /api/v1/incidents/{id}/evidence-manifest` returns snapshot IDs, sizes and SHA-256 calculated from validated local snapshot paths. It deliberately advertises `legal_hold: false` and `signed_export: false`; no video recorder, vault storage, chain-of-custody certification or retention guarantee.
3. **Shared five-platform Workspace UI:** `/workspace` has a real **Insiden** view; **Kejadian -> Buat Insiden** uses the same secured API on Web, Electron and Android WebView. `/command` and other synthetic demo routes remain unchanged and must continue to be labeled as demo.
4. **Protected LAN launch profile:** `python -m garda_ai.server serve --protected` forces named login and rejects missing HTTPS origin or disabled Secure cookies. Existing `serve` default LAB-only admin bypass is preserved to honor the prior owner-specified lab workflow. **Protected is not production certification:** MFA, account lifecycle, secrets rotation and penetration testing remain outstanding.
5. **Automated negative tests** for anonymous/viewer access, CSRF, cross-origin request, incident transitions, duplicate evidence, camera mismatch, snapshot checksum, database reopen and protected launch preflight.

### Pilot command (controlled LAN only)

From `projects/garda/ai-core` after installing `requirements-unified.txt` and configuring a trusted HTTPS reverse proxy:

```sh
python -m garda_ai.server setup-user
export GARDA_PUBLIC_ORIGIN=https://garda.example.internal
export GARDA_COOKIE_SECURE=1
python -m garda_ai.server serve --protected
```

The example hostname **must** be replaced with the actual approved private origin. Keep the Python API bound to loopback and use `infra/unified/Caddyfile` after certificate trust has been configured. Never expose camera RTSP, vault, biometric API or server port directly to the internet.

**Regression checks for reviewer:**

```sh
PYTHONPATH=projects/garda/ai-core python -m pytest projects/garda/ai-core/tests -q
npm ci
npm run build
npm test
node --test desktop/policy.test.cjs
```

CI must run and pass at the PR head; do not infer success from the previous v0.13.0 release.

## GREEN gate matrix (source -> lab -> customer)

| Module | What this PR advances | Remaining to software GREEN | External/customer GREEN gate |
|---|---|---|---|
| Live CCTV Web | No streaming change | MediaMTX WebRTC/HLS secure media proxy, FPS/latency/reconnect metrics; reconcile PR #9 | 8+ camera sustained LAN run and physical cross-client testing |
| Recording 24/7 | No recorder merge | Review PR #9 MediaMTX recorder, persistence and crash recovery; retention/legal hold | measured storage, power/network interruption, NVR independence |
| Playback | Incident evidence links, not video playback | Authenticated recording timeline, seek, segment export and checksum | real camera archive navigation and multi-device verification |
| Person/face presence | Existing adapters unchanged | traceable event-level benchmarks, false-positive review | consent/authorization and approved dataset results |
| ANPR | Existing adapters unchanged | model provenance, Indonesian plates dataset + confidence review | day/night/angle/plate tests |
| Face recognition | Existing research only | Tier2/KAK authorization, role granularity, accuracy and retention | licensed models, access governance and site acceptance |
| PTZ | Existing experimental Android/PR #10 | ONVIF backend, capability probing, motion STOP failsafe | real firmware pan/tilt/zoom + interlock tests |
| Incident management | **Durable lifecycle, note, event link, audit, Workspace** | assignments/escalations, richer field validation, retention and reporting | onsite operator UAT + incident investigation drills |
| GARDA Vault | **Snapshot hash manifest ONLY** | vault permissions, legal hold, versioning, integrity checking and signed export | file recoverability and chain-of-custody acceptance |
| Android OTA | Existing signed v0.13.0 relay unchanged | verified rollback/update failure handling | install/update on Fold and Standard physical devices |
| Security/RBAC | **Protected-mode preflight + secured incident endpoints** | production default-deny profiles, MFA, session policy, pentest, cross-site tenancy, logs | network segmentation and identity policy testing |
| Backup/DR | Incident metadata lives in existing SQLite | quiesced encrypted backup + recovery tooling, key backup, restoration tests | offline restore drill on alternate hardware |

### Integration cautions for Codex

- **PR #9** is an unmerged recording foundation with its own Node/Fastify/PostgreSQL stack. **PR #10** is an unmerged Python vision/ClearCam bridge. Do not blindly merge either: choose one authoritative camera registry, identity/session model and recording path.
- The main GARDA unified API uses Python, the demo UI uses React and the Android/desktop clients display the same Workspace origin. The **incident API implemented here** intentionally reuses existing `EventStore` and authentication.
- An incident's attached event is an existing `events.id`, not a user-supplied uploaded video. No new biometric model weights or customer footage are stored in Git.
- Preserve `1–49 cameras / one site / one operational seat` as the Basic product scope. Hardware capacity is unmeasured; Basic has **face presence only**, face identity is Tier2 or separately contracted KAK functionality.
- PUSADA KAK has a separate 90-day retention requirement. The fixed delivery baseline is **8 weeks implementation + 2 weeks UAT/commissioning and 12 months support from BAST**.
- Do not mark individual modules GREEN without a passing named acceptance test and evidence. Do not merge a draft until CI, code review and environment testing are complete.

## Recommended follow-on PRs (non-overlapping)

1. **P0 streaming/recording**: decide on MediaMTX + recorder adapter from PR #9; implement TLS-proxied WebRTC, recording status, timeline and seek. Preserve independent NVR recording.
2. **P0 security**: formal production configuration schema, mandatory operator login for customer packaging, backend authorization of each video URL, MFA and security tests.
3. **P1 incident/evidence**: assignments, evidence legal hold, signed export, retention policy, isolated backup/restore.
4. **P1 AI/ONVIF**: licensed models, repeatable offline benchmarks, real PTZ feedback tests and no autonomous physical actuation.
5. **P1 five-client QA**: real device smoke tests for Windows 11, Apple Silicon macOS, Ubuntu, Android Fold/Standard and HTTPS Web.

**Audit vocabulary:** EXISTING / NEW IN PR / TESTED IN CI / REQUIRES LAB / REQUIRES CUSTOMER. No artificial green flags.
