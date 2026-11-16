# FH8852V201 Native ONVIF Daemon — Experimental Source

**This is NOT a flashable firmware image, NOT production ready, and NOT an approved install.** The exact camera board and vendor uClibc toolchain have not been tested. The Windows CleanTV host was inaccessible in this chat, so no image was flashed, no camera MTD was read or verified, and no direct-camera build or runtime success can be claimed.

## Purpose
Add a standalone, low-dependency C SOAP/WS-Discovery process to the **stock** FH8852V201 firmware, without replacing the existing `sample_vlcview` video streamer. By default, maps the already observed vendor RTSP ports `1234` and `1235`. Tests on Ubuntu verify protocol XML only, **not real hardware**.

Implements:
- WS-Discovery ProbeMatch UDP 3702 (multicast membership)
- Device GetDeviceInformation, GetCapabilities, GetServices, GetScopes, GetSystemDateAndTime (time value intentionally incomplete)
- Media GetProfiles / GetStreamUri, main/sub RTSP pointers
- No real PTZ, microphone/speaker, recording, Profile G, video encoder control or camera configuration

The implementation uses a simplified read-only SOAP dispatch and lacks WS-Security. **Do not expose this service to the internet or untrusted LAN.** ONVIF compatibility with real clients is not certified. It is intended for lab validation of the communications path only; enabling it may leak camera endpoints. Never advertise PTZ control when not implemented.

## Host-only smoke test
```sh
make
make test
```
The resulting executable is for your **host** CPU and must NOT be copied to the ARM camera.

## Build for the FH8852V201
- Obtain the matching Fullhan ARMv7 **uClibc** toolchain and verify the ELF interpreter and ARM EABI on the original camera.
- Compile with e.g. `make CC=<verified-armv7-uclibc-gcc>`.
- Inspect `file foldview_onvifd`, `readelf -h`, `readelf -l` and its runtime library dependencies.
- Keep it entirely off permanent flash; transfer into an existing RAM filesystem (if sufficient capacity), run with `--ip <verified-camera-ip> --http-port 8899`, then stop/kill it and verify the original vendor process is unaffected.
- A single built-in UUID is used for prototyping only. Before multi-camera deployment generate a unique, stable endpoint UUID for each camera.
- The new daemon is **not** an independent video encoder. It only publishes the current vendor RTSP stream.
- No persistence/init modification, MTD write, bootloader change or firmware replacement is implemented.

## Required dual verification before any future firmware flash
1. Verified **device-specific** hardware/firmware match: exact FH8852V201 revision, board/sensor, bootloader, partition layout, image hash and trusted provenance.
2. Verified **off-device** backups of all MTD partitions: two independent reads with equal sizes/checksums, plus real UART/SPI recovery equipment/procedure.

**Neither gate is currently passed.** If recovery is only via LAN, flashing is NOT approved because a damaged kernel or network driver cannot be recovered remotely.

See `GARDA-DESKTOP-RENAME-AND-FLASH-GATE.md` for instructions to Antigravity to rename the existing Windows CleanTV app to GARDA DESKTOP and report results.
