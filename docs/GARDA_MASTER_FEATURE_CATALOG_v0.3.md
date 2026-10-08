# GARDA — MASTER FEATURE CATALOG v0.3 (Brainstorming / Candidate Universe)
Date: 2026-10-08 | Updated following owner Q1–20 | Owner: GARDA | Repo: `adith92/GardaWEB` (private)
State: **DRAFT / PROPOSED** except explicitly confirmed owner choices in `GARDA_DECISION_REGISTER_v0.2.md`.

> This is a **capability wishlist and tier proposal**, NOT a KAK, scope-of-work promise or a list of implemented features. Actual fulfillment depends on authorized use, exact camera/firmware compatibility, budget, testing, data governance and contract sign-off.

## Packaging semantics
- `T1` BASIC: NVR/VMS, operator work, incidents, evidence, operational security and observability.
- `T2` SMART: T1 + general AI video analytics, automation and early IoT.
- `T3` INTELLIGENCE: T1–2 + explicitly governed identity/vehicle recognition, investigations and semantic search.
- `T4` SOVEREIGN COMMAND: T1–3 + hierarchical unified command hub, data classification, federated cross-tier policy and multi-domain integrations.
- Minimum tier indicates **earliest commercial target**; does not mean the capability is implemented, licensed, legally authorized or available to every client.
- Source of truth for **owner-decided** items and risk flags: `docs/GARDA_DECISION_REGISTER_v0.3.md`. Individual tier allocations remain suggested until KAK review.
- Stable feature IDs `VID-nnn`. Never reuse or renumber after publication; append new capabilities only.

## Feature matrix (minimum tier)

| Feature ID | Min tier | Capability | Status |
|---|---|---|

**Feature-level interpretation overrides:** T1 face `VID-149` is **only face present/quality cue** (no face identity matching or biometric embedding enrollment); T1 ANPR `VID-167/169/170` is **simple plate OCR + evidence** only; T1 `VID-392` is limited evidence folder/file upload/download (no enterprise share); T1 `VID-494` bilingual UI (not all federated localization features); T3 `VID-500` means native mobile app (not a Tier2 app). See authoritative **Tier1 PRD v1.0 DRAFT** and Decision Register v0.3.

### 1. Camera discovery & multi-vendor ingest

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-001 | T1 | ONVIF LAN discovery | DRAFT |
| VID-002 | T1 | Manual RTSP camera registration | DRAFT |
| VID-003 | T1 | ONVIF capability probe | DRAFT |
| VID-004 | T1 | Media profile and stream URI selection | DRAFT |
| VID-005 | T1 | Camera credential vault reference | DRAFT |
| VID-006 | T1 | H.264/H.265 passthrough | DRAFT |
| VID-007 | T1 | Camera model/firmware inventory | DRAFT |
| VID-008 | T1 | Camera group/site assignment | DRAFT |
| VID-009 | T1 | Duplicate device detection | DRAFT |
| VID-010 | T1 | Import/export camera inventory | DRAFT |
| VID-011 | T2 | Automatic camera compatibility score | DRAFT |
| VID-012 | T2 | ONVIF Profile M metadata ingest | DRAFT |
| VID-013 | T2 | Batch adaptive stream enrollment | DRAFT |
| VID-014 | T3 | Cross-site unified camera discovery | DRAFT |
| VID-015 | T4 | Cross-tier remote site connector provisioning | DRAFT |
| VID-016 | T4 | Central capability/firmware matrix | DRAFT |

### 2. Video streaming and transport

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-017 | T1 | Main and substream support | DRAFT |
| VID-018 | T1 | Secure time-bound video URLs | DRAFT |
| VID-019 | T1 | WebRTC browser live | DRAFT |
| VID-020 | T1 | HLS fallback | DRAFT |
| VID-021 | T1 | RTSP restream gateway | DRAFT |
| VID-022 | T1 | Per-user concurrent session limits | DRAFT |
| VID-023 | T1 | Camera stream auto reconnect | DRAFT |
| VID-024 | T1 | Stream health counters | DRAFT |
| VID-025 | T1 | Audio monitoring if supported | DRAFT |
| VID-026 | T2 | Adaptive AI substream schedule | DRAFT |
| VID-027 | T2 | Smart transcoding priority | DRAFT |
| VID-028 | T2 | Intelligent quality downgrades | DRAFT |
| VID-029 | T3 | Inter-site proxy under delegated access | DRAFT |
| VID-030 | T4 | Federated media relay with classification policy | DRAFT |
| VID-031 | T4 | Bandwidth-aware regional relay | DRAFT |

### 3. Live monitoring and PTZ

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-032 | T1 | Single-camera view | DRAFT |
| VID-033 | T1 | 4-camera wall | DRAFT |
| VID-034 | T1 | 9-camera wall | DRAFT |
| VID-035 | T1 | 16-camera wall | DRAFT |
| VID-036 | T1 | 25-camera wall | DRAFT |
| VID-037 | T1 | Custom camera wall layouts | DRAFT |
| VID-038 | T1 | Multi-monitor and video wall ready | DRAFT |
| VID-039 | T1 | Camera drag and reorder | DRAFT |
| VID-040 | T1 | Digital zoom and screenshots | DRAFT |
| VID-041 | T1 | Fullscreen and pop-out views | DRAFT |
| VID-042 | T1 | PTZ directional control if supported | DRAFT |
| VID-043 | T1 | PTZ preset recall if supported | DRAFT |
| VID-044 | T1 | Live recording indicator | DRAFT |
| VID-045 | T1 | Operator camera favourites | DRAFT |
| VID-046 | T2 | AI visual overlay | DRAFT |
| VID-047 | T2 | Intelligent event tile spotlight | DRAFT |
| VID-048 | T2 | Auto-scan incident cameras | DRAFT |
| VID-049 | T3 | Re-ID cross-camera camera switching | DRAFT |
| VID-050 | T3 | Live identity and plate context drawer | DRAFT |
| VID-051 | T4 | Hierarchical wall delegation | DRAFT |
| VID-052 | T4 | National/regional Common Operating Picture | DRAFT |

