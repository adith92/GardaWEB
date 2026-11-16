"""Safe operator-invoked ONVIF optical zoom. Does not move on API requests."""
from __future__ import annotations

import argparse
import os

from .zoom import ZoomController


def main():
    parser = argparse.ArgumentParser(description="GARDA ONVIF optical zoom check / bounded test")
    parser.add_argument("--host", required=True, help="Private camera IP only")
    parser.add_argument("--port", type=int, default=8899)
    parser.add_argument("--action", choices=("check", "in", "out"), default="check")
    parser.add_argument("--seconds", type=float, default=0.35)
    parser.add_argument("--speed", type=float, default=0.5)
    args = parser.parse_args()
    user = os.environ.get("GARDA_ONVIF_USER", "")
    password = os.environ.get("GARDA_ONVIF_PASS", "")
    if not user:
        parser.error("Set GARDA_ONVIF_USER, GARDA_ONVIF_PASS in your local environment")
    zoom = ZoomController(args.host, args.port, user, password)
    capabilities = zoom.inspect()
    print("ONVIF PTZ zoom capability:", capabilities)
    if args.action != "check":
        if not capabilities["zoom_supported"]:
            parser.error("Camera firmware does not advertise optical zoom")
        # Only explicit operator action; no automatic zoom based on a face/plate.
        result = zoom.pulse(args.action, args.seconds, args.speed)
        print(result)
        print("A camera ACK does not prove physical lens movement; observe live video.")


if __name__ == "__main__":
    main()
