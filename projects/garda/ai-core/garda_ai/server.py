"""Unified runtime entrypoint. Setup prompts locally; never put passwords on CLI."""
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="GARDA shared server")
    parser.add_argument("command", choices=("setup-user", "serve", "provision-opencv"))
    parser.add_argument("--data", default=os.environ.get("GARDA_AI_DATA_DIR", "./var"))
    parser.add_argument("--port", type=int, default=8808)
    parser.add_argument("--require-login", action="store_true", help="Use named sessions instead of the initial local Admin lab")
    args = parser.parse_args()
    root = Path(args.data).resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.command == "provision-opencv":
        from .provision import provision_opencv
        print(provision_opencv(root))
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
    app = create_app(root, unified=True, lab_no_login=not args.require_login)
    if args.require_login and not app.state.unified.identity.has_users():
        app.state.unified.close()
        raise RuntimeError("Create a named user with setup-user first")
    if not args.require_login:
        print("GARDA initial lab: local Admin, all roles available, login disabled.")
    uvicorn.run(app, host="127.0.0.1", port=args.port, access_log=False,
                proxy_headers=False, workers=1)


if __name__ == "__main__":
    main()
