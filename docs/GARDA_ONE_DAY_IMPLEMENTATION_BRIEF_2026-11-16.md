# GARDA five-platform implementation brief

Date: 16 November 2026 (Asia/Jakarta).
Status: owner selected the central-server MVP architecture. Mac Apple Silicon M1, Ubuntu, Android 13+, minimum eight cameras; no previous signing key. Source implementation/status: GARDA_FIVE_PLATFORM_MVP_STATUS_2026-11-16.md.
Owner requests Windows, macOS, Linux, Android and Web, a one-day engineering target,
and explicit confirmation before builds. No APK/installer/frontend production build
is authorized by this brief alone. The pre-build confirmation comes after the source
changes, test results and exact proposed packages are available for review.

## Recommended architecture for owner selection

One local AI/API service initially runs on the available Windows lab machine
(RTX 4070 SUPER, approximately 64 GiB RAM), with Linux portability. Windows,
macOS and Linux desktop clients, Android FOLD/Standard, and React Web consume
one versioned API. Browser video uses a media gateway. Inference on every
client is a distinct alternative awaiting owner selection.

The current AI Core uses /api/events and /api/stats and already has Desktop
and Android consumers. PR #10 uses /api/v1 with a separate auth/event schema.
Define one contract and retain an explicit compatibility adapter during migration;
do not assume the existing clients can connect to either service interchangeably.

## Engine integration

| Task | Default candidate | Additional providers |
|---|---|---|
| Face detection/alignment | OpenCV YuNet | DeepFace-supported detector when selected |
| Enrolled face matching | OpenCV SFace | DeepFace; InsightFace only with an eligible model license |
| Plate detection and reading | FastALPR detector + OCR | PaddleOCR on detected plate crops; FastPlateOCR through FastALPR |

Providers have a shared result schema, model provenance, version, device selection,
health/status and explicit errors. Optional dependencies are loaded only for the
selected provider. An absent engine/model must report unavailable instead of
silently generating simulated recognition. Compare providers against the same
authorized dataset; confidence values from different engines are not interchangeable.
Preserve upstream licenses and verify each distributed model's terms and hash.

## Proposed one-day internal MVP acceptance

- Same API can be used by Web, Windows/macOS/Linux desktop and Android clients.
- Start with the actual owner-selected test cameras; one stream must decode before
  being marked online. Discovery and open ports alone do not satisfy acceptance.
- Live video, authorized reference enrollment, face candidates, plate detection/OCR,
  event search, snapshots, login/permissions and capability status.
- Provider selection, missing-model states and model/device errors are visible.
- OTA source can be a private GitHub Release through a GARDA update relay.
- Android update retains its package/signing identity. Mac signing/notarization and
  other OS signing require available owner-controlled credentials and runners.
- Source/unit/API tests and actual OS/device smoke results are reported separately.
  An untested OS or camera remains explicitly unverified.

The one-day target is an engineering priority, not proof of production readiness,
hardware compatibility, contract acceptance, recognition accuracy or a new SLA.
The earlier PUSADA contract baseline is retained as history; any contractual
replacement requires a distinct owner decision.

## Work order after scope clarification

1. Consolidate schemas, auth, camera registration and adapter interfaces.
2. Integrate eligible face/plate providers and a reproducible local model manifest.
3. Connect clients to the shared API and gateway. Preserve app IDs and existing
   camera profiles. Apply the selected React best practices: conditional heavy
   imports, parallel independent fetches and stable subscriptions/state updates.
4. Run focused source/API/provider/client tests and record the camera/OS matrix.
5. Present exact packages, versions, signing requirements and unresolved test gaps
   to the owner for the requested pre-build confirmation.
6. Build only the confirmed packages; verify checksums/signatures and smoke tests.

## Information requested from owner

1. Central AI server with clients, or local inference on each platform?
2. Accept the proposed one-day internal MVP, or specify additional required flows?
3. Mac architecture/macOS version, Linux distro, Android models, active test camera
   count and availability of the existing Android signing key. Actual credentials
   and keys must be supplied through local secure input, never this document.

## Existing evidence and blockers

- Main includes Android FOLD/Standard v0.12.2 and Desktop/AI source.
- AI unit checks passed Windows and Linux; no macOS runner evidence exists yet.
- Android builds/tests/signature verification passed; artifact upload is blocked
  by GitHub Actions storage quota. A private Releases relay is not implemented yet.
- PR #9 has a README merge conflict; PR #10 is a separate draft lab service.
- Direct recheck of camera .14 did not verify HTTP/ONVIF or RTSP operation.
- Stable Android signing identity, macOS signing/notarization and physical test
  devices remain unresolved. They must not be silently replaced by temporary keys.
