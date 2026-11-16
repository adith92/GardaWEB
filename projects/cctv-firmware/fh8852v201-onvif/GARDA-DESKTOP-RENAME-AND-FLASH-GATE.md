# GARDA DESKTOP — rename brief for local Antigravity agent

Target local Windows project:
`C:\\Users\\adith\\OneDrive\\Desktop\\CleanTV\\`
User says `RUN.BAT` already launches the current desktop camera application.

**This repository does not contain or claim to inspect the local Windows project.**
An offline/missing Windows desktop connector prevents directly renaming/running `RUN.BAT` from ChatGPT.

## Antigravity action request
1. Open the existing CleanTV folder, inspect `RUN.BAT` and source entrypoint.
2. Rename the **user-visible desktop application identity** to **GARDA DESKTOP**: main window title, login/landing branding, tray label, executable / shortcut display name if the build supports it, About screen, and installer metadata. Do not rename the Android **FOLDVIEW CCTV** app, its package ID or its Keystore alias.
3. Preserve existing configs, local camera profiles, API endpoints, startup behavior, passwords and database files. Do not rename internal module imports unless necessary.
4. Confirm `RUN.BAT` still starts the app, that camera discovery and RTSP/ONVIF still function, and that old user data remains intact.
5. Take a dated backup of the project before code modifications. Write a simple repeatable smoke test and return changed filenames plus verified screenshots/log output.
6. Do not flash CCTV firmware as part of a desktop application rename.

## Flash gate for Fullhan FH8852V201
- User's FH8852V201 board is not currently a verified ready-to-flash OpenIPC device.
- A previously claimed dual verified MTD backup, board-specific validated firmware image, and **recovery over LAN alone** have not been demonstrated.
- If LAN is the only management path, a failed boot/ethernet update can permanently eliminate remote recovery. Do not issue `flash_erase`, `mtd write`, `dd of=/dev/mtd*`, `fw_setenv`, or bootloader changes automatically.
- Independent verify #1: board/SoC/sensor/SPI layout match with trustworthy image release and immutable SHA256 hash.
- Independent verify #2: full flash backup per partition, repeated read/hash comparison, restoration plan with off-device copy and verified recovery equipment (UART/SPI).
- Add native ONVIF by reversible RAM-only daemon trial first. Require a separate explicit approval to flash the exact proven image after both gates.
- `192.168.18.232` and `192.168.18.233`: ONVIF 8899 + RTSP 554 reportedly present; root, SoC and custom firmware capability unknown. Open ports do not imply firmware compatibility.

Use project issue tracking; never upload user passwords, raw firmware dumps with credentials, or camera video to GitHub.
