# GARDA five-platform MVP — source candidate and pre-build review

Owner decisions recorded 16 November 2026 (Asia/Jakarta): one local server; client
targets Windows, Apple Silicon M1 macOS, Ubuntu, Android 13+ and Web; at least eight
cameras; old Android signing key unavailable. One-day priority applies to this lab
MVP. APK/installer/production Web build requires the owner's explicit confirmation.

Latest steering: initial lab must open without login as local Admin with all role
permissions. Unified `serve` defaults to this mode. Named accounts remain optional
through `serve --require-login`; the private site gateway determines which devices
can reach the all-Admin lab. CSRF/origin protections and local encryption remain.

## Source implementation

| Module | Source state | Validation boundary |
|---|---|---|
| Shared API | Named users, scrypt hashes, expiring sessions, roles/CSRF, old event read compatibility | Source/API tests; not external ingress certification |
| Camera runtime | Eight initial slots, encrypted private-IP RTSP credentials, bounded latest-frame queues, reconnect/timeouts, fresh JPEG previews | Configuration supported up to 49; eight real-camera throughput not measured |
| AI adapters | YuNet/SFace, DeepFace(SFace), licensed local InsightFace ONNX, FastALPR and detector+PaddleOCR | Lazy optional dependencies; local model fingerprints/provisioning required; no real model accuracy validation |
| Web | /workspace login, eight-slot live view, devices, event search/evidence, face enrollment/revoke, provider status, update guidance | React type-check and local browser QA, no production bundle |
| Desktop | Sandboxed shared Electron client, validated server address, restricted IPC/navigation | Node policy tests; Windows/Mac/Ubuntu installers not built |
| Android | Both existing flavors, minSdk 33, v0.13.0(17), named-session API, embedded shared Workspace, server-origin-only OTA authorization | Source/test compilation CI; no new APK assembly yet |
| OTA | Private GitHub Release relay, checked size/hash, redirect allowlist and server-only GitHub token | Mocked network tests; no real approved Release asset configured |

Source entrypoints: [unified server](../projects/garda/ai-core/README_UNIFIED.md),
[desktop client](../desktop/README.md), [Android](../projects/foldview-cctv/android/README.md).

## Focused local checks

- Python: 32 tests pass (18 existing + 14 new), including session/role/CSRF boundaries,
  eight offline slots, encrypted camera URLs, event lookup and release redirect/hash failures.
- Node: 6 tests pass (4 existing demo + 2 desktop navigation policy).
- TypeScript: `tsc --noEmit` passes. No `vite build` executed.
- Browser QA: initial local Admin bypass (no login), optional named login/logout, all eight offline camera slots, provider availability,
  empty event search and rejected public RTSP configuration verified. Desktop and
  390px responsive view inspected; no horizontal document overflow at 390px.
- UI fix during QA: scoped heading colors to avoid inherited demo white text on
  the light Workspace surface. Actual live images and physical Android WebView
  are not validated by the offline-slot screenshots.
- Cross-OS Python and Android unit compilation are delegated to CI source checks;
  actual results must be read from the current PR, not inferred from the workflow.

## Build hold and planned packages

Automatic APK assembly/upload is disabled. Manual workflow `approved_build` defaults
to false. Vercel auto-preview is disabled for the lab branch. Optional source archive
upload defaults to false so artifact quota does not mask source-test results.

After source review and owner confirmation, proposed internal packages are:

| Target | Intended package | Required acceptance |
|---|---|---|
| Web | Vite dist, on-prem HTTPS gateway | Actual browser stream and API tests |
| Windows x64 | Electron NSIS EXE | Install, server login, rendering |
| Mac M1 | Electron arm64 DMG | macOS run, camera view, signing status declared |
| Ubuntu x64 | Electron AppImage/DEB | Desktop dependencies, login, rendering |
| Android 13+ | Fold and Standard APKs v0.13.0(17) | New persistent signing identity, backup/migration, install/OTA tests |

User has no old Android private signing key. Existing installed APKs cannot be
updated in place under a different certificate. The new private keystore script
is prepared but has not been run. Apple notarization/Windows trusted signing
credentials are not available; internal packages cannot be presented as trusted
production releases.

## Outstanding acceptance

1. Provision audited model weights and optional engine environments; compare their
   accuracy using authorized faces and Indonesian plates. InsightFace model licensing
   is a concrete prerequisite; a configuration flag does not grant a license.
2. Configure eight real streams and run sustained decode/inference/reconnect tests
   on the owner's 4070 SUPER host. No eight-camera capacity claim yet.
3. Configure on-prem HTTPS/CA and verify actual Mac M1, Ubuntu and Android devices.
4. Confirm the requested package/signing plan before any packaging command.
5. Recorder/NVR integration, full-FPS gateway streaming, physical PTZ, legal-hold,
   production MFA/key rotation, model accuracy targets and desktop automatic updates
   remain outside this first source candidate. PR #9/#10 are still separate work.

## Feature traceability (source implementation only)

- VID-002: manual private-IP RTSP registration; encrypted server-local credentials.
- VID-005/007: local secret vault and operational inventory/status (model/firmware inventory pending).
- VID-023/032/033: reconnect, single/adaptive wall preview; real throughput untested.
- VID-149/150: face presence/reference enrollment and matching adapter; lab-authorized,
  distinct from commercial Basic entitlements.
- VID-167/169/170: plate detection/OCR/event metadata adapters; accuracy untested.
- VID-252/253/254/255: named viewer/operator/admin roles; full production auth/MFA pending.
- VID-500: Android native/shared client source; package and physical acceptance pending.

These entries do not change catalog feature status to customer ACCEPTED.