### 4. Recording engine and retention

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-053 | T1 | 24x7 stream recording | DRAFT |
| VID-054 | T1 | Schedule-based recording | DRAFT |
| VID-055 | T1 | Event-triggered supplementary clips | DRAFT |
| VID-056 | T1 | Recorder independent of AI worker | DRAFT |
| VID-057 | T1 | Time-sliced original video segments | DRAFT |
| VID-058 | T1 | Recording file index | DRAFT |
| VID-059 | T1 | Per-camera retention policy | DRAFT |
| VID-060 | T1 | Disk space threshold alarm | DRAFT |
| VID-061 | T1 | Configurable overwrite after retention | DRAFT |
| VID-062 | T1 | Recorded stream continuity monitor | DRAFT |
| VID-063 | T1 | Crash-safe segment handling | DRAFT |
| VID-064 | T1 | Time zone and clock normalization | DRAFT |
| VID-065 | T1 | Recording retention preview | DRAFT |
| VID-066 | T2 | Smart event clip pre/post buffers | DRAFT |
| VID-067 | T2 | Rule-based event retention increase | DRAFT |
| VID-068 | T3 | Case-based protected retention holds | DRAFT |
| VID-069 | T4 | Federated retention policies by classification | DRAFT |
| VID-070 | T4 | Geographically isolated recorder clusters | DRAFT |

### 5. Playback and video evidence search

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-071 | T1 | Camera/date playback filters | DRAFT |
| VID-072 | T1 | 24h searchable recording timeline | DRAFT |
| VID-073 | T1 | Multi-camera synchronized replay | DRAFT |
| VID-074 | T1 | Variable playback speed | DRAFT |
| VID-075 | T1 | Frame step | DRAFT |
| VID-076 | T1 | Timestamp jump | DRAFT |
| VID-077 | T1 | Playback quality selector | DRAFT |
| VID-078 | T1 | Event marker overlay | DRAFT |
| VID-079 | T1 | Bookmark important timestamps | DRAFT |
| VID-080 | T1 | Snapshot extract | DRAFT |
| VID-081 | T1 | Clip trimming | DRAFT |
| VID-082 | T1 | Playback permission checks | DRAFT |
| VID-083 | T2 | Search by object event class | DRAFT |
| VID-084 | T2 | AI event timeline filters | DRAFT |
| VID-085 | T3 | Query by face or plate with authorization | DRAFT |
| VID-086 | T3 | Cross-camera appearance search | DRAFT |
| VID-087 | T3 | Saved investigator searches | DRAFT |
| VID-088 | T4 | Federated searches with delegated grant | DRAFT |
| VID-089 | T4 | Cross-system timeline search | DRAFT |

### 6. CCTV alerts and event infrastructure

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-090 | T1 | Camera offline alarm | DRAFT |
| VID-091 | T1 | Stream packet loss alarm | DRAFT |
| VID-092 | T1 | Camera tamper event when supported | DRAFT |
| VID-093 | T1 | Basic motion trigger | DRAFT |
| VID-094 | T1 | Recording missing segment alarm | DRAFT |
| VID-095 | T1 | Storage near-full alarm | DRAFT |
| VID-096 | T1 | Operator acknowledge event | DRAFT |
| VID-097 | T1 | Event severity flags | DRAFT |
| VID-098 | T1 | Searchable event history | DRAFT |
| VID-099 | T1 | Event to incident link | DRAFT |
| VID-100 | T2 | Object detection alert | DRAFT |
| VID-101 | T2 | Line-crossing alert | DRAFT |
| VID-102 | T2 | Zone intrusion alert | DRAFT |
| VID-103 | T2 | Loitering alert | DRAFT |
| VID-104 | T2 | Directional wrong-way alert | DRAFT |
| VID-105 | T2 | Abandoned object alert | DRAFT |
| VID-106 | T2 | Crowd threshold alert | DRAFT |
| VID-107 | T2 | Adaptive alert noise filtering | DRAFT |
| VID-108 | T2 | Event rule engine | DRAFT |
| VID-109 | T2 | Scheduled zone alert | DRAFT |
| VID-110 | T3 | Biometric watchlist matches with manual confirmation | DRAFT |
| VID-111 | T3 | Plate watchlist alerts | DRAFT |
| VID-112 | T3 | Multi-event correlation | DRAFT |
| VID-113 | T3 | Temporal incident correlation | DRAFT |
| VID-114 | T4 | Cross-domain event fusion | DRAFT |
| VID-115 | T4 | Policy-controlled emergency orchestration | DRAFT |

### 7. Video analytics general objects

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-116 | T1 | Person presence detection | DRAFT |
| VID-117 | T1 | Vehicle presence detection | DRAFT |
| VID-118 | T2 | Object class detection | DRAFT |
| VID-119 | T2 | People counting | DRAFT |
| VID-120 | T2 | Vehicle counting | DRAFT |
| VID-121 | T2 | Gate in/out counting | DRAFT |
| VID-122 | T2 | Dwell duration | DRAFT |
| VID-123 | T2 | Crowd density estimation | DRAFT |
| VID-124 | T2 | Queue length estimation | DRAFT |
| VID-125 | T2 | Heatmap of motion | DRAFT |
| VID-126 | T2 | PPE visual indication where validated | DRAFT |
| VID-127 | T2 | Visual fire/smoke assisted alert where validated | DRAFT |
| VID-128 | T2 | Thermal event interpretation | DRAFT |
| VID-129 | T2 | Configurable visual ROI polygons | DRAFT |
| VID-130 | T3 | Multi-camera entity relationship graph | DRAFT |
| VID-131 | T4 | Global coordinated object tracking | DRAFT |
| VID-132 | T4 | World coordinate object fusion | DRAFT |

### 8. Advanced camera health and diagnostics

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-133 | T1 | Camera heartbeat | DRAFT |
| VID-134 | T1 | Bitrate/fps health | DRAFT |
| VID-135 | T1 | RTSP reconnect logs | DRAFT |
| VID-136 | T1 | Last good recording indicator | DRAFT |
| VID-137 | T1 | Video resolution monitor | DRAFT |
| VID-138 | T2 | Black/covered lens detection | DRAFT |
| VID-139 | T2 | Blur detection | DRAFT |
| VID-140 | T2 | Frozen frame detection | DRAFT |
| VID-141 | T2 | Scene/view angle change detection | DRAFT |
| VID-142 | T2 | Unusual brightness/darkness alert | DRAFT |
| VID-143 | T2 | Time sync drift alert | DRAFT |
| VID-144 | T2 | Quality degradation scoring | DRAFT |
| VID-145 | T2 | Camera tamper confidence review | DRAFT |
| VID-146 | T3 | Incident correlation with health faults | DRAFT |
| VID-147 | T4 | Fleet anomaly prediction | DRAFT |
| VID-148 | T4 | Automatic capacity-aware dispatch | DRAFT |

