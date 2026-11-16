# GARDA Workspace desktop client v0.13.0

One shared React workspace in a sandboxed Electron shell for Windows x64,
Apple Silicon macOS arm64 (including M1), and Ubuntu x64. Camera/AI work runs
on the owner's Windows/Linux server, not inside the client package.

The first-run screen accepts the trusted GARDA HTTPS origin. `GARDA_WEB_URL`
can provide the same origin for a managed installation. Only the server address
is saved; login sessions are handled by the server/browser cookie store.
Node integration is disabled; navigation, popup and permission requests are restricted.

## Development checks (no installer build)

```shell
node --test policy.test.cjs
npm ci
npm start
```

The shared web app must already be available at the selected address, or run Vite
for local testing (`http://127.0.0.1:5173`). Connect to `/workspace`.

## After owner confirms packaging

Run on each target OS using the committed lockfile:

| OS | Command | Planned output |
|---|---|---|
| Windows x64 | npm run package:windows | NSIS EXE |
| Apple Silicon macOS | npm run package:mac | arm64 DMG |
| Ubuntu x64 | npm run package:linux | AppImage and DEB |

Release signing/notarization credentials are supplied outside Git. Internal
unsigned/ad-hoc packages are not a notarized or publicly trusted production release.
No package command has been executed as part of source preparation.
