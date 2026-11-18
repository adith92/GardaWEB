"""Supervise an independent, locally compiled MediaMTX recorder. AI never owns its lifetime."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import httpx

CAMERA_ID = re.compile(r"[A-Za-z0-9_-]{1,40}")


def engine_config(root, retention_days=1):
    """Only loopback listeners. URLs are configured in memory via the local control API."""
    return {"logLevel": "error", "api": True, "apiAddress": "127.0.0.1:9997",
        "playback": True, "playbackAddress": "127.0.0.1:9996",
        "rtsp": True, "rtspAddress": "127.0.0.1:8554", "rtspTransports": ["tcp"],
        "rtmp": False, "hls": False, "webrtc": False, "srt": False, "moq": False,
        "authInternalUsers": [{"user": "any", "pass": "", "ips": ["127.0.0.1"],
            "permissions": [{"action": action} for action in ("api", "read", "playback")]}],
        "pathDefaults": {"sourceOnDemand": False, "record": True,
            "recordPath": (root / "video" / "%path" / "%Y-%m-%d_%H-%M-%S-%f_%z").as_posix(),
            "recordFormat": "fmp4", "recordPartDuration": "1s", "recordMaxPartSize": "8M",
            "recordSegmentDuration": "1m", "recordDeleteAfter": f"{retention_days}d",
            "rtspTransport": "tcp"}, "paths": {}}


def prepare_storage(root):
    root = Path(root).expanduser().resolve()
    if root == Path(root.anchor):
        raise ValueError("Use a dedicated recording folder, not the drive root")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    marker = root / ".garda-recordings"
    video = root / "video"
    if video.exists() and not marker.is_file():
        raise ValueError("Existing video directory has no GARDA ownership marker")
    if video.is_symlink() or (video.exists() and video.resolve().parent != root):
        raise ValueError("Recording directory must stay inside the managed folder")
    marker.touch(mode=0o600, exist_ok=True)
    video.mkdir(mode=0o700, exist_ok=True)
    return root


class Recorder:
    def __init__(self, root, runtime, binary=None, directory=None, retention_days=1):
        self.root, self.runtime = Path(root), runtime
        self.binary = str(binary or os.getenv("GARDA_NVR_BINARY", ""))
        self.expected_hash = os.getenv("GARDA_NVR_BINARY_SHA256", "").lower()
        self.directory = str(directory or os.getenv("GARDA_RECORDINGS_ROOT", ""))
        self.retention = int(os.getenv("GARDA_RETENTION_DAYS", retention_days))
        if not 1 <= self.retention <= 90:
            raise ValueError("Retention must be 1..90 days")
        self.reserve = max(1024**3, int(os.getenv("GARDA_DISK_RESERVE_BYTES", str(10*1024**3))))
        self.stop = threading.Event()
        self.lock = threading.RLock()
        self.process, self.thread = None, None
        self.applied, self.sources = {}, {}
        self.state = {"status": "configuration_required", "engine": "MediaMTX", "engine_version": "1.21.4",
                      "retention_days": self.retention, "restart_count": 0, "disk_paused": False, "cameras": []}
        self.storage = None

    def _request(self, method, path, payload=None):
        with httpx.Client(timeout=3, trust_env=False, follow_redirects=False) as client:
            result = client.request(method, "http://127.0.0.1:9997"+path, json=payload)
            result.raise_for_status()
            return result.json() if result.content else {}

    def start(self):
        if not self.binary or not self.directory:
            return
        if self.thread and self.thread.is_alive():
            return
        binary = Path(self.binary).resolve()
        if not binary.is_file() or not re.fullmatch("[0-9a-f]{64}", self.expected_hash):
            raise ValueError("NVR engine binary and SHA256 fingerprint are required")
        if hashlib.sha256(binary.read_bytes()).hexdigest() != self.expected_hash:
            raise ValueError("NVR binary fingerprint mismatch")
        self.binary = str(binary)
        self.storage = prepare_storage(self.directory)
        self.config = self.root / "nvr-engine.json"
        self.config.write_text(json.dumps(engine_config(self.storage, self.retention)), encoding="utf8")
        self.config.chmod(0o600)
        self.stop.clear()
        self.thread = threading.Thread(target=self._supervise, name="garda-recorder", daemon=True)
        self.thread.start()

    def _launch(self):
        for port in (9997, 9996, 8554):
            with socket.socket() as check:
                check.settimeout(0.2)
                if check.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("Recorder listener already in use; refusing to control another process")
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self.process = subprocess.Popen([self.binary, str(self.config.resolve())],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            cwd=str(self.root.resolve()), creationflags=flags)
        self.applied.clear()
        self.sources.clear()
        with self.lock:
            self.state["status"] = "starting"

    def reconcile(self):
        disk = shutil.disk_usage(self.storage)
        paused = disk.free < self.reserve
        with self.runtime.lock:
            records = {key: dict(value) for key, value in self.runtime.records.items() if value.get("url")}
        for key, record in records.items():
            if not CAMERA_ID.fullmatch(key):
                raise ValueError("Invalid camera ID")
            desired = {"source": record["url"], "sourceOnDemand": False,
                       "record": record.get("recording_enabled", True) and not paused, "rtspTransport": "tcp"}
            if self.applied.get(key) != desired:
                if key in self.applied:
                    self._request("PATCH", "/v3/config/paths/patch/"+key, desired)
                else:
                    try:
                        self._request("POST", "/v3/config/paths/add/"+key, desired)
                    except httpx.HTTPStatusError as exc:
                        if exc.response.status_code not in (400, 409):
                            raise
                        self._request("PATCH", "/v3/config/paths/patch/"+key, desired)
                self.applied[key] = desired
            if self.applied.get(key) != desired:
                # Source URLs never go into process arguments, plaintext config or HTTP responses.
                method, route = ("PATCH", "patch") if key in self.applied else ("POST", "add")
                self._request(method, "/v3/config/paths/"+route+"/"+key, desired)
                self.applied[key] = desired
        paths = self._request("GET", "/v3/paths/list?itemsPerPage=100").get("items", [])
        by_name = {p["name"]: p for p in paths}
        cameras = []
        for key, record in records.items():
            path = by_name.get(key, {})
            latest = self.latest_segment(key)
            cameras.append({"id": key, "source_ready": bool(path.get("ready")),
                "recording_enabled": record.get("recording_enabled", True),
                "recording_active": bool(path.get("ready") and self.applied.get(key, {}).get("record") and latest and latest["age_seconds"] < 90),
                "last_segment": latest, "bytes_received": path.get("bytesReceived", 0)})
        with self.lock:
            self.state.update(status="disk_low" if paused else "running", disk_paused=paused,
                free_bytes=disk.free, total_bytes=disk.total, reserve_bytes=self.reserve,
                storage=str(self.storage), cameras=cameras)

    def latest_segment(self, camera):
        directory = self.storage / "video" / camera
        if not directory.is_dir() or directory.is_symlink():
            return None
        # At one-minute segments and the bounded 90-day policy this stays local to one camera.
        newest = max((p for p in directory.glob("*.mp4") if p.is_file() and not p.is_symlink()),
                     key=lambda p: p.name, default=None)
        if newest is None:
            return None
        info = newest.stat()
        return {"name": newest.name, "size_bytes": info.st_size,
                "age_seconds": max(0, round(time.time()-info.st_mtime, 1))}

    def _supervise(self):
        failures = 0
        while not self.stop.is_set():
            try:
                if not self.process or self.process.poll() is not None:
                    if self.process:
                        with self.lock:
                            self.state["restart_count"] += 1
                    self._launch()
                self.reconcile()
                failures = 0
            except Exception:
                failures += 1
                with self.lock:
                    self.state["status"] = "recovering"
                if failures >= 4 and self.process:
                    self._terminate()
                    failures = 0
            self.stop.wait(2 if failures else 5)

    def _terminate(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

    def snapshot(self):
        with self.lock:
            return dict(self.state)

    def timeline(self, camera, start=None, end=None):
        if not CAMERA_ID.fullmatch(camera) or camera not in self.runtime.records:
            raise ValueError("Unknown camera")
        params = {"path": camera}
        for name, value in (("start", start), ("end", end)):
            if value:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
                params[name] = value
        with httpx.Client(timeout=10, trust_env=False, follow_redirects=False) as client:
            result = client.get("http://127.0.0.1:9996/list", params=params)
            if result.status_code == 404:
                return []
            result.raise_for_status()
            # Do not expose local media service URLs, or forward a URL supplied by that service.
            return [{"start": x["start"], "duration": x["duration"]} for x in result.json()[:2000]]

    def close(self):
        self.stop.set()
        if self.thread:
            self.thread.join(timeout=20)
        self._terminate()
        with self.lock:
            self.state["status"] = "stopped"
