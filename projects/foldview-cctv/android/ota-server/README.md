# GARDA CCTV FOLD edition: private LAN OTA

## Update features
- In Settings > About GARDA: real Android version and build number, developer Adithya Pratama, For internal use only.
- In Settings > App updates: Check for updates, Download update with progress, Install verified APK.
- Android confirmation is mandatory; never silently install or overwrite an application.
- Release manifest is hosted by a private Windows GARDA Desktop helper, not GitHub public release (adith92/GardaWEB is private).
- The Google Drive releases button opens the authenticated Drive folder as a manual backup path.

## Set up on Windows
1. Download the newest APK from https://drive.google.com/drive/folders/10CH9pSvjcSp7QoKv4nKdv2W5ePbHti9a
2. Keep that APK in a private Windows folder such as C:\GARDA\releases.
3. Run ipconfig to identify your PC's CURRENT LAN IPv4 address. It might differ from 192.168.18.3.
4. Navigate to projects/foldview-cctv/android/ota-server in the source repository.
5. Start the server (replace PC_IP and file path):

    py -3.11 garda_ota_server.py --bind PC_IP --port 8877 --apk C:\GARDA\releases\GARDA-CCTV-FOLD-edition-v0.10.0-DEBUG-SIDELOAD.apk --version-code 12 --version-name 0.10.0

6. Restrict Windows Firewall inbound TCP 8877 to your authorized CCTV Wi-Fi/LAN range. Never port-forward it.
7. On Fold: Settings > App updates > set http://PC_IP:8877/manifest.json
8. Press Check for updates; if release versionCode is higher, download and install the verified APK.

## Release contract
GET /manifest.json returns JSON with: packageName = org.foldview.cctv, versionCode = integer, versionName = string, sizeBytes, sha256, apkUrl, notes.
GET /GARDA-update.apk returns exactly the APK whose digest and file size the JSON declares.
The client accepts no cross-host redirect, only HTTPS or HTTP on private IPv4 LAN, max 200 MiB, SHA256, expected package ID, versionCode and matching certificate.

## Important signing limitation
All previous GitHub-hosted CI debug APKs were built using ephemeral debug signing certificates. A newly generated debug APK has a different certificate, so Android will NOT allow an in-place update over the previous build.
The OTA client deliberately blocks this case before Android's package installer. Do not uninstall until camera profiles are backed up; uninstalling deletes Keystore-encrypted camera settings.
For truly seamless OTA going forward, generate a stable release signing keystore owned by Adithya and back it up securely OFF GitHub. Add its material and password to encrypted GitHub Actions secrets, and reconfigure CI to sign every release with the SAME certificate. You may need a one-time manual migration from the current debug build.

## Security / deployment boundary
- Server defaults to 127.0.0.1; binding an actual LAN IP is a conscious operator action. It is not deployed automatically to CleanTV/GARDA Desktop.
- The server currently does not authenticate clients, and HTTP traffic is not encrypted. Use it ONLY on a trusted isolated network with inbound firewall restrictions.
- No APK is published publicly or shared outside Drive. Device requires connection to trusted LAN and the PC OTA server must be running.
- The application is still native Kotlin/Jetpack Compose, not a web app. Update checks and downloads use IO background workers and show progress immediately.
- Google Drive is the primary private file archive; private Drive links are not anonymous raw APK CDN URLs.

## Status
Code and build automated tests do not equal proof of field update installation. Verify live against Fold7, stable signing, and GARDA Desktop PC after setup.

## Two APK editions (v0.12.0)
The Python OTA server now accepts `--package-name`. For a Fold edition release use `--package-name org.foldview.cctv` (default). For Standard edition use `--package-name org.garda.cctv.standard`. Because the package names differ, a Standard app will reject a Fold manifest (and vice versa). Use separate local ports, e.g., 8877 Fold, 8878 Standard, or run one edition at a time. Download the correct edition ZIP/APK from the GARDA releases Drive folder, never publish the private GitHub repo. Retain the user's release signing keys securely off GitHub.
