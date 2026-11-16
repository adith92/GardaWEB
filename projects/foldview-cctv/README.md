# GARDA CCTV FOLD + Standard — development in GardaWEB

**Current location (16 November 2026):** private `adith92/GardaWEB`.
Android source is implemented at [android](android/README.md): **v0.12.2 / versionCode 16**, two flavors. The latest source includes the 14 November Android AI panel.

The source repository has successful debug CI builds; see [migration provenance](../../docs/GARDA_CCTV_MIGRATION_2026-11-16.md). A debug-signed build is not a production-signed release or physical-camera acceptance. Start at [projects/README.md](../README.md).

---

## Historical architecture proposal (8 November 2026)

The original proposal below predates the Android implementation. Its statements that source or APK builds do not exist are historical; use android/README.md and CHANGELOG.md for current code.

# FOLDVIEW CCTV — Galaxy Z Fold7 (V380 Pro alternative)

**Updated:** 2026-11-08 (Asia/Jakarta)  
**Repository:** private `adith92/docs`  
**Status:** Architecture and HTML mockup exist; **Android source/build has not been verified, and no signed Android APK exists yet.**  
**Source inspiration:** user's V380 Pro 2.2.92 APKM, inspected as reference; no redistribution of proprietary binaries or credentials.

## Product requirements (mandatory)

1. No advertisements, ad SDKs, ad ID, ad analytics, or mandatory cloud account.
2. Local-first ONVIF discovery + RTSP streaming, manual URL entry, H.264/H.265 subject to camera and device support.
3. Samsung Galaxy Z Fold7 adaptive layouts: compact cover and expanded unfolded screen; grid 1/4/9/16 with resource-aware stream allocation, flexible portrait/landscape/multiwindow, and camera-session preservation on fold/unfold.
4. Favor hardware decoding (Android MediaCodec + SurfaceView), avoiding pixel frame copies or full CPU decode; main stream only for selected camera, substream for grids, dynamic thermal/battery-aware decoder budget.
5. Rust for secure async ONVIF networking, WS-Discovery, SOAP/PTZ, camera/session logic and future desktop reuse; Kotlin for Android UI/lifecycle; Media3 RTSP first, GStreamer media fallback only when actual camera compatibility requires it.
6. Playback, PTZ, snapshots, 2-way audio, fisheye and V380 proprietary P2P/cloud features are **conditional** on camera firmware and authorized protocol support. Do not promise vendor-only features or undocumented cloud login replication.
7. Encrypt camera secrets with Android Keystore-backed encryption. Never log RTSP URLs containing credentials; never upload camera credentials or dumps; remote access via private VPN, not public RTSP port forwarding.
8. Run and test on real Fold7; no performance claim until streaming, decoder, memory, thermal and UI profiling is measured.

## Verified upstream stable baseline (checked 2026-11-08)

| Layer | Current reference | Implementation note |
|---|---|---|
| Android compile/target | API **37** (Android 17) | Request runtime `android.permission.ACCESS_LOCAL_NETWORK` when target 37+ and doing LAN ONVIF/RTSP. |
| Android Gradle Plugin | **9.5.1** | Official current stable API reference; requires Gradle **9.6.0+**. |
| Gradle | **9.6.0** minimum with AGP 9.5 | Use checked-in Gradle wrapper and dependency verification. |
| Kotlin language standalone | **2.4.21** latest stable reported by Kotlin | **Caution:** AGP 9+ enables built-in Kotlin. Do NOT blindly apply separate `org.jetbrains.kotlin.android` plugin; inspect AGP's bundled/compiler compatibility at build time. |
| Compose | BOM **2026.09.00** shown in official setup docs | Use stable BOM, not alpha/beta or dynamic `+` versions; refresh against Maven metadata before freezing a release. |
| Material3 | BOM-managed | Adaptive UI for Fold7. |
| Activity Compose | **1.13.0** | Validate compatibility with chosen AGP/Compose. |
| Lifecycle ViewModel Compose | **2.11.0** | Keep session state independent of Compose tree. |
| AndroidX Media3 | **1.11.1** | Use matching versions for `media3-exoplayer`, `media3-exoplayer-rtsp`, `media3-ui`; test H.264/H.265 on real hardware. |
| GStreamer, Rust, ONVIF libraries | **Select latest compatible stable at implementation** | Require version audit, native ABI compatibility, Android licensing review and reproducible pinning before release. No guessed version numbers. |
| Native architecture | **arm64-v8a** initially | Fold7-first. Other ABIs only if an explicit compatibility target is added. |

