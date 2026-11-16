"""Encrypted event payloads and biometric templates, append-only audit records."""
from __future__ import annotations

import base64
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from cryptography.fernet import Fernet


class Store:
    def __init__(self, path: str, key: str):
        if not key:
            raise ValueError("GARDA_DATA_KEY required. Generate with Fernet.generate_key().")
        self.crypt = Fernet(key.encode())
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.lock = threading.RLock()
        with self.lock, self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, time_utc TEXT, site_id TEXT, camera_id TEXT, kind TEXT, payload BLOB)")
            self.db.execute("CREATE INDEX IF NOT EXISTS events_by_time ON events(time_utc)")
            self.db.execute("CREATE TABLE IF NOT EXISTS enrolled_faces (person_id TEXT PRIMARY KEY, template BLOB, created_utc TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS audit (id TEXT PRIMARY KEY, time_utc TEXT, actor TEXT, action TEXT, target TEXT, outcome TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS network_scans (id TEXT PRIMARY KEY, created_utc TEXT, completed_utc TEXT, status TEXT, cidr TEXT, mode TEXT, target_ip TEXT, payload BLOB)")

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def seal(self, payload: dict[str, Any]) -> bytes:
        return self.crypt.encrypt(json.dumps(payload, separators=(",", ":")).encode())

    def unseal(self, payload: bytes) -> dict[str, Any]:
        return json.loads(self.crypt.decrypt(payload).decode())

    def event(self, site_id: str, camera_id: str, kind: str, payload: dict[str, Any]) -> str:
        eid = str(uuid4())
        with self.lock, self.db:
            self.db.execute("INSERT INTO events VALUES(?,?,?,?,?,?)", (eid, self.now(), site_id, camera_id, kind, self.seal(payload)))
        return eid

    def events(self, limit: int = 100, site_id: str | None = None) -> list[dict[str, Any]]:
        with self.lock:
            if site_id:
                rows = self.db.execute("SELECT id,time_utc,site_id,camera_id,kind,payload FROM events WHERE site_id=? ORDER BY time_utc DESC LIMIT ?", (site_id, limit)).fetchall()
            else:
                rows = self.db.execute("SELECT id,time_utc,site_id,camera_id,kind,payload FROM events ORDER BY time_utc DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": x[0], "time_utc": x[1], "site_id": x[2], "camera_id": x[3], "kind": x[4], "data": self.unseal(x[5])} for x in rows]

    def enroll(self, person_id: str, embedding: list[float]):
        with self.lock, self.db:
            self.db.execute("INSERT INTO enrolled_faces VALUES(?,?,?) ON CONFLICT(person_id) DO UPDATE SET template=excluded.template, created_utc=excluded.created_utc", (person_id, self.seal({"vector": embedding}), self.now()))

    def faces(self) -> dict[str, list[float]]:
        with self.lock:
            rows = self.db.execute("SELECT person_id,template FROM enrolled_faces").fetchall()
        return {name: self.unseal(value)["vector"] for name, value in rows}

    def delete_face(self, person_id: str) -> bool:
        with self.lock, self.db:
            count = self.db.execute("DELETE FROM enrolled_faces WHERE person_id=?", (person_id,)).rowcount
        return count > 0

    def audit(self, actor: str, action: str, target: str, outcome: str):
        with self.lock, self.db:
            self.db.execute("INSERT INTO audit VALUES(?,?,?,?,?,?)", (str(uuid4()), self.now(), actor, action, target, outcome))

    def audit_rows(self, limit: int = 100) -> list[dict[str, str]]:
        with self.lock:
            rows = self.db.execute("SELECT time_utc,actor,action,target,outcome FROM audit ORDER BY time_utc DESC LIMIT ?", (limit,)).fetchall()
        return [dict(zip(("time_utc", "actor", "action", "target", "outcome"), row)) for row in rows]

    def prune(self, days: int) -> int:
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self.lock, self.db:
            deleted = self.db.execute("DELETE FROM events WHERE time_utc<?", (cutoff,)).rowcount
        return deleted

    def create_scan(self, cidr: str, mode: str, target_ip: str | None) -> str:
        scan_id = str(uuid4())
        with self.lock, self.db:
            self.db.execute("INSERT INTO network_scans VALUES (?,?,?,?,?,?,?,?)",
                            (scan_id, self.now(), None, "queued", "", mode, None,
                             self.seal({"devices": [], "request_cidr": cidr, "request_target_ip": target_ip})))
        return scan_id

    def finish_scan(self, scan_id: str, status: str, result: dict[str, Any]):
        with self.lock, self.db:
            row = self.db.execute("SELECT payload FROM network_scans WHERE id=?", (scan_id,)).fetchone()
            original = self.unseal(row[0]) if row else {}
            payload = {**result, "request_cidr": original.get("request_cidr"),
                       "request_target_ip": original.get("request_target_ip")}
            self.db.execute("UPDATE network_scans SET status=?, completed_utc=?, payload=? WHERE id=?",
                            (status, self.now() if status in ("completed", "failed") else None,
                             self.seal(payload), scan_id))

    def scan(self, scan_id: str) -> dict[str, Any] | None:
        with self.lock:
            row = self.db.execute("SELECT id,created_utc,completed_utc,status,cidr,mode,target_ip,payload FROM network_scans WHERE id=?", (scan_id,)).fetchone()
        if not row:
            return None
        payload = self.unseal(row[7])
        target, network = payload.pop("request_target_ip", None), payload.pop("request_cidr", None)
        return {"id": row[0], "created_utc": row[1], "completed_utc": row[2],
                "status": row[3], "network": network, "mode": row[5], "target_ip": target,
                "result": payload}

    def scans(self, limit: int = 10) -> list[dict[str, Any]]:
        with self.lock:
            rows = self.db.execute("SELECT id FROM network_scans ORDER BY created_utc DESC LIMIT ?", (limit,)).fetchall()
        return [self.scan(row[0]) for row in rows]

    def close(self):
        with self.lock:
            self.db.close()