### 9. Face intelligence and biometric governance

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-149 | T1 | Face detection and image quality scoring | DRAFT |
| VID-150 | T2 | Authorized reference image enrollment | DRAFT |
| VID-151 | T2 | Known/unknown tagging | DRAFT |
| VID-152 | T2 | Identity similarity candidate search | DRAFT |
| VID-153 | T2 | Recognition confidence display | DRAFT |
| VID-154 | T2 | Human confirm/reject face match | DRAFT |
| VID-155 | T2 | Face watchlist and ownership | DRAFT |
| VID-156 | T2 | Protected identity directory | DRAFT |
| VID-157 | T3 | Face last-seen timeline | DRAFT |
| VID-158 | T2 | Face crop and source-clip linkage | DRAFT |
| VID-159 | T2 | Biometric TTL and delete | DRAFT |
| VID-160 | T2 | Enrollment approval and audit | DRAFT |
| VID-161 | T2 | Bias/accuracy evaluation on tested populations | DRAFT |
| VID-162 | T2 | No automated adverse decision from face match | DRAFT |
| VID-163 | T4 | Cross-domain approved biometric query | DRAFT |
| VID-164 | T4 | Classification-aware face identity compartment | DRAFT |
| VID-165 | T4 | Regional approval workflow for watchlists | DRAFT |

### 10. Vehicle intelligence / ANPR / LPR

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-166 | T2 | Vehicle attributes and category classification | DRAFT |
| VID-167 | T1 | License-plate detection | DRAFT |
| VID-168 | T3 | Plate crop quality enhancement | DRAFT |
| VID-169 | T1 | Plate OCR Indonesian plate formats | DRAFT |
| VID-170 | T1 | Plate normalization and confidence | DRAFT |
| VID-171 | T2 | Vehicle registration directory | DRAFT |
| VID-172 | T2 | White/priority/deny list with policy | DRAFT |
| VID-173 | T2 | Manual OCR correction and audit | DRAFT |
| VID-174 | T2 | Vehicle last seen | DRAFT |
| VID-175 | T2 | Entry and exit correlation | DRAFT |
| VID-176 | T3 | Vehicle journey replay | DRAFT |
| VID-177 | T3 | Parking duration detection | DRAFT |
| VID-178 | T3 | Vehicle make/color attributes if validated | DRAFT |
| VID-179 | T2 | Evidence-backed plate search | DRAFT |
| VID-180 | T4 | Federated plate watchlist propagation with approval | DRAFT |
| VID-181 | T4 | Cross-agency vehicle correlation under authorization | DRAFT |

### 11. Cross-camera and semantic intelligence

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-182 | T3 | Appearance embedding search | DRAFT |
| VID-183 | T3 | Cross-camera person re-ID candidate | DRAFT |
| VID-184 | T3 | Cross-camera vehicle re-ID | DRAFT |
| VID-185 | T3 | Entity timeline | DRAFT |
| VID-186 | T3 | Journey reconstruction with uncertain links | DRAFT |
| VID-187 | T3 | Semantic video search | DRAFT |
| VID-188 | T3 | Natural language Ask GARDA evidence retrieval | DRAFT |
| VID-189 | T3 | Evidence-referenced AI answer | DRAFT |
| VID-190 | T3 | AI incident/shift summary with disclaimers | DRAFT |
| VID-191 | T3 | Case entity linking | DRAFT |
| VID-192 | T4 | Global entity graph with data compartments | DRAFT |
| VID-193 | T4 | Multi-modal video-text retrieval | DRAFT |
| VID-194 | T4 | VLM alert verification with second-stage evidence | DRAFT |
| VID-195 | T4 | AI-generated proposed rules with human sign-off | DRAFT |

### 12. Incident operations

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-196 | T1 | Incident creation and ID | DRAFT |
| VID-197 | T1 | Triage severity and category | DRAFT |
| VID-198 | T1 | Incident acknowledge | DRAFT |
| VID-199 | T1 | Incident assignment | DRAFT |
| VID-200 | T1 | Incident timeline and status | DRAFT |
| VID-201 | T1 | Operator notes | DRAFT |
| VID-202 | T1 | Incident evidence attachments | DRAFT |
| VID-203 | T1 | Supervisor escalation | DRAFT |
| VID-204 | T1 | Incident closure and reopening | DRAFT |
| VID-205 | T1 | Shift handover notes | DRAFT |
| VID-206 | T1 | Incident SLA timestamp tracking | DRAFT |
| VID-207 | T2 | AI-assisted prefilled incident records | DRAFT |
| VID-208 | T2 | Rule-initiated incident ticket | DRAFT |
| VID-209 | T2 | Escalation timer alerts | DRAFT |
| VID-210 | T3 | Investigation workspaces | DRAFT |
| VID-211 | T3 | Case chronology builder | DRAFT |
| VID-212 | T3 | Multi-party evidence collaboration | DRAFT |
| VID-213 | T3 | Case-to-person/vehicle association | DRAFT |
| VID-214 | T4 | Inter-agency command coordination | DRAFT |
| VID-215 | T4 | Emergency SOP execution state machine | DRAFT |

### 13. Evidence integrity and forensic export

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-216 | T1 | Evidence snapshot export | DRAFT |
| VID-217 | T1 | Video clip export | DRAFT |
| VID-218 | T1 | SHA-256 manifest | DRAFT |
| VID-219 | T1 | Source camera ID provenance | DRAFT |
| VID-220 | T1 | Normalized timestamp metadata | DRAFT |
| VID-221 | T1 | Export audit entries | DRAFT |
| VID-222 | T1 | Read-only evidence inspection | DRAFT |
| VID-223 | T1 | Export right authorization | DRAFT |
| VID-224 | T1 | Incident bundle with report and clips | DRAFT |
| VID-225 | T1 | Export format constraints | DRAFT |
| VID-226 | T1 | Watermarked audit export | DRAFT |
| VID-227 | T2 | Automatic event evidence bundle | DRAFT |
| VID-228 | T2 | Bulk tagged evidence packaging | DRAFT |
| VID-229 | T3 | Chain of custody handover record | DRAFT |
| VID-230 | T3 | Evidence legal hold | DRAFT |
| VID-231 | T3 | Case-controlled sharing with expiration | DRAFT |
| VID-232 | T3 | Tamper-evident history proof | DRAFT |
| VID-233 | T4 | Evidence cryptographic signatures with managed keys | DRAFT |
| VID-234 | T4 | Classification-controlled cross-agency evidence release | DRAFT |
| VID-235 | T4 | Offline signed evidence transfer | DRAFT |

