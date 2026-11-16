"""Incident persistence, negative access, state transitions and evidence checks."""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient

from garda_ai.api import create_app
from garda_ai.server import validate_protected_launch


class IncidentApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"GARDA_COOKIE_SECURE": "0"})
        self.env.start()
        self.app = create_app(self.temp.name, unified=True)
        self.app.state.unified.identity.add_user("admin", "a-long-admin-password", "admin")
        self.app.state.unified.identity.add_user("operator", "a-long-operator-password", "operator")
        self.app.state.unified.identity.add_user("viewer", "a-long-viewer-password", "viewer")
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.event_id = self.app.state.unified.store.add_event("CAM-01", "Gate", "motion", .90)

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.env.stop()
        self.temp.cleanup()

    def login(self, name="admin"):
        result = self.client.post("/api/v1/auth/login", json={
            "username": name,
            "password": {"admin": "a-long-admin-password",
                         "operator": "a-long-operator-password",
                         "viewer": "a-long-viewer-password"}[name]})
        self.assertEqual(result.status_code, 200)
        return result.json()

    def create_incident(self, csrf, event_id=None, camera="CAM-01"):
        body = {"title": "Pemeriksaan gerbang", "camera_id": camera, "severity": "high"}
        if event_id is not None:
            body["event_id"] = event_id
        return self.client.post("/api/v1/incidents", json=body, headers={"X-GARDA-CSRF": csrf})

    def test_auth_and_csrf_roles_apply_to_all_incident_routes(self):
        self.assertEqual(self.client.get("/api/v1/incidents").status_code, 401)
        self.assertEqual(self.client.post("/api/v1/incidents", json={
            "title": "Unauthorized", "camera_id": "CAM-01"}).status_code, 401)
        viewer = self.login("viewer")
        self.assertEqual(self.client.get("/api/v1/incidents").status_code, 403)
        self.assertEqual(self.create_incident(viewer["csrf"]).status_code, 403)
        actor = self.login()
        self.assertEqual(self.create_incident("").status_code, 403)
        self.assertEqual(self.client.post("/api/v1/incidents", json={
            "title": "No origin", "camera_id": "CAM-01"},
            headers={"Origin": "https://unknown.example", "X-GARDA-CSRF": actor["csrf"]}).status_code, 403)
        incident = self.create_incident(actor["csrf"]).json()
        self.assertEqual(self.client.get("/api/v1/incidents").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/incidents/" + incident["id"]).status_code, 200)
        self.login("viewer")
        for suffix in ("", "/evidence-manifest"):
            self.assertEqual(self.client.get("/api/v1/incidents/" + incident["id"] + suffix).status_code, 403)
        self.assertEqual(self.client.post("/api/v1/incidents/" + incident["id"] + "/resolve",
                                          headers={"X-GARDA-CSRF": viewer["csrf"]}).status_code, 403)

    def test_operator_event_link_lifecycle_note_and_audit(self):
        actor = self.login("operator")
        created = self.create_incident(actor["csrf"], self.event_id)
        self.assertEqual(created.status_code, 201, created.text)
        incident_id = created.json()["id"]
        self.assertEqual(created.json()["status"], "open")
        self.assertEqual([x["id"] for x in created.json()["events"]], [self.event_id])
        self.assertEqual(self.create_incident(actor["csrf"], self.event_id).status_code, 409)
        self.assertEqual(self.client.post("/api/v1/incidents/" + incident_id + "/resolve",
                         headers={"X-GARDA-CSRF": actor["csrf"]}).status_code, 409)
        note = self.client.post("/api/v1/incidents/" + incident_id + "/notes",
                    json={"note": "Tunggu konfirmasi operator lain"},
                    headers={"X-GARDA-CSRF": actor["csrf"]})
        self.assertEqual(note.status_code, 200)
        self.assertEqual(note.json()["history"][-1]["action"], "note")
        ack = self.client.post("/api/v1/incidents/" + incident_id + "/acknowledge",
                               headers={"X-GARDA-CSRF": actor["csrf"]})
        self.assertEqual(ack.status_code, 200)
        self.assertEqual(ack.json()["status"], "acknowledged")
        self.assertEqual(self.client.post("/api/v1/incidents/" + incident_id + "/acknowledge",
                                          headers={"X-GARDA-CSRF": actor["csrf"]}).status_code, 409)
        resolved = self.client.post("/api/v1/incidents/" + incident_id + "/resolve",
                                    headers={"X-GARDA-CSRF": actor["csrf"]})
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.json()["status"], "resolved")
        self.assertEqual(self.client.post("/api/v1/incidents/" + incident_id + "/notes",
            json={"note": "late"}, headers={"X-GARDA-CSRF": actor["csrf"]}).status_code, 409)
        self.assertEqual(self.client.get("/api/v1/incidents?status=resolved").json()["count"], 1)
        self.assertEqual(self.client.get("/api/v1/incidents?status=unknown").status_code, 422)
        history = resolved.json()["history"]
        self.assertEqual([h["action"] for h in history], ["created", "note", "acknowledge", "resolve"])
        audit = self.app.state.unified.store.db.execute(
            "SELECT action FROM access_audit WHERE action LIKE 'incident:%'").fetchall()
        self.assertEqual(len(audit), 4)

    def test_event_camera_validation_and_missing_id(self):
        actor = self.login()
        self.assertEqual(self.create_incident(actor["csrf"], "missing-id").status_code, 404)
        self.assertEqual(self.create_incident(actor["csrf"], self.event_id, "CAM-02").status_code, 422)
        result = self.create_incident(actor["csrf"])
        self.assertEqual(result.status_code, 201)
        incident_id = result.json()["id"]
        wrong = self.app.state.unified.store.add_event("CAM-02", "Door", "motion")
        self.assertEqual(self.client.post("/api/v1/incidents/" + incident_id + "/events",
            json={"event_id": wrong}, headers={"X-GARDA-CSRF":actor["csrf"]}).status_code, 422)
        attach = self.client.post("/api/v1/incidents/" + incident_id + "/events",
            json={"event_id": self.event_id}, headers={"X-GARDA-CSRF":actor["csrf"]})
        self.assertEqual(attach.status_code, 200)
        self.assertEqual(attach.json()["events"][0]["id"], self.event_id)
        self.assertEqual(self.client.post("/api/v1/incidents/" + incident_id + "/events",
            json={"event_id": self.event_id}, headers={"X-GARDA-CSRF":actor["csrf"]}).status_code, 409)
        self.assertEqual(self.client.get("/api/v1/incidents/not-an-incident").status_code, 404)

    def test_snapshot_manifest_has_checksum_but_no_false_legal_hold_claim(self):
        actor = self.login()
        photo_id = self.app.state.unified.store.add_photo(
            self.event_id, np.zeros((32, 32, 3), dtype=np.uint8), "entry")
        incident = self.create_incident(actor["csrf"], self.event_id).json()
        response = self.client.get("/api/v1/incidents/" + incident["id"] + "/evidence-manifest")
        self.assertEqual(response.status_code, 200)
        manifest = response.json()
        self.assertEqual(manifest["snapshot_count"], 1)
        self.assertFalse(manifest["legal_hold"])
        self.assertFalse(manifest["signed_export"])
        self.assertEqual(manifest["photos"][0]["photo_id"], photo_id)
        path = self.app.state.unified.store.photo_path(self.event_id, photo_id)
        self.assertEqual(manifest["photos"][0]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertNotIn(str(Path(self.temp.name)), response.text)

    def test_incidents_persist_across_app_reopen(self):
        actor = self.login()
        incident_id = self.create_incident(actor["csrf"], self.event_id).json()["id"]
        self.client.__exit__(None, None, None)
        self.app = create_app(self.temp.name, unified=True)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.app.state.unified.identity.add_user("operator2", "another-long-password", "operator")
        self.login()
        result = self.client.get("/api/v1/incidents/" + incident_id)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["events"][0]["id"], self.event_id)


class ProtectedLaunchTests(unittest.TestCase):
    def test_protected_mode_requires_https_origin_and_secure_cookie(self):
        for value in ("", "http://localhost", "http://192.168.1.1",
                      "https://server.example/path", "https://user@server.example",
                      "https://server.example?token=bad"):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                validate_protected_launch(value, True)
        with self.assertRaises(RuntimeError):
            validate_protected_launch("https://garda.example.internal", False)
        self.assertIsNone(validate_protected_launch("https://garda.example.internal", True))
        self.assertIsNone(validate_protected_launch("https://garda.example.internal:8443", True))


if __name__ == "__main__":
    unittest.main()
