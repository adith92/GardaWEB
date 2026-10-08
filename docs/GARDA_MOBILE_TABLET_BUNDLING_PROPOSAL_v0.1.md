# GARDA — Mobile Applications & Bundled Tablet Strategy v0.1
**Created:** 2026-10-08
**Status:** PRODUCT OWNER DISCOVERY — hardware tablet bundling and anti-unauthorized deployment are expressed needs; tier distribution below is **RECOMMENDED, NOT YET APPROVED**.
**Context:** Government/TNI, GARDA 4 cumulative tiers. Canonical names T1–T4; SIAGA/WASPADA/WASKITA/KOMANDO are still **proposed branding**.

## Executive decision sought
The owner wants Android/iOS apps in future tiers; advanced field/command capabilities should be delivered with **company-supplied GARDA-branded tablets locked to the approved app**. They also want a light **view-only app installable on separately approved devices**, and asked which tier should contain it.

### Recommendation
| Entitlement | Earliest recommended tier | App / device offering | Who can do what |
|---|---|---|---|
| **NO NATIVE APP** | T1 SIAGA | On-prem/WebApp only | Local operator uses browser WebApp; independent NVR backup |
| **GARDA VIEW** | **T2 WASPADA**, as view-only controlled add-on (or included if approved) | Native Android/iOS viewer distributed via approved enterprise/private channel; may be on licensed personal/agency device with **device enrollment** | View only camera live (authorized unit/site) + optionally basic status, incident alert and permitted playback *only if explicitly entitled*. No PTZ control by default, export, snapshot download, watchlist changes, biometric search, enrollment or inter-unit grants |
| **GARDA FIELD** | **T3 WASKITA** | GARDA-owned/managed **tablet + app + kiosk/MDM + per-device license**, optionally integrated with native mobile investigator app | Governed investigator/field permissions: case, permitted playback, evidence annotations, Ask GARDA if licensed, incident acknowledgment; no unauthorized export / cross-unit viewing |
| **GARDA COMMAND** | **T4 KOMANDO** | GARDA-managed hardened **command tablet + controlled app + command license** | Hierarchical Common Operating Picture, scoped cross-tier viewing, approvals, authorized dispatch/SOP operations, classification-aware RBAC/ABAC, high-assurance audit |

**Read-only GARDA VIEW is proposed for T2** even though the earlier v0.3 decision says *native Android/iOS begins at T3*. This is a proposed **exception/change request** awaiting explicit owner approval, NOT an implicit replacement of v0.3. T1 remains without native mobile app. Keeping basic alerts via approved existing channels for the PUSADA contract does not require a GARDA native app.

## Different products, different trust boundaries
1. **Viewer app (T2):** installable on specifically authorized Android/iOS phones/tablets. Licensing ties access to **user + enrolled device + site + role + allowed cameras + permitted streaming actions**, not only to the APK's install location. BYOD allowed only when customer policy permits; sensitive TNI networks should default to organization-managed devices.
2. **Bundled GARDA field tablet (T3):** shipped physically with preinstalled app and managed device configuration. Locked into one application or approved small app set, with OS management, device attestation/PKI binding, local or enterprise UEM, and a serial/inventory handover.
3. **Command tablet (T4):** managed field tablet controls + stricter authentication, dual authorization for classified/critical actions, classification labels, compartment/need-to-know, robust security controls; HQ rank alone never bypasses owner permissions.
4. **Not an APK DRM promise:** app binaries can potentially be extracted/copied, and stock hardware cannot be promised impossible to reset or jailbreak. Protection goal = **copied app or unmanaged tablet cannot authenticate or receive any GARDA video/data/commands from backend**.

## Recommended protection architecture (defense in depth)
```
Factory-supplied tablet --> hardware-backed keypair / device identity
  |  (enrollment requires an approved administrator)
  v
GARDA Device Registry (on-prem): site + serial/inventory + device public key + user + tier/license
  |-- Device attestation (supported hardware, during provisioning / periodic checks)
  |-- PKI/client certificate, revocable; never embed an extractable shared static secret
  |-- Approved Android Enterprise device-owner / dedicated kiosk or supervised iPad MDM
  v
GARDA API Gateway: mutual TLS/device binding + user session/MFA + RBAC/ABAC + entitlements
  |-- per-camera stream ticket time-limited and revocable
  |-- full audit + remote access termination + device loss workflow
  v
ON-PREM GARDA: site-local video/AI/storage; only permitted signed stream & incident data
```
- Device binding alone does not replace user authentication, authorization, owner unit camera scoping or encrypted transport.
- Example local entitlement fields: `license_id`, `tier`, `module`, `device_public_key_hash`, `device_inventory_id`, `site_id`, `user_id`, `cameras_allowed`, `expires_at`, `revoked_at`, `offline_policy`.
- QR code may initiate enrollment but **QR/IMEI/MAC/serial by itself is not an authentication secret**. Protect the enrollment workflow and require hardware-bound proof-of-possession. Reassignment and RMA require explicit revoke, reset and re-enrollment.
- Rooted/untrusted or compromised devices fail policy or are restricted; allow documented operator recovery with audit, avoid breaking ongoing on-prem NVR recording.
- Device loss: revoke at GARDA server immediately; wipe when management channel available. Remote wipe cannot be guaranteed on an unreachable powered-off device. Encrypted OS/device storage protects cached sensitive data.
- Block or restrict screen capture, clipboard, local media export, USB debugging/side-load, app switching and external backup as hardware/OS policy allows, but cannot prevent someone using another camera to photograph a screen.
- Stream overlays/watermark with `user/device/camera/timestamp` for accountable viewing, especially in higher tiers. Conditional per policy, avoid exposed classified data.
- Hardware first choice for company tablets can be enterprise-supported Android with reputable security updates and managed provisioning; compare iPad supervised deployment where necessary. **Do not select model/vendor by brand alone**; validate lifecycle, OS/patches, supported hardware-backed keys, cellular/eSIM/LAN/VPN/Wi-Fi, replacement policy, cost and Indonesian availability.