### 14. Maps, GIS and digital twin

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-236 | T1 | Site and floor-plan upload | DRAFT |
| VID-237 | T1 | Camera pin positions | DRAFT |
| VID-238 | T1 | Camera coverage directional indicators | DRAFT |
| VID-239 | T1 | Online/offline map icons | DRAFT |
| VID-240 | T1 | Incident location pins | DRAFT |
| VID-241 | T1 | Site zones/polygons | DRAFT |
| VID-242 | T2 | Occupancy/heatmap overlay | DRAFT |
| VID-243 | T2 | ROI camera zone editing | DRAFT |
| VID-244 | T3 | GIS basemap adapter | DRAFT |
| VID-245 | T3 | Multi-site operational map | DRAFT |
| VID-246 | T3 | Investigative entity journey overlay | DRAFT |
| VID-247 | T4 | Regional/national GIS layers | DRAFT |
| VID-248 | T4 | 2D-3D digital twin | DRAFT |
| VID-249 | T4 | Calibrated geo-coordinate fusion | DRAFT |
| VID-250 | T4 | 3D tracking and trajectories | DRAFT |
| VID-251 | T4 | Critical infrastructure geofencing integration | DRAFT |

### 15. Roles and identities

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-252 | T1 | Operator user accounts | DRAFT |
| VID-253 | T1 | Supervisor role | DRAFT |
| VID-254 | T1 | Administrator role | DRAFT |
| VID-255 | T1 | Auditor role | DRAFT |
| VID-256 | T1 | Investigator role | DRAFT |
| VID-257 | T1 | Read-only command viewer role | DRAFT |
| VID-258 | T1 | RBAC and least privilege | DRAFT |
| VID-259 | T1 | Organization/camera ownership boundaries | DRAFT |
| VID-260 | T1 | Session expiry and revoke | DRAFT |
| VID-261 | T1 | MFA-ready identity design | DRAFT |
| VID-262 | T1 | Service account scopes | DRAFT |
| VID-263 | T1 | API authorization enforcement | DRAFT |
| VID-264 | T1 | Cross-unit deny-by-default tests | DRAFT |
| VID-265 | T2 | Event-rule author permissions | DRAFT |
| VID-266 | T2 | Sensitive biometric operator role | DRAFT |
| VID-267 | T2 | Watchlist admin dual approval | DRAFT |
| VID-268 | T4 | Hierarchical delegated command roles | DRAFT |
| VID-269 | T4 | Clearance plus need-to-know ABAC | DRAFT |
| VID-270 | T4 | Classification-aware access engine | DRAFT |
| VID-271 | T4 | Short-lived cross-unit special-code grant with approval | DRAFT |
| VID-272 | T4 | Emergency break-glass with audit | DRAFT |
| VID-273 | T4 | Periodic privileged access recertification | DRAFT |

### 16. Data classification and privacy

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-274 | T1 | Recorded-video retention policy | DRAFT |
| VID-275 | T1 | Personal data minimization | DRAFT |
| VID-276 | T1 | Per-site data ownership | DRAFT |
| VID-277 | T1 | Privacy mask on permitted view | DRAFT |
| VID-278 | T1 | User data deletion/export governance where applicable | DRAFT |
| VID-279 | T1 | Sensitive actions logged | DRAFT |
| VID-280 | T2 | Analytics metadata retention controls | DRAFT |
| VID-281 | T3 | Biometric purpose limitation and access logging | DRAFT |
| VID-282 | T3 | Consent/authority audit records | DRAFT |
| VID-283 | T3 | Training data segregation | DRAFT |
| VID-284 | T4 | Biasa/Terbatas/Rahasia classification UI | DRAFT |
| VID-285 | T4 | Classification labels applied to media/event/evidence | DRAFT |
| VID-286 | T4 | Mandatory classification enforcement | DRAFT |
| VID-287 | T4 | Need-to-know compartment access | DRAFT |
| VID-288 | T4 | No downgrade without approval | DRAFT |
| VID-289 | T4 | Cross-classification export gate | DRAFT |
| VID-290 | T4 | Classification key/storage segmentation | DRAFT |
| VID-291 | T4 | Redaction approval pipeline | DRAFT |

### 17. Site federation and command hierarchy

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-292 | T1 | Single-site organizational tree data model | DRAFT |
| VID-293 | T1 | Site identifiers and autonomous recordings | DRAFT |
| VID-294 | T2 | Site operations dashboard grouping | DRAFT |
| VID-295 | T3 | Approved multi-site supervisory view | DRAFT |
| VID-296 | T3 | Limited read-only multi-site health federation | DRAFT |
| VID-297 | T4 | Mabes/Kotama/Satker/Site configurable hierarchy | DRAFT |
| VID-298 | T4 | Top Command Center aggregating T1-T4 nodes | DRAFT |
| VID-299 | T4 | Site connector version negotiation | DRAFT |
| VID-300 | T4 | Local site autonomy on WAN loss | DRAFT |
| VID-301 | T4 | Policy-gated remote live viewing | DRAFT |
| VID-302 | T4 | Delegated central device administration | DRAFT |
| VID-303 | T4 | Cross-unit request/approve/revoke process | DRAFT |
| VID-304 | T4 | Central federated incident queue | DRAFT |
| VID-305 | T4 | Multi-region command activity dashboard | DRAFT |
| VID-306 | T4 | Distributed configuration propagation with approvals | DRAFT |
| VID-307 | T4 | Federation health and queue recovery | DRAFT |
| VID-308 | T4 | Remote node upgrade orchestration | DRAFT |

