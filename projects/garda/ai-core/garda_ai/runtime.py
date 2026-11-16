"""One-site camera registry and bounded live/inference workers. Secrets stay local."""
from __future__ import annotations

import ipaddress
import json
import os
import re
import threading
import time
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlsplit

import cv2
from cryptography.fernet import Fernet

from .config import CameraConfig
from .processor import FrameProcessor
from .providers import Providers
from .runner import StreamWorker
from .vision import FaceDetector


def checked_rtsp(url):
    u = urlsplit(url)
    if u.scheme not in ("rtsp", "rtsps") or not u.hostname or len(url) > 2048:
        raise ValueError("Valid RTSP camera URL required")
    try:
        ip = ipaddress.ip_address(u.hostname)
    except ValueError as exc:
        raise ValueError("Use a private camera IP address") from exc
    private = (ip.version == 4 and any(ip in net for net in
               map(ipaddress.ip_network, ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))))
    if not (private or ip.is_loopback) or u.fragment:
        raise ValueError("Camera must be on the local private network")
    if u.port is not None and not 1 <= u.port <= 65535:
        raise ValueError("Invalid camera port")
    return url


class Runtime:
    def __init__(self, root: Path, store):
        self.root, self.store = root, store
        self.lock = threading.RLock()
        self.providers = Providers(root)
        self.plate_lock = threading.Lock()
        self.workers, self.frames, self.states = {}, {}, {}
        key_path = root / "camera.key"
        if not key_path.exists():
            fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(Fernet.generate_key())
        self.cipher = Fernet(key_path.read_bytes())
        self.file = root / "cameras.encrypted"
        self.records = json.loads(self.cipher.decrypt(self.file.read_bytes())) if self.file.exists() else {
            f"CAM-{n:02}": {"id": f"CAM-{n:02}", "name": f"Kamera {n:02}", "url": "",
                            "face_provider": "sface", "plate_provider": "fastalpr"} for n in range(1, 9)}

    def save(self, camera_id, name, url, face="sface", plate="fastalpr"):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", camera_id):
            raise ValueError("Invalid camera ID")
        if face not in ("presence", "sface", "deepface", "insightface") or plate not in ("off", "fastalpr", "paddleocr"):
            raise ValueError("Invalid provider")
        if not name.strip() or len(name) > 100:
            raise ValueError("Camera name required (max 100 characters)")
        checked_rtsp(url)
        with self.lock:
            if camera_id in self.workers:
                raise ValueError("Stop the camera before editing")
            if camera_id not in self.records and len(self.records) >= 49:
                raise ValueError("Single-site configuration limit is 49")
            self.records[camera_id] = {"id": camera_id, "name": name.strip(), "url": url,
                                       "face_provider": face, "plate_provider": plate,
                                       "recording_enabled": self.records.get(camera_id, {}).get("recording_enabled", True)}
            self._persist()

    def _persist(self):
        temp = self.file.with_suffix(".tmp")
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(self.cipher.encrypt(json.dumps(self.records).encode()))
        os.replace(temp, self.file)

    def recording(self, camera_id, enabled):
        with self.lock:
            if camera_id not in self.records or not self.records[camera_id]["url"]:
                raise ValueError("Configure the camera first")
            self.records[camera_id]["recording_enabled"] = bool(enabled)
            self._persist()

    def cameras(self):
        with self.lock:
            now = time.monotonic()
            result = []
            for key, record in self.records.items():
                frame = self.frames.get(key)
                state = dict(self.states.get(key, {}))
                result.append({k: v for k, v in record.items() if k != "url"} | {
                    "configured": bool(record["url"]), "running": key in self.workers,
                    "online": bool(frame and key in self.workers and now-frame[0] < 5),
                    "frame_age_seconds": round(now-frame[0], 1) if frame else None,
                    "inference": state.get("inference", "not_started"),
                    "provider_issues": state.get("provider_issues", []),
                })
            return result

    def preview(self, key):
        with self.lock:
            frame = self.frames.get(key)
            if not frame or key not in self.workers or time.monotonic()-frame[0] >= 5:
                return None
            return frame[1]

    def start(self, key):
        with self.lock:
            if key not in self.records or not self.records[key]["url"]:
                raise ValueError("Configure the camera first")
            if key in self.workers:
                return
            record = dict(self.records[key])
            detector, matcher, plates, issues = FaceDetector(), None, None, []
            if record["face_provider"] != "presence":
                try:
                    matcher = self.providers.get(record["face_provider"])
                    detector = matcher
                except Exception:
                    issues.append(record["face_provider"] + ": configuration_required; presence_only")
            if record["plate_provider"] != "off":
                try:
                    plates = self.providers.get(record["plate_provider"])
                except Exception:
                    issues.append(record["plate_provider"] + ": configuration_required")
            stop = threading.Event()
            config = CameraConfig(key, record["url"], record["name"], 1.0)
            processor = FrameProcessor(config, self.store, detector, plates, self.plate_lock,
                                       face_matcher=matcher)
            def preview(frame):
                # Bound bandwidth per stream and keep only the latest JPEG.
                small = cv2.resize(frame, (640, max(1, int(640*frame.shape[0]/frame.shape[1]))))
                ok, image = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if ok:
                    with self.lock:
                        self.frames[key] = (time.monotonic(), image.tobytes())
            def inference(ok):
                with self.lock:
                    self.states[key]["inference"] = ("partial" if issues else "processing") if ok else "inference_error"
            worker = StreamWorker(config, processor, stop, on_preview=preview, on_inference=inference)
            self.states[key] = {"inference": "partial" if issues else "configured",
                                "provider_issues": issues}
            self.workers[key] = (worker, stop)
            worker.start()

    def stop(self, key):
        with self.lock:
            pair = self.workers.get(key)
            if not pair:
                return
            pair[1].set()
        pair[0].join()
        if pair[0].reader.is_alive() or pair[0].processor_thread.is_alive():
            raise RuntimeError("Camera worker still stopping; retry shortly")
        with self.lock:
            self.workers.pop(key, None)
            self.frames.pop(key, None)

    def close(self):
        for key in list(self.workers):
            try:
                self.stop(key)
            except RuntimeError:
                pass
        # Do not close stores/models while a bounded shutdown is still draining a worker.
        if not self.workers:
            self.providers.close()
