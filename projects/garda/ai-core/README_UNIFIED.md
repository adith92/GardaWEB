# GARDA shared server and five-platform workspace — v0.13.0 source candidate

Owner-selected lab target (16 November 2026): one local AI server, Windows/macOS
M1/Ubuntu/Android 13+/Web clients, minimum eight camera configurations, one-day
implementation priority. Packaging requires a separate pre-build confirmation.

## Source entrypoints

- Python: `python -m garda_ai.server` from this folder.
- Web: `/workspace` in the repository's React/Vite app.
- Windows/macOS/Ubuntu shared desktop client: root `desktop/`.
- Android: `projects/foldview-cctv/android`, FOLD/Standard v0.13.0 (17), minSdk 33.
  Native AI login and embedded Workspace use the same API; legacy direct-RTSP UI remains.
- The previous PySide6 desktop and legacy `/api` event API remain available.
  This does not merge the separate draft PR #10 scanner/service automatically.

## Server setup

Use Python 3.11+ in an isolated virtual environment:

```shell
python -m venv .venv
# Activate .venv according to the local OS.
python -m pip install -r requirements-unified.txt
python -m garda_ai.server serve
```

The initial `serve` mode opens directly as **Admin lokal, all role permissions**,
without login, per the owner's initial-lab instruction. It remains loopback-bound;
any device allowed through the private site gateway also receives Admin access.
For the later named-account mode use `setup-user`, then `serve --require-login`.

Setup prompts for username, role (admin/operator/viewer), and password without
command-line secrets. It stores salted scrypt hashes locally. Sessions expire
after eight hours, are revocable, and use bearer tokens for Android or HttpOnly
SameSite cookies plus CSRF protection for Web. There is no default password.

For localhost named-account Vite testing only, set `GARDA_COOKIE_SECURE=0`. Vite proxies
`/garda-api` to loopback 8808; use the same localhost name in browser and server.
For other devices, keep secure cookies enabled, set `GARDA_PUBLIC_ORIGIN` to the
actual HTTPS origin, and use `infra/unified/Caddyfile` from the repository root.
Set `GARDA_WEB_ROOT` to the eventual approved `dist/` directory. Caddy and the
loopback service run on the same host. This application does not require Internet
for existing provisioned model inference or local monitoring.

The Caddy private site CA must be explicitly trusted by each device. Android
supports an explicitly installed user CA; TLS certificate validation remains
enabled. The API never binds directly to public/LAN interfaces.

## Eight-camera workflow

1. Open `/workspace`; the initial lab enters local Admin without login. Eight unconfigured slots are created, all offline.
2. Admin: Perangkat → select slot → name, actual private-IP RTSP URL and providers.
   URLs/credentials are encrypted in `var/cameras.encrypted`; `var/camera.key`
   stays local. Back up the key and encrypted data together in protected storage.
3. Operator/admin: Live → Mulai. Capture uses a one-frame queue, timeouts, reconnect
   backoff and sampled inference. Live previews are bounded 640px JPEGs at up to
   2 fps per camera, fetched by clients periodically; this is not full-FPS video.
4. Status becomes online only after decoded fresh frames. Provider/configuration
   errors remain visible independently of camera online state. Stale frames are
   refused. Camera starts are explicit, not automatic after a server restart.
5. Search face/plate/motion events and open stored snapshots. Enrollment and
   revocation are admin-only; viewer cannot retrieve biometric/plate events.

Configuration supports 1–49 channels; the acceptance target is at least eight
real streams on the owner's hardware. Eight simultaneous decode/inference streams
have NOT been measured. Continuous video recording, retention/legal hold and NVR
failover are separate work; the live JPEG endpoint is not a recorder.

## Model adapters and provisioning

No weights are committed or fetched just by starting the server. Optional imports
are lazy. Provider catalog distinguishes installed, not-loaded and configuration
required states; loaded does not mean accuracy-certified.

