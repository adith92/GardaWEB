"""Bounded-rate RTSP inference worker. Recording is handled by independent NVR."""
from __future__ import annotations

import threading
import time

import cv2

from .core import Camera
from .storage import Store
from .vision import Vision


class Workers:
    def __init__(self, cameras: dict[str, Camera], vision: Vision, store: Store):
        self.cameras, self.vision, self.store = cameras, vision, store
        self._stops: dict[str, threading.Event] = {}
        self._threads: dict[str, threading.Thread] = {}
        self._last: dict[str, str] = {}
        self._lock = threading.RLock()

    def status(self) -> dict:
        with self._lock:
            return {cid: {"running": cid in self._threads and self._threads[cid].is_alive(), "last_error": self._last.get(cid)} for cid in self.cameras}

    def start(self, camera_id: str):
        camera = self.cameras[camera_id]
        if not camera.rtsp_url:
            raise ValueError("RTSP environment variable missing")
        with self._lock:
            if camera_id in self._threads and self._threads[camera_id].is_alive():
                return
            stop = threading.Event()
            self._stops[camera_id] = stop
            thread = threading.Thread(target=self._loop, args=(camera, stop), daemon=True)
            self._threads[camera_id] = thread
            thread.start()

    def _loop(self, camera: Camera, stop: threading.Event):
        last_emit = ""
        while not stop.is_set():
            capture = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG)
            if not capture.isOpened():
                self._last[camera.id] = "stream_unavailable"
                stop.wait(3)
                continue
            try:
                while not stop.is_set():
                    ok, frame = capture.read()
                    if not ok:
                        self._last[camera.id] = "stream_interrupted"
                        break
                    self._last[camera.id] = ""
                    # At most one inference every 2 seconds; no 16-camera throughput guarantee.
                    if stop.wait(2):
                        break
                    try:
                        candidates = self.vision.analyze(frame, self.store.faces() if self.vision.enable_face_id else None)
                        # A coarse dedupe to reduce repeated detection events.
                        sig = str((candidates["face_count"], candidates["plates"], candidates["face_candidates"]))
                        if sig != last_emit and (candidates["face_count"] or candidates["plates"] or candidates["face_candidates"]):
                            self.store.event(camera.site_id, camera.id, "vision_candidate", candidates)
                            last_emit = sig
                    except Exception:
                        self._last[camera.id] = "inference_error"
                        stop.wait(1)
            finally:
                capture.release()
            stop.wait(2)

    def stop(self, camera_id: str):
        with self._lock:
            event = self._stops.get(camera_id)
            if event:
                event.set()

    def close(self):
        with self._lock:
            for event in self._stops.values():
                event.set()
            threads = list(self._threads.values())
        for thread in threads:
            thread.join(timeout=3)
