"""SQLite WAL metadata and private filesystem evidence; no biometric templates."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2
import numpy as np

KINDS = frozenset({"motion", "face", "plate"})


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class EventStore:
    def __init__(self, directory: str | Path):
        self.root = Path(directory).resolve()
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            self.root.chmod(0o700)
        except OSError:
            pass  # Filesystem permissions should be checked at deployment.
        self._lock = threading.RLock()
        self.db = sqlite3.connect(str(self.root / "garda.db"), timeout=30, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=30000")
        with self._lock, self.db:
            self.db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, camera_id TEXT NOT NULL, location TEXT NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN ('motion','face','plate')),
                observed_at TEXT NOT NULL, confidence REAL,
                plate_text TEXT, track_id TEXT, bbox_json TEXT,
                review_status TEXT NOT NULL DEFAULT 'unreviewed'
            );
            CREATE INDEX IF NOT EXISTS ix_events_search
                ON events(kind, observed_at DESC, camera_id);
            CREATE INDEX IF NOT EXISTS ix_events_plate
                ON events(plate_text, observed_at DESC);
            CREATE TABLE IF NOT EXISTS photos (
                id TEXT PRIMARY KEY, event_id TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE, label TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS ix_photos_event ON photos(event_id);
            CREATE TABLE IF NOT EXISTS access_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL, at TEXT NOT NULL, source TEXT NOT NULL
            );
            """)
            columns = {r[1] for r in self.db.execute("PRAGMA table_info(events)")}
            if "face_label" not in columns:
                self.db.execute("ALTER TABLE events ADD COLUMN face_label TEXT")
            if "face_similarity" not in columns:
                self.db.execute("ALTER TABLE events ADD COLUMN face_similarity REAL")

    def add_event(self, camera_id: str, location: str, kind: str,
                  confidence: float | None = None, plate_text: str | None = None,
                  track_id: str | None = None, bbox: tuple[int, int, int, int] | None = None,
                  when: str | None = None,
                  face_label: str | None = None,
                  face_similarity: float | None = None) -> str:
        if kind not in KINDS:
            raise ValueError("invalid event kind")
        if face_label and kind != "face":
            raise ValueError("face_label only allowed for face events")
        if plate_text and kind != "plate":
            raise ValueError("plate_text can only belong to plate events")
        event_id = uuid.uuid4().hex
        with self._lock, self.db:
            self.db.execute(
                "INSERT INTO events(id,camera_id,location,kind,observed_at,confidence,plate_text,track_id,bbox_json,face_label,face_similarity) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (event_id, camera_id, location, kind, when or utcnow(), confidence,
                 plate_text, track_id, json.dumps(bbox) if bbox else None,
                 face_label, face_similarity),
            )
        return event_id

    def add_photo(self, event_id: str, frame: np.ndarray, label: str) -> str:
        if frame is None or frame.size == 0:
            raise ValueError("invalid image")
        if not label.replace("-", "").replace("_", "").isalnum():
            raise ValueError("invalid snapshot label")
        with self._lock:
            record = self.db.execute("SELECT id, camera_id, observed_at FROM events WHERE id=?",
                                     (event_id,)).fetchone()
            if record is None:
                raise ValueError("event does not exist")
            camera_id = record["camera_id"]
            date = record["observed_at"][:10]
            directory = self.root / "evidence" / date / camera_id
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            name = f"{event_id}_{label}_{uuid.uuid4().hex[:8]}.jpg"
            target = directory / name
            ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 83])
            if not ok:
                raise IOError("JPEG encoding failed")
            temp = target.with_suffix(".tmp")
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd, "wb") as output:
                    output.write(encoded.tobytes())
                os.replace(temp, target)
                photo_id = uuid.uuid4().hex
                rel = target.relative_to(self.root).as_posix()
                with self.db:
                    self.db.execute("INSERT INTO photos(id,event_id,path,label,created_at) VALUES(?,?,?,?,?)",
                                    (photo_id, event_id, rel, label, utcnow()))
                return photo_id
            except Exception:
                temp.unlink(missing_ok=True)
                target.unlink(missing_ok=True)
                raise

    def list_events(self, kind: str | None = None, plate_prefix: str | None = None,
                    camera_id: str | None = None, limit: int = 50, search: str = "") -> list[dict]:
        if kind is not None and kind not in KINDS:
            raise ValueError("invalid kind")
        limit = max(1, min(int(limit), 100))
        sql = "SELECT id,camera_id,location,kind,observed_at,confidence,plate_text,track_id,review_status,face_label,face_similarity FROM events WHERE 1=1"
        args: list = []
        if kind:
            sql += " AND kind=?"; args.append(kind)
        if plate_prefix:
            sql += " AND plate_text LIKE ?"; args.append(plate_prefix.upper().replace("%", "").replace("_", "") + "%")
        if camera_id:
            sql += " AND camera_id=?"; args.append(camera_id)
        if search:
            text = "%" + search[:100].replace("%", "").replace("_", "") + "%"
            sql += " AND (plate_text LIKE ? OR face_label LIKE ? OR camera_id LIKE ?)"
            args.extend((text, text, text))
        sql += " ORDER BY observed_at DESC, id DESC LIMIT ?"; args.append(limit)
        with self._lock:
            return [dict(row) for row in self.db.execute(sql, args)]

    def event_photos(self, event_id: str) -> list[dict]:
        with self._lock:
            return [dict(row) for row in self.db.execute(
                "SELECT id,event_id,label,created_at FROM photos WHERE event_id=? ORDER BY created_at,id",
                (event_id,))]

    def photo_path(self, event_id: str, photo_id: str) -> Path | None:
        with self._lock:
            row = self.db.execute("SELECT path FROM photos WHERE id=? AND event_id=?",
                                  (photo_id, event_id)).fetchone()
        if row is None:
            return None
        target = (self.root / row["path"]).resolve()
        # Defense against path traversal or symlinked evidence directories.
        if not target.is_relative_to(self.root / "evidence"):
            return None
        return target if target.is_file() else None

    def stats(self) -> dict[str, int]:
        with self._lock:
            counts = {"motion": 0, "face": 0, "plate": 0}
            for row in self.db.execute("SELECT kind,COUNT(*) n FROM events GROUP BY kind"):
                counts[row["kind"]] = row["n"]
            return counts

    def audit(self, action: str, source: str = "local-api") -> None:
        with self._lock, self.db:
            self.db.execute("INSERT INTO access_audit(action,at,source) VALUES(?,?,?)",
                            (action[:100], utcnow(), source[:100]))

    def purge(self, retention_days: int = 90) -> dict[str, int]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat(timespec="milliseconds")
        with self._lock:
            images = [row[0] for row in self.db.execute(
                "SELECT photos.path FROM photos JOIN events ON photos.event_id=events.id WHERE events.observed_at < ?",
                (cutoff,))]
            deleted = self.db.execute("SELECT COUNT(*) FROM events WHERE observed_at < ?", (cutoff,)).fetchone()[0]
            with self.db:
                self.db.execute("DELETE FROM events WHERE observed_at < ?", (cutoff,))
            count = 0
            for path in images:
                target = (self.root / path).resolve()
                if target.is_relative_to(self.root / "evidence") and target.is_file():
                    target.unlink()
                    count += 1
            return {"events": deleted, "photos": count}

    def close(self):
        with self._lock:
            self.db.close()