**Policy:** "latest" means latest **stable, security-supported, mutually compatible** release, not the highest preview. Pin exact versions in `gradle/libs.versions.toml`, lock native dependencies (e.g. `Cargo.lock`), and test upgrades before merge. Revalidate versions on every build/release, since this table is a 2026-11-08 snapshot.

### Android manifest for targetSdk 37+

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

Request ACCESS_LOCAL_NETWORK **at runtime** only when user initiates camera search/connect on a local network. Handle permission denied with useful UI. For older targets and Android versions, follow official compatibility behavior; do not request unrelated permissions by default.

## Release APK signing: required delivery gate

**Current status: NOT BUILT / NOT SIGNED.** A design prototype, an HTML file, an APKM from V380, or a Gradle config is **not** a signed FOLDVIEW APK.

An APK is considered ready to deliver only after all gates pass:

- [ ] Native Android project exists and compiles with compatible stable build tools.
- [ ] Physical Fold7 smoke tests: install, launch, cover/inner transitions, rotation, multi-window, ONVIF local permission, RTSP 1/4 tile, hardware decoder, reconnect.
- [ ] Gradle release task **`./gradlew clean assembleRelease`** succeeds with a persistent private **release keystore**.
- [ ] Signing credentials are provided privately at build time (CI secret/env or local secure storage); **never commit .jks, passwords, private keys or signing secrets** to GitHub.
- [ ] APK signed with v2/v3 Android signing schemes as applicable, using a consistent certificate across releases. Debug-signed packages are **not** production signed.
- [ ] Run `apksigner verify --verbose --print-certs app-release.apk`; require success, record signing certificate SHA-256 fingerprint (public metadata only).
- [ ] Run `sha256sum app-release.apk`; record artifact checksum, package name, versionCode, versionName, minimum SDK, target SDK, ABI, test date, and commit SHA.
- [ ] Run `zipalign -c -v 4 app-release.apk` and complete install/update test; ensure matching certificate for upgrade.
- [ ] Keep `.apk` output as release artifact (GitHub Release / protected CI artifact), **not merely a statement saying signed**.
- [ ] Check for ad SDKs/trackers, insecure camera logging, accidental telemetry, secret leakage, dependency and native license compliance.
- [ ] Automated release pipeline must FAIL if signing verification or certificate integrity check fails.

Example verification after successful build:

```bash
./gradlew clean assembleRelease
$ANDROID_HOME/build-tools/<installed-version>/apksigner verify --verbose --print-certs app/build/outputs/apk/release/app-release.apk
sha256sum app/build/outputs/apk/release/app-release.apk
```

No signing key has been created by this documentation. On initial internal testing a debug APK can be generated with Android tooling, but it must be labeled **debug** and never presented as production signed. Prefer user-controlled long-lived release keystore for future upgrades.

## Delivery acceptance

- [ ] Native app built and installable on Fold7.
- [ ] Signed release APK **verified**, not assumed.
- [ ] Folded/unfolded layouts verified.
- [ ] No ad/analytics SDKs or mandatory cloud sign-in.
- [ ] Confirm at least one authorized physical camera supports local RTSP/ONVIF; list any unsupported V380 vendor features.
- [ ] Hardware playback profiles and measured CPU/battery/thermals recorded.
- [ ] README, license/SBOM, change log and installation instructions.

## Primary sources

- Android Gradle Plugin current reference: https://developer.android.com/reference/tools/gradle-api
- AGP and Gradle compatibility: https://developer.android.com/build/releases/about-agp
- AGP 9 built-in Kotlin: https://developer.android.com/build/migrate-to-built-in-kotlin
- Kotlin releases: https://kotlinlang.org/docs/releases.html
- Compose setup and BOM: https://developer.android.com/develop/ui/compose/setup-compose-dependencies-and-compiler
- Media3 release notes: https://developer.android.com/jetpack/androidx/releases/media3
- Android 17 local network permission: https://developer.android.com/privacy-and-security/local-network-permission
- Signing build and verification: https://developer.android.com/build/building-cmdline
- apksigner reference: https://developer.android.com/tools/apksigner

## Progress tracking

**Next engineering milestone:** initialize Android source project and build first installable **debug** MVP, then provision release signing secrets and run verified **signed release APK** build. Do not mark deliverable "done" until an actual verified APK and checksum exist.