### 18. Integration Hub and external software

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-309 | T1 | REST API contracts | DRAFT |
| VID-310 | T1 | Versioned webhook event schema | DRAFT |
| VID-311 | T1 | Service-to-service auth | DRAFT |
| VID-312 | T1 | Integration audit trail | DRAFT |
| VID-313 | T1 | API rate limiting | DRAFT |
| VID-314 | T1 | Documented extension points | DRAFT |
| VID-315 | T2 | MQTT event adapter | DRAFT |
| VID-316 | T2 | Sensor/IoT telemetry ingest | DRAFT |
| VID-317 | T2 | Rule actions to approved webhooks | DRAFT |
| VID-318 | T2 | ONVIF Profile M analytics adapter | DRAFT |
| VID-319 | T3 | Access control read-only correlation | DRAFT |
| VID-320 | T3 | Visitor management connector | DRAFT |
| VID-321 | T3 | GIS connector | DRAFT |
| VID-322 | T3 | Ticketing/investigation system adapter | DRAFT |
| VID-323 | T3 | Notification system adapter | DRAFT |
| VID-324 | T3 | External data enrichment with authorization | DRAFT |
| VID-325 | T4 | Integration marketplace/adapter SDK | DRAFT |
| VID-326 | T4 | Bidirectional access-control actuation with interlock | DRAFT |
| VID-327 | T4 | Radio/dispatch integration | DRAFT |
| VID-328 | T4 | SIEM/SOC platform connector | DRAFT |
| VID-329 | T4 | Perimeter alarm connector | DRAFT |
| VID-330 | T4 | Fire safety/siren connector | DRAFT |
| VID-331 | T4 | PA/intercom integration | DRAFT |
| VID-332 | T4 | ERP/asset management connector | DRAFT |
| VID-333 | T4 | Cross-agency API gateway | DRAFT |
| VID-334 | T4 | Versioned connector sandbox | DRAFT |
| VID-335 | T4 | Integration dead-letter replay console | DRAFT |
| VID-336 | T4 | Signed plugin package validation | DRAFT |

### 19. Physical sensors and special feeds

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-337 | T2 | Thermal CCTV metadata import | DRAFT |
| VID-338 | T2 | IoT door contact sensors | DRAFT |
| VID-339 | T2 | Environmental sensor events | DRAFT |
| VID-340 | T2 | Panic button read-only ingest | DRAFT |
| VID-341 | T3 | Bodycam evidence ingestion | DRAFT |
| VID-342 | T3 | Traffic gate sensor fusion | DRAFT |
| VID-343 | T4 | Radar track adapter | DRAFT |
| VID-344 | T4 | Drone/UAS authorized video ingest | DRAFT |
| VID-345 | T4 | Thermal-optical fusion | DRAFT |
| VID-346 | T4 | Smart fence event correlation | DRAFT |
| VID-347 | T4 | LPR gate barrier integration with human authorization | DRAFT |
| VID-348 | T4 | Acoustic alarm event classification | DRAFT |
| VID-349 | T4 | Public address voice action with authorization | DRAFT |
| VID-350 | T4 | Multi-source location alignment | DRAFT |

### 20. Notifications, alerts and dispatch

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-351 | T1 | Operator in-app notifications | DRAFT |
| VID-352 | T1 | Critical alert banner | DRAFT |
| VID-353 | T1 | Supervisor acknowledgement | DRAFT |
| VID-354 | T1 | Email notification option | DRAFT |
| VID-355 | T1 | Notification preferences | DRAFT |
| VID-356 | T1 | Noisy alert mute and timer | DRAFT |
| VID-357 | T2 | Rule-based routing | DRAFT |
| VID-358 | T2 | On-call shift rotation | DRAFT |
| VID-359 | T2 | Alert deduplication | DRAFT |
| VID-360 | T2 | Smart escalation timing | DRAFT |
| VID-361 | T2 | Approved mobile push notifications | DRAFT |
| VID-362 | T3 | Investigator assigned case alerts | DRAFT |
| VID-363 | T3 | Watchlist hit review queue | DRAFT |
| VID-364 | T4 | Radio dispatch gateway | DRAFT |
| VID-365 | T4 | Emergency broadcast approval flow | DRAFT |
| VID-366 | T4 | Incident multi-agency paging | DRAFT |
| VID-367 | T4 | Geographically routed alert cascade | DRAFT |

### 21. Analytics and dashboards

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-368 | T1 | Camera uptime KPI | DRAFT |
| VID-369 | T1 | Incident count KPI | DRAFT |
| VID-370 | T1 | Storage capacity KPI | DRAFT |
| VID-371 | T1 | Operator response time KPI | DRAFT |
| VID-372 | T1 | Daily shift report export | DRAFT |
| VID-373 | T1 | Recording health trend | DRAFT |
| VID-374 | T1 | Device availability history | DRAFT |
| VID-375 | T2 | People flow graphs | DRAFT |
| VID-376 | T2 | Vehicle flow graphs | DRAFT |
| VID-377 | T2 | Crowd heatmap | DRAFT |
| VID-378 | T2 | Anomaly alerts by zone | DRAFT |
| VID-379 | T2 | False-positive review metrics | DRAFT |
| VID-380 | T2 | Peak hour summary | DRAFT |
| VID-381 | T3 | Recognized vehicle movement report | DRAFT |
| VID-382 | T3 | Investigative timeline analytics | DRAFT |
| VID-383 | T3 | AI executive summary with source links | DRAFT |
| VID-384 | T4 | Unified national operational overview | DRAFT |
| VID-385 | T4 | Cross-unit trends only with aggregation permissions | DRAFT |
| VID-386 | T4 | Predictive incident resource planning | DRAFT |

### 22. GARDA Vault and file collaboration

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-387 | T1 | Event clip storage and retrieval | DRAFT |
| VID-388 | T1 | Evidence folder structure | DRAFT |
| VID-389 | T1 | Vault audit trail | DRAFT |
| VID-390 | T1 | Quota policy basics | DRAFT |
| VID-391 | T1 | Read-only incident evidence attachment | DRAFT |
| VID-392 | T1 | Team folder and file upload workflows | DRAFT |
| VID-393 | T2 | File search and tagging | DRAFT |
| VID-394 | T2 | Preview and recycle bin | DRAFT |
| VID-395 | T2 | Expiring share links with RBAC | DRAFT |
| VID-396 | T3 | Case-specific evidence vault | DRAFT |
| VID-397 | T3 | Version history | DRAFT |
| VID-398 | T3 | Legal hold and retention override | DRAFT |
| VID-399 | T3 | Investigator collaboration folder | DRAFT |
| VID-400 | T4 | Classification-segregated vault | DRAFT |
| VID-401 | T4 | Sovereign object store replication | DRAFT |
| VID-402 | T4 | Approved classified file transfer | DRAFT |
| VID-403 | T4 | Cross-agency protected evidence exchange | DRAFT |