| Adapter | Requirements |
|---|---|
| sface | OpenCV YuNet + SFace official local ONNX files |
| deepface | DeepFace dependency, SFace backend, and explicit `GARDA_DEEPFACE_ALLOW_MODEL_DOWNLOADS=1` for its managed model provisioning |
| insightface | InsightFace dependency + approved local recognition ONNX; `GARDA_INSIGHTFACE_MODEL_LICENSED=1` is an operator attestation, not a legal license grant |
| fastalpr | FastALPR with selected ONNX Runtime and locally audited detector/OCR model terms; `GARDA_FASTALPR_MODELS_APPROVED=1` enables its model provisioning |
| paddleocr | FastALPR detector crops + PaddleOCR 3.x and compatible PaddlePaddle runtime, under the same FastALPR provisioning opt-in |

For all face adapters: set `GARDA_FACE_YUNET_MODEL`, its
`GARDA_FACE_YUNET_MODEL_SHA256`, and a protected Fernet `GARDA_FACE_KEY`.
SFace additionally needs `GARDA_FACE_SFACE_MODEL` and `_SHA256`.
InsightFace additionally needs `GARDA_INSIGHTFACE_MODEL` and `_SHA256`.
Missing files/fingerprints or mismatches fail closed.

Install selected adapters in a separate controlled environment; see
`requirements-providers.txt`. Choose either CPU ONNX Runtime or a compatible
CUDA runtime, not two conflicting backend extras. CUDA/4070 SUPER throughput
and all optional provider dependency combinations still require testing.
DeepFace/Paddle/FastALPR may fetch dependencies/weights on explicit provisioning;
prepare verified caches before true offline operation.

Each face provider has its own encrypted gallery so embedding spaces cannot
silently be mixed. Enrollment requires a reference and exactly one face.
Cosine thresholds are per-provider and illustrative until calibrated locally.
Use authorized references and operator review of candidate matches.

## GitHub-backed Android OTA

The server's private Releases relay serves approved APKs through the same HTTPS
origin. Only the server holds `GARDA_GITHUB_READ_TOKEN` with repository Contents
read permission. `GARDA_RELEASE_REPOSITORY` defaults to `adith92/GardaWEB`.
Configure `var/updates.json` locally with `fold` and/or `standard` entries:

```json
{
  "fold": {
    "assetId": 123,
    "packageName": "org.foldview.cctv",
    "versionCode": 17,
    "versionName": "0.13.0",
    "sha256": "REPLACE_WITH_VERIFIED_64_HEX_DIGEST",
    "sizeBytes": 123456,
    "notes": "Approved internal build"
  }
}
```

The placeholder is intentionally invalid. Catalog entries must correspond to a
real approved GitHub Release asset. SHA/size are verified before serving.
Redirect hosts are allowlisted, and GitHub authorization is stripped on cross-host
redirects. Artifacts are cached privately. Client paths:
`/api/v1/updates/fold/manifest.json` or `/api/v1/updates/standard/manifest.json`.
Android connects to GARDA AI on that same origin (without login in initial lab); a named session, when enabled later, is never
sent to a different configured update host.

Owner has no previous Android signing key. Existing installations cannot be
updated in place with a new certificate. Export camera profiles using the old app
before uninstalling; passwords are not exported and must be re-entered. Provision
one persistent new key privately for subsequent internal releases. Configure Gradle
through `GARDA_ANDROID_KEYSTORE`, `GARDA_ANDROID_STORE_PASSWORD`,
`GARDA_ANDROID_KEY_ALIAS`, `GARDA_ANDROID_KEY_PASSWORD`. No keystore/password enters
Git. Desktop OTA is not implemented; desktop packages use manual distribution.

## Verification and build hold

Focused API tests cover role boundaries, CSRF, sessions, encrypted camera URLs,
eight offline slots, model fingerprints, event lookup and GitHub redirect/digest
failure. Existing vision tests use synthetic frames and mock engines. These are
not real model accuracy, eight-camera load, Mac M1 UI or physical Android tests.

CI runs source checks, Android unit compilation/tests and Python tests on Windows,
Ubuntu and macOS. APK assembly/upload is gated by workflow_dispatch with
`approved_build=true`; source archive upload is optional. This branch disables
Vercel auto-preview. Do not run production web/desktop/APK packaging before the
owner's requested confirmation. Builds do not by themselves approve a release.

Owner-approved desktop/Web packaging is prepared in `.github/workflows/garda-approved-packages.yml`, with an explicit false-by-default dispatch input. Android packaging uses its separate guarded workflow. These workflows have not been dispatched. GitHub artifact quota may still block uploads even if packaging succeeds.
