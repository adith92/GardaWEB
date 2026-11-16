"""Authenticated private GitHub Release relay; GitHub credentials never reach clients."""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from urllib.parse import urlsplit

import httpx
from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse

CHANNELS = {"fold": "org.foldview.cctv", "standard": "org.garda.cctv.standard"}
GITHUB_HOSTS = {"api.github.com", "github.com", "release-assets.githubusercontent.com",
                "objects.githubusercontent.com"}


class ReleaseCache:
    def __init__(self, root):
        self.root = root
        self.lock = threading.Lock()

    def entry(self, channel):
        if channel not in CHANNELS:
            raise ValueError("Unknown update channel")
        catalog = self.root / "updates.json"
        if not catalog.is_file():
            raise FileNotFoundError("No approved releases configured")
        entry = json.loads(catalog.read_text())[channel]
        if (entry["packageName"] != CHANNELS[channel] or
                not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) or
                not 0 < int(entry["sizeBytes"]) <= 200*1024*1024 or
                int(entry["versionCode"]) <= 0 or int(entry["assetId"]) <= 0):
            raise ValueError("Invalid release catalog")
        return entry

    def fetch(self, entry):
        repo = os.environ.get("GARDA_RELEASE_REPOSITORY", "adith92/GardaWEB")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise ValueError("Invalid release repository")
        token = os.environ.get("GARDA_GITHUB_READ_TOKEN", "")
        if not token:
            raise RuntimeError("Configure server-only GitHub read access")
        target = self.root / (entry["sha256"] + ".apk")
        with self.lock:
            if target.is_file() and target.stat().st_size == entry["sizeBytes"]:
                if hashlib.sha256(target.read_bytes()).hexdigest() == entry["sha256"]:
                    return target
            url = f"https://api.github.com/repos/{repo}/releases/assets/{int(entry['assetId'])}"
            headers = {"Accept": "application/octet-stream", "Authorization": "Bearer " + token}
            part = target.with_suffix(".part")
            try:
                with httpx.Client(follow_redirects=False, timeout=30) as client:
                    for _ in range(5):
                        parsed = urlsplit(url)
                        if parsed.scheme != "https" or parsed.hostname not in GITHUB_HOSTS or parsed.username:
                            raise ValueError("Release redirect host is not trusted")
                        with client.stream("GET", url, headers=headers) as response:
                            if response.status_code in (301, 302, 303, 307, 308):
                                from urllib.parse import urljoin
                                next_url = urljoin(url, response.headers["location"])
                                if urlsplit(next_url).hostname != parsed.hostname:
                                    headers = {"Accept": "application/octet-stream"}
                                url = next_url
                                continue
                            response.raise_for_status()
                            digest, count = hashlib.sha256(), 0
                            fd = os.open(part, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                            with os.fdopen(fd, "wb") as output:
                                for chunk in response.iter_bytes(65536):
                                    count += len(chunk)
                                    if count > entry["sizeBytes"]:
                                        raise ValueError("Release exceeds approved size")
                                    digest.update(chunk)
                                    output.write(chunk)
                            if count != entry["sizeBytes"] or digest.hexdigest() != entry["sha256"]:
                                raise ValueError("Release checksum/size mismatch")
                            os.replace(part, target)
                            return target
                    raise RuntimeError("Too many release redirects")
            finally:
                part.unlink(missing_ok=True)


def install_updates(app, service, root):
    cache = ReleaseCache(root)
    guard = service.require("admin", "operator")

    def approved(channel):
        try:
            return cache.entry(channel)
        except (FileNotFoundError, KeyError):
            raise HTTPException(404, "No approved release for this channel")
        except (ValueError, TypeError):
            raise HTTPException(503, "Release catalog needs local configuration")

    @app.get("/api/v1/updates/{channel}/manifest.json")
    def manifest(channel: str, actor=Depends(guard)):
        entry = approved(channel)
        origin = service.allowed_origin
        if not origin or urlsplit(origin).scheme != "https":
            raise HTTPException(503, "Configure the GARDA HTTPS public origin first")
        return {k: entry[k] for k in ("packageName", "versionCode", "versionName", "sha256", "sizeBytes")} | {
            "notes": str(entry.get("notes", ""))[:900],
            "apkUrl": origin + f"/api/v1/updates/{channel}/package.apk"}

    @app.get("/api/v1/updates/{channel}/package.apk")
    def package(channel: str, actor=Depends(guard)):
        try:
            path = cache.fetch(approved(channel))
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(503, "Approved package unavailable; inspect local release relay")
        return FileResponse(path, media_type="application/vnd.android.package-archive")
