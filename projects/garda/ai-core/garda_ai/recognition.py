"""Optional, consent-based local face recognition using OpenCV YuNet + SFace.

No cloud calls, identity guessing or automatic person-name discovery.
The operator enrolls reference images explicitly. Templates are encrypted
with a Fernet key supplied at runtime and stored in SQLite, not in source.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from cryptography.fernet import Fernet, InvalidToken

from .vision import Detection


class FaceGallery:
    def __init__(self, data_dir: Path, secret: str):
        if not secret:
            raise ValueError("GARDA_FACE_KEY is required for biometric recognition")
        try:
            self.cipher = Fernet(secret.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise ValueError("GARDA_FACE_KEY must be a Fernet key") from exc
        self._lock = threading.RLock()
        self.path = Path(data_dir).resolve() / "garda.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), timeout=30, check_same_thread=False)
        self.db.execute("PRAGMA busy_timeout=30000")
        self.db.execute("PRAGMA journal_mode=WAL")
        with self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS enrolled_faces(
                id TEXT PRIMARY KEY, label TEXT NOT NULL,
                feature_cipher BLOB NOT NULL, enrolled_at TEXT NOT NULL,
                consent_reference TEXT NOT NULL
            )""")

    def enroll(self, label: str, feature: np.ndarray, consent_reference: str) -> str:
        label = label.strip()
        reference = consent_reference.strip()
        if not (1 <= len(label) <= 90) or not (1 <= len(reference) <= 140):
            raise ValueError("Label and consent reference are required")
        arr = np.asarray(feature, dtype=np.float32).reshape(-1)
        if arr.size < 64 or not np.isfinite(arr).all():
            raise ValueError("Invalid biometric feature")
        cipher = self.cipher.encrypt(json.dumps(arr.tolist()).encode("utf-8"))
        face_id = uuid.uuid4().hex
        with self._lock, self.db:
            self.db.execute("""INSERT INTO enrolled_faces
                (id,label,feature_cipher,enrolled_at,consent_reference)
                VALUES(?,?,?,?,?)""", (face_id, label, cipher,
                                        datetime.now(timezone.utc).isoformat(), reference))
        return face_id

    def registered(self) -> list[tuple[str, np.ndarray]]:
        with self._lock:
            rows = self.db.execute("SELECT label,feature_cipher FROM enrolled_faces").fetchall()
        identities = []
        for label, token in rows:
            try:
                raw = json.loads(self.cipher.decrypt(token).decode("utf-8"))
            except (InvalidToken, ValueError) as exc:
                raise RuntimeError("Cannot decrypt stored face template: check GARDA_FACE_KEY") from exc
            identities.append((label, np.asarray(raw, dtype=np.float32).reshape(1, -1)))
        return identities

    def revoke(self, face_id: str) -> bool:
        with self._lock, self.db:
            result = self.db.execute("DELETE FROM enrolled_faces WHERE id=?", (face_id,))
            return bool(result.rowcount)

    def close(self):
        with self._lock:
            self.db.close()


class FaceMatcher:
    """YuNet landmarks + SFace cosine. Unknown is never assigned a real identity."""
    def __init__(self, sface_model: Path, gallery: FaceGallery, threshold: float = 0.55):
        if not Path(sface_model).is_file():
            raise FileNotFoundError("SFace ONNX model is missing")
        if not (0.36 <= threshold <= 0.90):
            raise ValueError("Face match threshold must be within 0.36..0.90")
        self.recognizer = cv2.FaceRecognizerSF.create(str(sface_model), "")
        self._lock = threading.RLock()
        self.gallery = gallery
        self.threshold = threshold

    def feature(self, frame: np.ndarray, detection: Detection) -> np.ndarray | None:
        if detection.face_row is None:
            return None  # Haar fallback cannot supply reliable 5-point landmarks.
        row = np.asarray(detection.face_row, dtype=np.float32)
        with self._lock:
            aligned = self.recognizer.alignCrop(frame, row)
            return self.recognizer.feature(aligned).copy()

    def match(self, frame: np.ndarray, detection: Detection) -> tuple[str | None, float | None]:
        feature = self.feature(frame, detection)
        if feature is None:
            return None, None
        best_label, best_score = None, -1.0
        with self._lock:
            for label, enrolled in self.gallery.registered():
                score = float(self.recognizer.match(
                    feature, enrolled, cv2.FaceRecognizerSF_FR_COSINE))
                if score > best_score:
                    best_label, best_score = label, score
        return (best_label if best_score >= self.threshold else None,
                round(best_score, 4) if best_score >= 0 else None)


def enroll_image(image_path: Path, label: str, reference: str,
                 face_model: Path, sface_model: Path, data_dir: Path,
                 key: str) -> str:
    from .vision import FaceDetector
    frame = cv2.imread(str(image_path))
    if frame is None:
        raise ValueError("Cannot read enrollment image")
    detections = FaceDetector(face_model).detect(frame)
    if len(detections) != 1:
        raise ValueError("Enrollment image must contain exactly one clear face")
    gallery = FaceGallery(data_dir, key)
    try:
        matcher = FaceMatcher(sface_model, gallery)
        feature = matcher.feature(frame, detections[0])
        if feature is None:
            raise ValueError("YuNet landmark detection is required for enrollment")
        return gallery.enroll(label, feature, reference)
    finally:
        gallery.close()