## What MDM/Kiosk actually does
- **Android Enterprise fully managed dedicated device**: managed provisioning, device restrictions, app allowlist, kiosk mode, app push, admin commands including remote lock/wipe and policy compliance. Android Management API + Managed Google Play are ordinarily Google-connected management options; verify offline/bootstrap limitations before any air-gapped TNI offer.
- **Apple Business / Automated Device Enrollment with supervision**: organization-owned iPad managed from device setup, restrictions and managed apps. Apple Managed Device Attestation can provide stronger device identity via Secure Enclave, but Apple services may be needed during provisioning/attestation.
- **Fully isolated / air-gapped deployment**: requires a specifically proven local enrollment/management route, locally hosted signing/PKI, offline app updates through vetted signed packages, local revoke lists and recovery playbooks. Do NOT claim that cloud-dependent MDM or Play Integrity always work without Internet. For normal offline-first site with approved optional outbound connectivity, managed MDM may be viable with secure controlled management window.

### Verified public reference material (current, official)
- Google Android Enterprise dedicated management: https://support.google.com/work/android/answer/9560920
- Android dedicated kiosk policy examples: https://developers.google.com/android/management/policies/dedicated-devices
- Android enterprise private app distribution: https://developers.google.com/android/management/apps
- Android hardware-backed attestation: https://developer.android.com/identity/digital-credentials/credential-issuer/keystore-attestation
- Apple Automated Device Enrollment & management: https://support.apple.com/guide/security/automated-device-enrollment-secc2cd563ef/web
- Apple Managed Device Attestation: https://support.apple.com/guide/security/managed-device-attestation-sec8a37b4cb2/web

## Viewer (T2) restrictions proposal
| Action | T2 GARDA VIEW | T3 FIELD on bundled device | T4 COMMAND on bundled device |
|---|---|---|---|
| Authenticated live view of own authorized site | YES | YES | YES |
| Camera health & alert banner | YES (read-only) | YES | YES |
| Playback | OPTIONAL entitlement | YES with rights | YES with classification |
| Export / save video locally | NO | OFF by default; separate approval | OFF by default; classification-gated approval |
| Person name/face/plate watchlist investigation | NO | Optional scoped permissions | Classification and purpose gated |
| PTZ/remote control | NO | Optional role-gated | Optional with approval |
| Incident creation / response | NO; read-only alerts | YES if entitled | YES + cross-unit workflow |
| HQ multi-unit federation | NO | Only specially approved limited views | YES via T4 policy, never automatic |
| Device requirements | enrolled/approved and authenticated device | managed issued tablet, certificate-bound, kiosk | managed hardened command tablet, hardware keys, stronger privileged attestation |

## Proposed commercial packaging
- T2: `GARDA VIEW LICENSE` with a small permitted device quota per named user/site, possibly sold as an add-on. Counts, pricing and playback allowance **OPEN**.
- T3: `GARDA FIELD KIT` = physical tablet + locked management + Field app license + initial provisioning + warranty/replacement + support; renewal/replacement license is tied to registered replacement with revoke/reissue.
- T4: `GARDA COMMAND KIT` = hardened tablet + HQ command software license + high-assurance enrollment + managed support, subject to classification/data policy.
- Device cost, cellular/data connectivity, management subscriptions, on-prem management deployment, spare pool, battery/charger, and 3-year replacement/warranty must be **separate visible procurement items**. No SKU/pricing proposed yet.
- Avoid making existing licensed WebApp seats silently become unlimited mobile seats. Dedicated **viewer seat/device** entitlements and role caps are explicit.

## PUSADA KAK interpretation
The uploaded KAK includes **notifications via dashboard, mobile, email or another approved channel** and mandates full other modules, but does **not unambiguously require a proprietary native Android/iOS app or bundled GARDA tablet** in the initial 16-point Basic contract. Verify the approved notification channel and avoid charging/adding Tier2 mobile app unless expressly included by procurement/customer. The independent KAK compliance gap matrix still applies.

## Codex implementation boundary
This is **NOT approval to code mobile today or change the shipping four-tier features**. Create architectural hooks for `DeviceRegistry`, `DeviceBinding`, `AppEntitlement`, `LicenseSeat`, `AllowedActions`, and `AccessAudit` when appropriate. Separate viewer-only API scopes from T3 investigator and T4 command rights, centrally enforced on streams and evidence. No hard-coded root secrets, device serial as password, hidden backdoors or licence verification solely in front-end mobile code.

## Follow-up confirmation for owner
**Approve or modify proposal:** "GARDA VIEW view-only di Tier2; GARDA FIELD tablet bundling T3; GARDA COMMAND tablet bundling T4". If approved, adjust canonical decision register/tier feature IDs and executive PDF; count/pricing and deployment network remain open.
