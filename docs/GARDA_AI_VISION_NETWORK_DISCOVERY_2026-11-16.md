# GARDA AI Vision | Self-service LAN scanner (2026-11-16)

Status: **IMPLEMENTED in source, unit/API tested with fake local interface and fake probes; NOT RUN against the user's camera or LAN.** This is a Windows-first / Linux-ready development component. No network credentials, actual camera IPs, MAC addresses or government network details are committed.

## Source and audit provenance

The user-provided Antigravity report lists open ports on a private-lab camera. The report is **not independently verified** by this environment. It is a test scenario, not a true ground-truth service inventory:

- `21` FTP candidate (`220` greeting would verify FTP only)
- `23` Telnet candidate; port open does not prove shell or account access
- `1111` HTTP candidate; `Server: MJPG-Streamer/0.2` supports MJPEG streaming-server classification if observed directly
- `8899` ONVIF candidate; ONVIF WS-Discovery/authorized GetCapabilities required for verification
- Other vendor/private-service port examples include 1234/1235, 6666/7777/8888 and 10055/10067. Do not assert they are video/cloud P2P protocols based solely on a port number.
- MAC addresses with locally administered bits cannot reliably identify a vendor OUI.

## Components

- `scanner.py`: private-only interface enumeration, CIDR/single-host validation, TCP connection/optional HTTP HEAD/RTSP OPTIONS/FTP greeting, optional UDP ONVIF WS-Discovery, passive ARP cache, classification with evidence, asynchronous job manager.
- `api.py`: admin-only, `GARDA_NETWORK_SCAN_ENABLED=1` opt-in, owner authorization checkbox, one scan at a time, HTTP 202 and result/status/history endpoints, audited API activity.
- `storage.py`: Fernet encryption for scan result and scope, local SQLite persistence; neither real camera IPs nor credentials in repository.
- `src/GardaVisionWorkbench.tsx`: NIC selection, quick/extended mode, targeted scan field, authorization confirmation, progress polling and review of scan results.
- `tests/test_scanner.py`: mocked LAN interfaces/probes, scope rejection, RBAC and authorization checks, async result polling, encrypted persistence and disabled-by-default scanning.

## Future audit gates

1. Validate Windows 11 source runtime with actual installed Python/FFmpeg; this environment cannot connect to the target LAN.
2. Test at most one authorized camera initially; verify expected port/banner matches scan report and ensure no device instability.
3. Confirm exact ONVIF Device Management URL and credentials with read-only `GetCapabilities/GetProfiles/GetStreamUri` and independently verify RTSP decode and optical zoom capability.
4. Build an explicitly approved registry/enrollment path that stores credentials in secure local secrets store, not source code or browser.
5. Add retention controls, named-user RBAC, MFA, bind-to-site-scoped authorization, TLS/VPN, tamper-evident audit trails and network rate limiting before production.
6. Measure false-positive detection, Windows Firewall effects, multicast blocked cases, cameras on VLANs, offline behavior and load under 16 video channels.
7. Never confuse the local discovery service with a redundant VMS/NVR or 90-day recording fulfillment.

## Terminology

- `camera_evidence`: protocol evidence suggests a CCTV/stream device (e.g., actual RTSP response, MJPEG server header, WS-Discovery ProbeMatch).
- `possible_camera`: plausible open CCTV ports, identity unverified.
- `other_device`: open TCP port(s) but no camera-specific evidence.
- `onvif_ws_discovery`: WS-Discovery ProbeMatch observed from IP; does **not** guarantee ONVIF PTZ support.