### 23. Infrastructure observability

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-404 | T1 | CPU/RAM metrics | DRAFT |
| VID-405 | T1 | Disk capacity metrics | DRAFT |
| VID-406 | T1 | Disk SMART health | DRAFT |
| VID-407 | T1 | RAID/pool health | DRAFT |
| VID-408 | T1 | Network throughput | DRAFT |
| VID-409 | T1 | UPS runtime indicator | DRAFT |
| VID-410 | T1 | Camera FPS/bitrate monitor | DRAFT |
| VID-411 | T1 | Service health dashboard | DRAFT |
| VID-412 | T1 | RTSP error counters | DRAFT |
| VID-413 | T1 | Server restart log | DRAFT |
| VID-414 | T2 | GPU utilization/temperature | DRAFT |
| VID-415 | T2 | AI throughput/latency metrics | DRAFT |
| VID-416 | T2 | Model error monitoring | DRAFT |
| VID-417 | T3 | Multi-site health aggregation | DRAFT |
| VID-418 | T3 | Correlation of infrastructure faults to case events | DRAFT |
| VID-419 | T4 | Predictive HDD/UPS lifecycle | DRAFT |
| VID-420 | T4 | National/regional NOC view | DRAFT |
| VID-421 | T4 | High-scale SLO/error budget reporting | DRAFT |

### 24. Resilience / backup / disaster recovery

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-422 | T1 | Config backup | DRAFT |
| VID-423 | T1 | Database backup | DRAFT |
| VID-424 | T1 | Restore procedure | DRAFT |
| VID-425 | T1 | UPS safe-shutdown support | DRAFT |
| VID-426 | T1 | WAN-loss autonomous recording | DRAFT |
| VID-427 | T1 | Recorder service restart recovery | DRAFT |
| VID-428 | T1 | Hot HDD capacity alerts | DRAFT |
| VID-429 | T1 | Basic recovery drill runbook | DRAFT |
| VID-430 | T2 | Edge inference failover strategy | DRAFT |
| VID-431 | T2 | Graceful AI degradation | DRAFT |
| VID-432 | T3 | Cross-site metadata backup | DRAFT |
| VID-433 | T3 | Resumable case synchronization | DRAFT |
| VID-434 | T4 | Site-level HA cluster | DRAFT |
| VID-435 | T4 | Regional disaster recovery | DRAFT |
| VID-436 | T4 | Failover command hub | DRAFT |
| VID-437 | T4 | Air-gapped deployment profile | DRAFT |
| VID-438 | T4 | Recovery RPO/RTO verification | DRAFT |
| VID-439 | T4 | Cryptographic offline backups | DRAFT |
| VID-440 | T4 | Multi-datacenter replication under classification rules | DRAFT |

### 25. Cybersecurity and secure operations

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-441 | T1 | HTTPS/TLS on app | DRAFT |
| VID-442 | T1 | Security headers | DRAFT |
| VID-443 | T1 | Credential secret store | DRAFT |
| VID-444 | T1 | Rate limiting | DRAFT |
| VID-445 | T1 | Password/session security | DRAFT |
| VID-446 | T1 | Audit for exports/config changes | DRAFT |
| VID-447 | T1 | CCTV VLAN separation | DRAFT |
| VID-448 | T1 | Dedicated management segment | DRAFT |
| VID-449 | T1 | VPN access | DRAFT |
| VID-450 | T1 | No public exposure of RTSP | DRAFT |
| VID-451 | T1 | Dependency vulnerability scan | DRAFT |
| VID-452 | T1 | Least privilege services | DRAFT |
| VID-453 | T1 | Safe backup permissions | DRAFT |
| VID-454 | T2 | Device security posture assessments | DRAFT |
| VID-455 | T2 | Automation rules change approvals | DRAFT |
| VID-456 | T3 | Biometric query monitoring | DRAFT |
| VID-457 | T3 | Immutable forensics logs | DRAFT |
| VID-458 | T3 | Sensitive search anomaly alerts | DRAFT |
| VID-459 | T4 | Central security event monitoring | DRAFT |
| VID-460 | T4 | SIEM correlation feed | DRAFT |
| VID-461 | T4 | Zero trust device attestation | DRAFT |
| VID-462 | T4 | HSM external key integration | DRAFT |
| VID-463 | T4 | Hardware rooted signing | DRAFT |
| VID-464 | T4 | Policy-as-code for classification | DRAFT |
| VID-465 | T4 | Air-gap update signature verification | DRAFT |
| VID-466 | T4 | Network data diode integration option | DRAFT |

### 26. Configuration and lifecycle

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-467 | T1 | Camera configuration revision history | DRAFT |
| VID-468 | T1 | Admin change log | DRAFT |
| VID-469 | T1 | License entitlement record | DRAFT |
| VID-470 | T1 | Versioned database migrations | DRAFT |
| VID-471 | T1 | Configuration backup | DRAFT |
| VID-472 | T1 | Diagnostic logs | DRAFT |
| VID-473 | T1 | Maintenance mode | DRAFT |
| VID-474 | T2 | Rule definition versioning | DRAFT |
| VID-475 | T2 | AI configuration profiles | DRAFT |
| VID-476 | T3 | AI model deployment versioning | DRAFT |
| VID-477 | T3 | Approved model rollback | DRAFT |
| VID-478 | T4 | Multi-site policy rollout | DRAFT |
| VID-479 | T4 | Hierarchical patch orchestration | DRAFT |
| VID-480 | T4 | Fleet firmware compliance | DRAFT |
| VID-481 | T4 | Operational change approval workflow | DRAFT |

