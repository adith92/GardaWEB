"""Named lab users, scrypt password hashes, expiring revocable sessions."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
import threading
import time
from pathlib import Path


class Identity:
    def __init__(self, root: Path):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(root / "identity.db"), check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, salt BLOB, digest BLOB, role TEXT)")
        self.sessions = {}
        self.attempts = {}

    def add_user(self, name: str, password: str, role="admin"):
        if not 1 <= len(name) <= 80 or len(password) < 12 or role not in ("admin", "operator", "viewer"):
            raise ValueError("Username, password >=12 characters and valid role required")
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        with self.lock, self.db:
            self.db.execute("INSERT INTO users VALUES(?,?,?,?)", (name, salt, digest, role))

    def has_users(self):
        with self.lock:
            return bool(self.db.execute("SELECT 1 FROM users LIMIT 1").fetchone())

    def login(self, name, password, source):
        now = time.monotonic()
        with self.lock:
            self.attempts = {k: [v for v in times if now-v < 60] for k, times in self.attempts.items()
                             if any(now-v < 60 for v in times)}
            # Global bound also prevents unbounded source-address memory allocation.
            if len(self.attempts) >= 512 and source not in self.attempts:
                raise PermissionError("Login temporarily limited")
            attempts = self.attempts.setdefault(source, [])
            if len(attempts) >= 5:
                raise PermissionError("Login temporarily limited")
            attempts.append(now)
            row = self.db.execute("SELECT salt,digest,role FROM users WHERE name=?", (name,)).fetchone()
        salt = row[0] if row else bytes(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        if row is None or not hmac.compare_digest(digest, row[1]):
            raise ValueError("Invalid login")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with self.lock:
            self.sessions = {k: v for k, v in self.sessions.items() if v["expires"] > time.time()}
            if len(self.sessions) >= 128:
                raise PermissionError("Session limit reached")
            self.sessions[self.digest(token)] = {"name": name, "role": row[2], "csrf": csrf,
                                                 "expires": time.time() + 8 * 3600}
        return token, dict(self.sessions[self.digest(token)])

    @staticmethod
    def digest(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def actor(self, token):
        with self.lock:
            result = self.sessions.get(self.digest(token))
            if result is None or result["expires"] <= time.time():
                return None
            return dict(result)

    def logout(self, token):
        with self.lock:
            self.sessions.pop(self.digest(token), None)

    def close(self):
        self.sessions.clear()
        self.db.close()
