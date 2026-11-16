"""Persistent single-site incident workflow, linked to existing GARDA event evidence.

No automated physical actions. All calls must pass Unified API RBAC/CSRF guards.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import uuid

from .storage import utcnow


class IncidentMissing(LookupError):
    pass


class IncidentConflict(RuntimeError):
    pass


SEVERITIES = frozenset({"low", "medium", "high", "critical"})
STATUSES = frozenset({"open", "acknowledged", "resolved"})


class IncidentLedger:
    def __init__(self, event_store):
        self.events = event_store
        with self.events._lock, self.events.db:
            self.events.db.executescript("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),
                status TEXT NOT NULL CHECK(status IN ('open','acknowledged','resolved')),
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                acknowledged_by TEXT,
                resolved_by TEXT
            );
            CREATE INDEX IF NOT EXISTS ix_incidents_status_time
                ON incidents(status, updated_at DESC);
            CREATE TABLE IF NOT EXISTS incident_events (
                incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
                event_id TEXT NOT NULL UNIQUE REFERENCES events(id) ON DELETE RESTRICT,
                attached_at TEXT NOT NULL,
                attached_by TEXT NOT NULL,
                PRIMARY KEY (incident_id, event_id)
            );
            CREATE TABLE IF NOT EXISTS incident_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                note TEXT,
                at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_incident_history
                ON incident_history(incident_id, at, id);
            """)

    def _history(self, incident_id, action, actor, note=None):
        self.events.db.execute(
            "INSERT INTO incident_history(incident_id,action,actor,note,at) VALUES(?,?,?,?,?)",
            (incident_id, action, actor[:80], note, utcnow()))
        self.events.db.execute(
            "INSERT INTO access_audit(action,at,source) VALUES(?,?,?)",
            ("incident:" + action, utcnow(), actor[:100]))

    def _incident(self, incident_id):
        row = self.events.db.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
        if row is None:
            raise IncidentMissing("Incident not found")
        return dict(row)

    def _event_camera(self, event_id):
        row = self.events.db.execute("SELECT camera_id FROM events WHERE id=?", (event_id,)).fetchone()
        if row is None:
            raise IncidentMissing("Event not found")
        return row["camera_id"]

    def create(self, title, camera_id, severity, actor, event_id=None):
        title = title.strip()
        if not title or severity not in SEVERITIES or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", camera_id):
            raise ValueError("Invalid incident title, camera or severity")
        incident_id = uuid.uuid4().hex
        now = utcnow()
        with self.events._lock, self.events.db:
            if event_id and self._event_camera(event_id) != camera_id:
                raise ValueError("Linked event belongs to another camera")
            self.events.db.execute(
                "INSERT INTO incidents(id,title,camera_id,severity,status,created_by,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (incident_id, title, camera_id, severity, "open", actor[:80], now, now))
            if event_id:
                try:
                    self.events.db.execute(
                        "INSERT INTO incident_events VALUES(?,?,?,?)",
                        (incident_id, event_id, now, actor[:80]))
                except sqlite3.IntegrityError as exc:
                    raise IncidentConflict("Event is already linked to another incident") from exc
            self._history(incident_id, "created", actor)
        return self.get(incident_id)

    def list(self, status=None, limit=50):
        if status is not None and status not in STATUSES:
            raise ValueError("Invalid incident status")
        sql = ("SELECT i.*, (SELECT COUNT(*) FROM incident_events ie "
               "WHERE ie.incident_id=i.id) AS event_count FROM incidents i")
        args = []
        if status is not None:
            sql += " WHERE i.status=?"
            args.append(status)
        sql += " ORDER BY i.updated_at DESC, i.id DESC LIMIT ?"
        args.append(max(1, min(int(limit), 100)))
        with self.events._lock:
            return [dict(row) for row in self.events.db.execute(sql, args)]

    def get(self, incident_id):
        with self.events._lock:
            result = self._incident(incident_id)
            result["events"] = [dict(row) for row in self.events.db.execute(
                "SELECT e.id,e.camera_id,e.kind,e.observed_at,e.review_status "
                "FROM incident_events ie JOIN events e ON e.id=ie.event_id "
                "WHERE ie.incident_id=? ORDER BY e.observed_at,e.id", (incident_id,))]
            result["history"] = [dict(row) for row in self.events.db.execute(
                "SELECT action,actor,note,at FROM incident_history "
                "WHERE incident_id=? ORDER BY id", (incident_id,))]
            return result

    def transition(self, incident_id, action, actor):
        expected, target = {
            "acknowledge": ("open", "acknowledged"),
            "resolve": ("acknowledged", "resolved"),
        }.get(action, (None, None))
        if target is None:
            raise ValueError("Invalid incident action")
        with self.events._lock, self.events.db:
            incident = self._incident(incident_id)
            if incident["status"] != expected:
                raise IncidentConflict("Incident must be " + expected + " before " + action)
            column = "acknowledged_by" if action == "acknowledge" else "resolved_by"
            self.events.db.execute(
                "UPDATE incidents SET status=?,updated_at=?, " + column + "=? WHERE id=? AND status=?",
                (target, utcnow(), actor[:80], incident_id, expected))
            self._history(incident_id, action, actor)
        return self.get(incident_id)

    def attach_event(self, incident_id, event_id, actor):
        with self.events._lock, self.events.db:
            incident = self._incident(incident_id)
            if incident["status"] == "resolved":
                raise IncidentConflict("Resolved incident cannot accept more evidence")
            if self._event_camera(event_id) != incident["camera_id"]:
                raise ValueError("Evidence camera does not match incident camera")
            try:
                self.events.db.execute(
                    "INSERT INTO incident_events VALUES(?,?,?,?)",
                    (incident_id, event_id, utcnow(), actor[:80]))
            except sqlite3.IntegrityError as exc:
                raise IncidentConflict("Event is already linked to an incident") from exc
            self._history(incident_id, "event_attached", actor)
        return self.get(incident_id)

    def add_note(self, incident_id, note, actor):
        note = note.strip()
        if not 1 <= len(note) <= 500:
            raise ValueError("Note must contain 1-500 characters")
        with self.events._lock, self.events.db:
            incident = self._incident(incident_id)
            if incident["status"] == "resolved":
                raise IncidentConflict("Resolved incident cannot be edited")
            self._history(incident_id, "note", actor, note)
        return self.get(incident_id)

    def evidence_manifest(self, incident_id):
        """Integrity inventory for linked snapshots, not a legal-hold or signed export."""
        with self.events._lock:
            self._incident(incident_id)
            event_ids = [row[0] for row in self.events.db.execute(
                "SELECT event_id FROM incident_events WHERE incident_id=? ORDER BY event_id",
                (incident_id,))]
            photos = []
            for event_id in event_ids:
                for row in self.events.event_photos(event_id):
                    path = self.events.photo_path(event_id, row["id"])
                    if path is not None:
                        payload = path.read_bytes()
                        photos.append({"event_id": event_id, "photo_id": row["id"],
                                       "label": row["label"], "size_bytes": len(payload),
                                       "sha256": hashlib.sha256(payload).hexdigest()})
            return {"incident_id": incident_id, "events": event_ids,
                    "photos": photos, "snapshot_count": len(photos),
                    "legal_hold": False, "signed_export": False}