### 27. Operator UX and localization

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-482 | T1 | Indonesian interface | DRAFT |
| VID-483 | T1 | Accessible keyboard controls | DRAFT |
| VID-484 | T1 | Dark operational theme | DRAFT |
| VID-485 | T1 | Large command monitor layouts | DRAFT |
| VID-486 | T1 | Quick camera hotkeys | DRAFT |
| VID-487 | T1 | Screen-readable timestamps | DRAFT |
| VID-488 | T1 | No blank camera tiles without reason | DRAFT |
| VID-489 | T1 | Common searchable navigation | DRAFT |
| VID-490 | T2 | Event-driven workspace | DRAFT |
| VID-491 | T2 | Personalized notification settings | DRAFT |
| VID-492 | T3 | Investigator workspace layouts | DRAFT |
| VID-493 | T3 | Natural-language search interaction | DRAFT |
| VID-494 | T1 | Bilingual operational language packs | DRAFT |
| VID-495 | T4 | Accessibility across federated controls | DRAFT |
| VID-496 | T4 | Classification watermark and badge | DRAFT |

### 28. Web and mobile applications

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-497 | T1 | Responsive command web UI | DRAFT |
| VID-498 | T1 | Browser camera compatibility matrix | DRAFT |
| VID-499 | T1 | Offline network error indicators | DRAFT |
| VID-500 | T3 | Mobile alert-only companion | DRAFT |
| VID-501 | T2 | Approved secure remote VPN viewer | DRAFT |
| VID-502 | T3 | Mobile investigator case access | DRAFT |
| VID-503 | T3 | Mobile authorized video review | DRAFT |
| VID-504 | T3 | Mobile evidence annotation | DRAFT |
| VID-505 | T4 | Field command app with cached SOP | DRAFT |
| VID-506 | T4 | Secure offline field synchronization | DRAFT |
| VID-507 | T4 | HQ/mobile incident dispatch | DRAFT |

### 29. Automation and command SOP

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-508 | T1 | Operator-confirmed incident workflow | DRAFT |
| VID-509 | T1 | Incident severity and escalation rule settings | DRAFT |
| VID-510 | T2 | Visual rule builder | DRAFT |
| VID-511 | T2 | Zone/time thresholds | DRAFT |
| VID-512 | T2 | Multi-event automation chaining | DRAFT |
| VID-513 | T2 | Rule simulation and dry run | DRAFT |
| VID-514 | T3 | AI-generated draft incident narrative with review | DRAFT |
| VID-515 | T3 | Semantic rule suggestion with confirmation | DRAFT |
| VID-516 | T4 | Command SOP engine | DRAFT |
| VID-517 | T4 | Incident playbooks with approval gates | DRAFT |
| VID-518 | T4 | Cross-system orchestration | DRAFT |
| VID-519 | T4 | Actuation safety interlock | DRAFT |
| VID-520 | T4 | Post-command provenance and replay | DRAFT |

### 30. AI / model operations and accuracy

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-521 | T2 | Detector confidence thresholds | DRAFT |
| VID-522 | T2 | False positive review label capture | DRAFT |
| VID-523 | T2 | Versioned detector packages | DRAFT |
| VID-524 | T2 | GPU workload scheduling | DRAFT |
| VID-525 | T3 | Face/plate accuracy monitoring | DRAFT |
| VID-526 | T3 | Human-in-the-loop match verification | DRAFT |
| VID-527 | T3 | Model evaluation on approved datasets | DRAFT |
| VID-528 | T3 | AI explanation with evidence clips | DRAFT |
| VID-529 | T4 | Model registry and approval workflow | DRAFT |
| VID-530 | T4 | VLM verification chain | DRAFT |
| VID-531 | T4 | Canary/shadow deployment | DRAFT |
| VID-532 | T4 | Model drift detection | DRAFT |
| VID-533 | T4 | Hardware-aware GPU orchestration | DRAFT |
| VID-534 | T4 | AI safety and fairness reporting | DRAFT |
| VID-535 | T4 | Sovereign offline model hosting | DRAFT |

### 31. System licensing and commercial features

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-536 | T1 | Tier entitlement record | DRAFT |
| VID-537 | T1 | Site activation identity | DRAFT |
| VID-538 | T1 | Module feature flag gating at API | DRAFT |
| VID-539 | T1 | License expiry grace-period policy | DRAFT |
| VID-540 | T1 | Offline license verification design | DRAFT |
| VID-541 | T1 | Camera-count entitlement option | DRAFT |
| VID-542 | T2 | AI inference-capacity entitlement option | DRAFT |
| VID-543 | T2 | Recognition/biometric add-on entitlement | DRAFT |
| VID-544 | T3 | Federation site count entitlement option | DRAFT |
| VID-545 | T4 | Command hierarchy entitlement | DRAFT |
| VID-546 | T4 | Cross-tier federation license administration | DRAFT |
| VID-547 | T4 | Offline enterprise license issuing | DRAFT |
| VID-548 | T4 | Auditable offline entitlement transfer | DRAFT |

### 32. Audit, compliance and reporting

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-549 | T1 | Login/logout audit | DRAFT |
| VID-550 | T1 | Camera view audit | DRAFT |
| VID-551 | T1 | Recording playback audit | DRAFT |
| VID-552 | T1 | Evidence export audit | DRAFT |
| VID-553 | T1 | Incident status audit | DRAFT |
| VID-554 | T1 | Admin changes audit | DRAFT |
| VID-555 | T1 | Timestamp/sync validation | DRAFT |
| VID-556 | T1 | Daily audit review console | DRAFT |
| VID-557 | T2 | Rules/AI action provenance | DRAFT |
| VID-558 | T2 | Alarm response SLAs | DRAFT |
| VID-559 | T3 | Biometric enrollment and searches audit | DRAFT |
| VID-560 | T3 | Chain-of-custody reports | DRAFT |
| VID-561 | T3 | Investigator case export approval | DRAFT |
| VID-562 | T4 | Cross-unit special-grant audit | DRAFT |
| VID-563 | T4 | Classification policy-change audit | DRAFT |
| VID-564 | T4 | Compliance evidence reports | DRAFT |
| VID-565 | T4 | Privileged break-glass review | DRAFT |
| VID-566 | T4 | External independent audit export | DRAFT |

