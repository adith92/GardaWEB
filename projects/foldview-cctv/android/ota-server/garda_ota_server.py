#!/usr/bin/env python3
"""Private GARDA update server for a trusted owned CCTV LAN.

Example:
  py -3.11 garda_ota_server.py --bind 192.168.18.3 --port 8877 --apk "C:\GARDA\release.apk" --version-code 12 --version-name 0.10.0

Do not expose port 8877 to the internet.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def build_manifest(apk: Path, host: str, port: int, code: int,
                   version: str, notes: str = "", package_name: str = "org.foldview.cctv") -> dict:
    if code <= 0 or not version or len(version) > 48:
        raise ValueError("Invalid versionCode/versionName")
    if apk.suffix.lower() != ".apk" or not apk.is_file():
        raise ValueError("Select an existing GARDA .apk file")
    size = apk.stat().st_size
    if size < 100_000 or size > 200 * 1024 * 1024:
        raise ValueError("Unexpected APK size")
    digest = hashlib.sha256()
    with apk.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "packageName": package_name,
        "versionCode": code,
        "versionName": version,
        "sizeBytes": size,
        "sha256": digest.hexdigest(),
        "apkUrl": f"http://{host}:{port}/GARDA-update.apk",
        "notes": notes,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="GARDA private LAN OTA host")
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8877)
    ap.add_argument("--apk", type=Path, required=True)
    ap.add_argument("--version-code", required=True, type=int)
    ap.add_argument("--version-name", required=True)
    ap.add_argument("--notes", default="GARDA CCTV internal update")
    ap.add_argument("--package-name", choices=["org.foldview.cctv", "org.garda.cctv.standard"],
                    default="org.foldview.cctv")
    args = ap.parse_args()
    ip = ipaddress.ip_address(args.bind)
    if not isinstance(ip, ipaddress.IPv4Address) or (
        not ip.is_loopback and not ip.is_private
    ):
        ap.error("Bind a specific private IPv4 address or 127.0.0.1")
    if not (1024 <= args.port <= 65535):
        ap.error("Port must be 1024..65535")
    if len(args.notes) > 900:
        ap.error("Release notes too long")
    apk = args.apk.expanduser().resolve()
    data = build_manifest(apk, args.bind, args.port, args.version_code,
                          args.version_name, args.notes, args.package_name)
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    if len(body) > 16_384:
        ap.error("Manifest too large")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/manifest.json":
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/GARDA-update.apk":
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.android.package-archive")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(data["sizeBytes"]))
                self.end_headers()
                try:
                    with apk.open("rb") as fp:
                        for chunk in iter(lambda: fp.read(65_536), b""):
                            self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.send_error(404, "Not found")

        def log_message(self, fmt: str, *values):
            print("%s %s" % (self.address_string(), fmt % values), flush=True)

    server = ThreadingHTTPServer((args.bind, args.port), Handler)
    server.daemon_threads = True
    print("GARDA OTA: http://%s:%s/manifest.json" % (args.bind, args.port), flush=True)
    print("Version %s build %s, SHA-256 %s" % (
        args.version_name, args.version_code, data["sha256"]), flush=True)
    server.serve_forever(poll_interval=0.25)


if __name__ == "__main__":
    main()
