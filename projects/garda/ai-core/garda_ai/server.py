"""Unified runtime entrypoint. Setup prompts locally; never put passwords on CLI."""
from __future__ import annotations

import argparse
import getpass
import os
import json
from pathlib import Path
from urllib.parse import urlsplit


def validate_protected_launch(origin: str, cookie_secure: bool) -> None:
    """Preflight for an authenticated LAN deployment; not a production certification."""
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or
            parsed.password or parsed.path not in ("", "/") or parsed.query or
            parsed.fragment or not parsed.netloc):
        raise RuntimeError("Protected mode requires GARDA_PUBLIC_ORIGIN=https://trusted-host (no path)")
    if not cookie_secure:
        raise RuntimeError("Protected mode refuses GARDA_COOKIE_SECURE=0")



def main():
    parser = argparse.ArgumentParser(description="GARDA shared server")
    parser.add_argument("command", choices=("setup-user", "serve", "provision-opencv", "provision-ai", "configure-nvr", "configure-https"))
    parser.add_argument("--data", default=os.environ.get("GARDA_AI_DATA_DIR", "./var"))
    parser.add_argument("--port", type=int)
    parser.add_argument("--host")
    parser.add_argument("--web-root")
    parser.add_argument("--require-login", action="store_true", help="Use named sessions instead of the initial local Admin lab")
    parser.add_argument("--protected", action="store_true", help="Require named login and HTTPS origin in controlled pilot")
    parser.add_argument("--nvr-binary")
    parser.add_argument("--recordings-root")
    parser.add_argument("--retention-days", type=int, default=1)
    args = parser.parse_args()
    root = Path(args.data).resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    settings_file = root / "server-settings.json"
    settings = json.loads(settings_file.read_text(encoding="utf8")) if settings_file.is_file() else {}
    if args.command == "configure-nvr":
        import hashlib
        from .recorder import prepare_storage
        if not args.nvr_binary or not args.recordings_root or not 1 <= args.retention_days <= 90:
            parser.error("configure-nvr requires --nvr-binary, --recordings-root, retention 1..90 days")
        binary = Path(args.nvr_binary).resolve()
        storage = prepare_storage(args.recordings_root)
        settings.update({"GARDA_NVR_BINARY": str(binary), "GARDA_NVR_BINARY_SHA256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                    "GARDA_RECORDINGS_ROOT": str(storage), "GARDA_RETENTION_DAYS": str(args.retention_days)})
        settings_file.write_text(json.dumps(settings, indent=2), encoding="utf8")
        settings_file.chmod(0o600)
        print("NVR configured; recording starts with the server, independently of AI.")
        return
    if args.command == "configure-https":
        from .tls import provision_tls
        if not args.host or not args.web_root or not (Path(args.web_root)/"index.html").is_file():
            parser.error("configure-https requires --host LAN-IP and --web-root built-Web-folder")
        tls = provision_tls(root, args.host)
        port = args.port or 8843
        if not 1 <= port <= 65535:
            parser.error("Invalid HTTPS port")
        settings.update({"GARDA_SSL_CERTFILE":tls["cert"],"GARDA_SSL_KEYFILE":tls["key"],
            "GARDA_BIND_HOST":args.host,"GARDA_PORT":str(port),"GARDA_WEB_ROOT":str(Path(args.web_root).resolve()),
            "GARDA_PUBLIC_ORIGIN":f"https://{args.host}:{port}"})
        settings_file.write_text(json.dumps(settings,indent=2),encoding="utf8")
        settings_file.chmod(0o600)
        print("HTTPS configured. Install site CA on client devices: "+tls["ca"])
        return
    if settings_file.is_file():
        for name, value in json.loads(settings_file.read_text(encoding="utf8")).items():
            if name in {"GARDA_NVR_BINARY", "GARDA_NVR_BINARY_SHA256", "GARDA_RECORDINGS_ROOT", "GARDA_RETENTION_DAYS",
                        "GARDA_SSL_CERTFILE", "GARDA_SSL_KEYFILE", "GARDA_BIND_HOST", "GARDA_PORT", "GARDA_WEB_ROOT", "GARDA_PUBLIC_ORIGIN"}:
                os.environ.setdefault(name, str(value))
    if args.command in ("provision-opencv", "provision-ai"):
        from .provision import provision_opencv
        print(provision_opencv(root))
        if args.command == "provision-ai":
            from .provision import provision_plates
            print(provision_plates(root))
        return
    if args.command == "setup-user":
        from .auth import Identity
        identity = Identity(root)
        try:
            name = input("Username: ").strip()
            role = input("Role (admin/operator/viewer): ").strip()
            password = getpass.getpass("Password (12+ characters): ")
            if password != getpass.getpass("Repeat password: "):
                raise ValueError("Passwords differ")
            identity.add_user(name, password, role)
            print("User created. Credentials were not stored in source.")
        finally:
            identity.close()
        return
    # Native FFmpeg diagnostics must not leak credential-bearing RTSP URLs.
    os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "-8")
    from .provision import local_models
    local_models(root)
    from .api import create_app
    import uvicorn
    if args.protected:
        validate_protected_launch(os.environ.get("GARDA_PUBLIC_ORIGIN", ""),
                                  os.environ.get("GARDA_COOKIE_SECURE", "1") != "0")
    named_login = args.require_login or args.protected
    app = create_app(root, unified=True, lab_no_login=not named_login)
    web = args.web_root or os.getenv("GARDA_WEB_ROOT")
    if web:
        from .gateway import install_web
        install_web(app, web)
    if named_login and not app.state.unified.identity.has_users():
        app.state.unified.close()
        raise RuntimeError("Create a named user with setup-user first")
    if not named_login:
        print("GARDA initial lab: local Admin, all roles available, login disabled.")
    if args.protected:
        print("GARDA controlled LAN pilot: named sessions and secure origin enabled")
    host = args.host or os.getenv("GARDA_BIND_HOST", "127.0.0.1")
    cert, key = os.getenv("GARDA_SSL_CERTFILE"), os.getenv("GARDA_SSL_KEYFILE")
    if host != "127.0.0.1" and not (cert and key):
        raise RuntimeError("Configure HTTPS before binding to the LAN")
    uvicorn.run(app, host=host, port=args.port or int(os.getenv("GARDA_PORT", "8808")), access_log=False,
                proxy_headers=False, workers=1, ssl_certfile=cert, ssl_keyfile=key)


if __name__ == "__main__":
    main()