### 33. Deployment, tooling and testing

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-567 | T1 | Docker Compose deploy profile | DRAFT |
| VID-568 | T1 | Environment config sample | DRAFT |
| VID-569 | T1 | CI typecheck/lint/tests | DRAFT |
| VID-570 | T1 | Synthetic safe demo fixtures | DRAFT |
| VID-571 | T1 | Camera simulator for tests | DRAFT |
| VID-572 | T1 | Hardware/firmware support matrix | DRAFT |
| VID-573 | T1 | Backup restore verification | DRAFT |
| VID-574 | T1 | Load baseline capture | DRAFT |
| VID-575 | T2 | GPU benchmark fixtures | DRAFT |
| VID-576 | T2 | AI event ground-truth testset | DRAFT |
| VID-577 | T2 | Edge device agent diagnostics | DRAFT |
| VID-578 | T3 | Face/plate evaluation with authorized labeled data | DRAFT |
| VID-579 | T3 | Multi-site federation staging | DRAFT |
| VID-580 | T4 | Federated chaos experiments | DRAFT |
| VID-581 | T4 | Air-gap installation and patch playbook | DRAFT |
| VID-582 | T4 | DR exercises | DRAFT |
| VID-583 | T4 | Regional load & fault injection | DRAFT |
| VID-584 | T4 | Secure offline supply-chain package | DRAFT |

### 34. Future extreme research candidates

| ID | Min tier | Capability | Status |
|---|---|---|---|
| VID-585 | T3 | Investigative graph reasoning with human-review evidence | DRAFT |
| VID-586 | T3 | Privacy-preserving feature aggregation | DRAFT |
| VID-587 | T4 | Multi-camera 3D scene fusion | DRAFT |
| VID-588 | T4 | Collaborative edge intelligence under privacy constraints | DRAFT |
| VID-589 | T4 | Federated analytics without raw footage | DRAFT |
| VID-590 | T4 | Authenticated synthetic scene rehearsal | DRAFT |
| VID-591 | T4 | Privacy-preserving regional anomaly signals | DRAFT |
| VID-592 | T4 | Post-quantum crypto migration preparedness | DRAFT |

## Catalog QA summary
- Total distinct candidate capability entries: **592**.
- Proposed minimum tier counts: T1 **227**, T2 **123**, T3 **91**, T4 **151**.
- No entry is declared APPROVED/IMPLEMENTED/ACCEPTED by this catalog.
- Real TNI hierarchy and classification terms must be adapted from customer policy/KAK; no speculative camera counts, pricing or SLA.
- Several entries are **research** or integration possibilities (not vendor capability warranties). Any real biometric/physical control integration requires separate authority and safety evaluation.

## Feature workflow and KAK mapping template
For each `VID-nnn` add an issue with: source/decision ID; user story; minimum tier; affected organization/resource; security/privacy scope; functional acceptance; performance SLO; on-prem/offline expectation; integration/camera models; test evidence; milestone; KAK clause; owner approval; deploy/release status.
Keep status consistent across issue, PR, feature registry and acceptance report. Use changelog rather than replacing this file silently.

## Commercial and architectural constraints
1. Tier 4 can coordinate nodes licensed at T1/T2/T3/T4 **without accessing a unit's protected data by default**. Cross-unit requests need approval, scoped one-time authorization and audit.
2. Official data labels (Biasa, Terbatas, Rahasia; further levels TBD) and clearance policy are Tier 4 capabilities; minimal privacy/RBAC protection applies to **all tiers**.
3. All interoperability is modular and versioned; connectors never bypass local authorizations or safety interlocks.
4. Proprietary GARDA backend/AI source is NOT customer deliverable. Viewer/basic-client source may be released only in a separate approved package; frontend code is inspectable, so rights must be backend-enforced.
5. Never mistake the repository's existing synthetic frontend demo for production camera integrations.


## v0.3 CHANGELOG — 2026-10-08
- **Owner decision:** camera Basic strictly fewer than 50, one site, one operator; independent NVR backup, 7-day default GARDA retention with HDD sizing, offline-first and offline license, bilingual UI, limited GARDA Vault, basic person+face-presence detection and ANPR Lite; Tier2 recognition, Tier3 native mobile, Tier4 top federation.
- Capability IDs preserved and not renumbered. Changed proposed earliest tiers: **31** entries; v0.2 remains available in git.
- Some advanced techniques within a broad catalog row remain outside the lower-tier capability; refer to PRD for exact API/use-case acceptance scope.
- This catalog is not customer-approved contractual delivery. PUSADA's **KAK requires capabilities beyond base T1 and 90-day retention**; refer to special bundle gap matrix.
- Future tier quotas (T2/T3/T4 site/camera/operator) remain OPEN.

### Individual tier changes
| ID | Earlier | Revised | Capability |
|---|---|---|---|
| VID-116 | T2 | T1 | Person presence detection |
| VID-117 | T2 | T1 | Vehicle presence detection |
| VID-149 | T3 | T1 | Face detection and image quality scoring |
| VID-150 | T3 | T2 | Authorized reference image enrollment |
| VID-151 | T3 | T2 | Known/unknown tagging |
| VID-152 | T3 | T2 | Identity similarity candidate search |
| VID-153 | T3 | T2 | Recognition confidence display |
| VID-154 | T3 | T2 | Human confirm/reject face match |
| VID-155 | T3 | T2 | Face watchlist and ownership |
| VID-156 | T3 | T2 | Protected identity directory |
| VID-158 | T3 | T2 | Face crop and source-clip linkage |
| VID-159 | T3 | T2 | Biometric TTL and delete |
| VID-160 | T3 | T2 | Enrollment approval and audit |
| VID-161 | T3 | T2 | Bias/accuracy evaluation on tested populations |
| VID-162 | T3 | T2 | No automated adverse decision from face match |
| VID-167 | T3 | T1 | License-plate detection |
| VID-169 | T3 | T1 | Plate OCR Indonesian plate formats |
| VID-170 | T3 | T1 | Plate normalization and confidence |
| VID-171 | T3 | T2 | Vehicle registration directory |
| VID-172 | T3 | T2 | White/priority/deny list with policy |
| VID-173 | T3 | T2 | Manual OCR correction and audit |
| VID-174 | T3 | T2 | Vehicle last seen |
| VID-175 | T3 | T2 | Entry and exit correlation |
| VID-179 | T3 | T2 | Evidence-backed plate search |
| VID-266 | T3 | T2 | Sensitive biometric operator role |
| VID-267 | T3 | T2 | Watchlist admin dual approval |
| VID-392 | T2 | T1 | Team folder and file upload workflows |
| VID-494 | T4 | T1 | Bilingual operational language packs |
| VID-500 | T2 | T3 | Mobile alert-only companion |
| VID-541 | T2 | T1 | Camera-count entitlement option |
| VID-543 | T3 | T2 | Recognition/biometric add-on entitlement |
