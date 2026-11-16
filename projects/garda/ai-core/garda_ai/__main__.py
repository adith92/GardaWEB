from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from .config import load_config
from .storage import EventStore


def main():
    parser = argparse.ArgumentParser(description="GARDA AI Core on-premises stage 1")
    parser.add_argument("command", choices=("run", "api", "purge", "check", "enroll", "revoke", "face-keygen"))
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8808)
    parser.add_argument("--name", help="Consent-based subject label; enroll only")
    parser.add_argument("--image", help="Local image with one person; enroll only")
    parser.add_argument("--consent-ref", help="Recorded permission/reference, not a secret")
    parser.add_argument("--face-id", help="Face gallery record to revoke")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.command == "face-keygen":
        from cryptography.fernet import Fernet
        print(Fernet.generate_key().decode("ascii"))
        return
    if args.command == "enroll":
        if not all([args.name, args.image, args.consent_ref]):
            parser.error("enroll requires --name, --image, --consent-ref")
        config = load_config(args.config)
        if not config.face_model or not config.recognition_model:
            parser.error("Set GARDA_FACE_YUNET_MODEL and GARDA_FACE_SFACE_MODEL")
        from .recognition import enroll_image
        new_id = enroll_image(Path(args.image), args.name, args.consent_ref,
                              config.face_model, config.recognition_model,
                              config.data_dir, os.environ.get("GARDA_FACE_KEY", ""))
        print("Encrypted face template enrolled ID:", new_id)
        return
    if args.command == "revoke":
        if not args.face_id:
            parser.error("revoke requires --face-id")
        from .recognition import FaceGallery
        gallery = FaceGallery(Path(os.environ.get("GARDA_AI_DATA_DIR", "./var")),
                              os.environ.get("GARDA_FACE_KEY", ""))
        try:
            print("Revoked" if gallery.revoke(args.face_id) else "Not found")
        finally:
            gallery.close()
        return
    if args.command in ("run", "check"):
        config = load_config(args.config)
        print(f"Configured {len(config.cameras)} camera(s), data={config.data_dir}, retention={config.retention_days} days")
        if args.command == "run":
            from .runner import run
            run(config)
    elif args.command == "api":
        if args.listen not in ("127.0.0.1", "::1", "localhost"):
            raise RuntimeError("API must bind to loopback; use a secured TLS/VPN reverse proxy")
        from .api import create_app
        import uvicorn
        app = create_app()
        uvicorn.run(app, host=args.listen, port=args.port, access_log=False)
    elif args.command == "purge":
        cfg = load_config(args.config)
        store = EventStore(cfg.data_dir)
        print(store.purge(cfg.retention_days))
        store.close()


if __name__ == "__main__":
    main()
