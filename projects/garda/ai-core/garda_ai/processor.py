"""Event-driven, per-scene (NOT biometric identity) face and plate state machines."""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from threading import Lock

import numpy as np

from .config import CameraConfig
from .storage import EventStore
from .vision import Detection, MotionDetector, crop_box

LOG = logging.getLogger("garda.processor")


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    area = max(0, x2 - x1) * max(0, y2 - y1)
    full_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    full_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    return area / max(1, full_a + full_b - area)


@dataclass
class FaceTrack:
    id: str
    event_id: str
    bbox: tuple[int, int, int, int]
    last_seen: float
    last_shot: float
    shots: int


class FaceSessions:
    """Dedup face positions over seconds; no embeddings or cross-visit identity."""
    def __init__(self, store: EventStore, camera: CameraConfig, max_shots: int = 3,
                 interval_seconds: float = 0.55, expires_seconds: float = 4.0):
        self.store, self.camera = store, camera
        self.max_shots, self.interval = max_shots, interval_seconds
        self.expires = expires_seconds
        self.tracks: dict[str, FaceTrack] = {}

    def update(self, frame: np.ndarray, detections: list[Detection], now: float,
               matcher=None) -> list[str]:
        for key, track in list(self.tracks.items()):
            if now - track.last_seen > self.expires:
                del self.tracks[key]
        available = set(self.tracks)
        newly_created: list[str] = []
        for face in detections:
            matches = [(overlap(face.bbox, self.tracks[key].bbox), key) for key in available]
            score, key = max(matches, default=(0.0, ""))
            if score >= 0.22:
                track = self.tracks[key]
                available.remove(key)
                track.bbox, track.last_seen = face.bbox, now
            else:
                key = uuid.uuid4().hex[:12]
                label, score = matcher.match(frame, face) if matcher else (None, None)
                event_id = self.store.add_event(self.camera.id, self.camera.location, "face",
                                                face.confidence, track_id=key, bbox=face.bbox,
                                                face_label=label, face_similarity=score)
                track = FaceTrack(key, event_id, face.bbox, now, float("-inf"), 0)
                self.tracks[key] = track
                newly_created.append(event_id)
                self._capture(track, frame, face)
            if track.shots < self.max_shots and now - track.last_shot >= self.interval:
                self._capture(track, frame, face)
        return newly_created

    def _capture(self, track: FaceTrack, frame: np.ndarray, detection: Detection):
        if track.shots >= self.max_shots:
            return
        index = track.shots + 1
        self.store.add_photo(track.event_id, frame, f"scene-{index:02d}")
        face = crop_box(frame, detection.bbox, padding=0.18)
        if face.size:
            self.store.add_photo(track.event_id, face, f"face-{index:02d}")
        track.shots = index
        track.last_shot = track.last_seen


class PlateConsensus:
    """Two matching OCR reads + confidence threshold + bounded dedup window."""
    def __init__(self, store: EventStore, camera: CameraConfig,
                 confirmations: int = 2, window_seconds: float = 7.0,
                 cooldown_seconds: float = 60.0):
        self.store, self.camera = store, camera
        self.confirmations, self.window = confirmations, window_seconds
        self.cooldown = cooldown_seconds
        self.votes: dict[str, list[tuple[float, float]]] = {}
        self.last_saved: dict[str, float] = {}

    def update(self, frame: np.ndarray, detections: list[Detection], now: float) -> list[str]:
        saved: list[str] = []
        # Keep state bounded even if hundreds of noisy readings accumulate.
        self.votes = {plate: [(t, c) for t, c in votes if now - t <= self.window]
                      for plate, votes in self.votes.items()
                      if any(now - t <= self.window for t, _ in votes)}
        self.last_saved = {p: t for p, t in self.last_saved.items()
                           if now - t <= self.cooldown}
        seen_now = set()
        for entry in detections:
            plate = entry.text
            if not plate or plate in seen_now:
                continue
            seen_now.add(plate)
            votes = self.votes.setdefault(plate, [])
            votes.append((now, entry.confidence))
            if (len(votes) < self.confirmations or
                plate in self.last_saved and now - self.last_saved[plate] < self.cooldown):
                continue
            confidence = sum(v for _, v in votes) / len(votes)
            event_id = self.store.add_event(self.camera.id, self.camera.location, "plate",
                                            confidence, plate_text=plate, bbox=entry.bbox)
            self.store.add_photo(event_id, frame, "scene")
            plate_crop = crop_box(frame, entry.bbox, padding=0.1)
            if plate_crop.size:
                self.store.add_photo(event_id, plate_crop, "plate")
            saved.append(event_id)
            self.last_saved[plate] = now
            self.votes.pop(plate, None)
        return saved


class FrameProcessor:
    """Injection-friendly processor; AI calls never touch Android/GUI main thread."""
    def __init__(self, camera: CameraConfig, store: EventStore, face_detector,
                 plate_reader=None, plate_lock: Lock | None = None,
                 motion_min_fraction: float = 0.016, face_matcher=None):
        self.camera, self.store = camera, store
        self.face_detector = face_detector
        self.face_matcher = face_matcher
        self.plate_reader = plate_reader
        self.plate_lock = plate_lock or Lock()
        self.motion = MotionDetector(minimum_fraction=motion_min_fraction)
        self.faces = FaceSessions(store, camera)
        self.plates = PlateConsensus(store, camera)
        self.last_motion = float("-inf")
        self.last_plate = float("-inf")

    def process(self, frame: np.ndarray, now: float | None = None) -> dict[str, int]:
        timestamp = now if now is not None else time.monotonic()
        active, fraction = self.motion.detect(frame)
        counters = {"motion": 0, "face": 0, "plate": 0}
        if active and timestamp - self.last_motion >= 15.0:
            event = self.store.add_event(self.camera.id, self.camera.location, "motion",
                                         min(1.0, fraction))
            self.store.add_photo(event, frame, "scene")
            self.last_motion = timestamp
            counters["motion"] += 1
        faces = self.face_detector.detect(frame)
        counters["face"] = len(self.faces.update(frame, faces, timestamp, matcher=self.face_matcher))
        # Idle LPR every 5s; in-motion up to one frame per second.
        interval = 1.0 if active else 5.0
        if self.plate_reader is not None and timestamp - self.last_plate >= interval:
            with self.plate_lock:
                plates = self.plate_reader.detect(frame)
            counters["plate"] = len(self.plates.update(frame, plates, timestamp))
            self.last_plate = timestamp
        return counters
