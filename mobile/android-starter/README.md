# GARDA Android starter, NOT a complete app

`GardaVisionClient.kt` is a **source-only** Kotlin API consumer showing read-only camera discovery for a future native GARDA Android app. Existing `adith92/GardaWEB` contains Android/mobile PRDs and SVGs, not a built native project. It is not accurate to say an Android integration/APK was completed.

Requires Kotlin coroutines, a proper Android project and per-device/user login. Must operate through site-scoped HTTPS with certificate verification and on-prem VPN. Use role/site checks on every request, remove long-lived static tokens before deployment, and never embed CCTV network routes, models, face embeddings or credentials in the APK.

Do not repackage ClearCam's GPL Android application into GARDA proprietary software without a license review. Design GARDA FIELD (T3) or separate KAK-authorized mobile viewer in subsequent work.
