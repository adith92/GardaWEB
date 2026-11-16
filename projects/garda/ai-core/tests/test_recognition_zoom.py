"""Synthetic, local-only checks for biometric enrollment and ONVIF zoom.

No CCTV is contacted and no real faces/number plates are supplied.
"""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from cryptography.fernet import Fernet

from garda_ai.recognition import FaceGallery
from garda_ai.config import CameraConfig
from garda_ai.processor import FaceSessions
from garda_ai.storage import EventStore
from garda_ai.vision import Detection
from garda_ai.zoom import ZoomController, validate_host


class GalleryTests(unittest.TestCase):
    def test_templates_encrypted_decrypt_and_revocation(self):
        with tempfile.TemporaryDirectory() as temp:
            key = Fernet.generate_key().decode("ascii")
            gallery = FaceGallery(Path(temp), key)
            feature = np.arange(128, dtype=np.float32).reshape(1, 128)
            record_id = gallery.enroll("Authorized Tester", feature, "permission-2026-001")
            raw = gallery.db.execute(
                "SELECT feature_cipher FROM enrolled_faces WHERE id=?", (record_id,)
            ).fetchone()[0]
            self.assertNotIn(b"[0.0, 1.0", raw)
            self.assertTrue(raw.startswith(b"gAAAA"))
            matches = gallery.registered()
            self.assertEqual(matches[0][0], "Authorized Tester")
            np.testing.assert_allclose(matches[0][1], feature)
            self.assertTrue(gallery.revoke(record_id))
            self.assertEqual(gallery.registered(), [])
            gallery.close()

    def test_wrong_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            key = Fernet.generate_key().decode("ascii")
            gallery = FaceGallery(Path(temp), key)
            gallery.enroll("Test", np.ones(128, np.float32), "explicit-consent")
            gallery.close()
            wrong = FaceGallery(Path(temp), Fernet.generate_key().decode("ascii"))
            with self.assertRaises(RuntimeError):
                wrong.registered()
            wrong.close()

    def test_consent_reference_required(self):
        with tempfile.TemporaryDirectory() as temp:
            gallery = FaceGallery(Path(temp), Fernet.generate_key().decode("ascii"))
            with self.assertRaises(ValueError):
                gallery.enroll("Tester", np.ones(128, np.float32), "")
            gallery.close()

    def test_face_sighting_writes_optional_match_label(self):
        with tempfile.TemporaryDirectory() as temp:
            store = EventStore(temp)
            camera = CameraConfig(id="gate", url="rtsp://localhost/door", location="Gate")
            sessions = FaceSessions(store, camera)
            fake_frame = np.zeros((200, 300, 3), np.uint8)
            face = Detection((10, 20, 90, 130), .92)
            matcher = SimpleNamespace(match=lambda frame, face: ("Enrolled Tester", .82))
            ids = sessions.update(fake_frame, [face], now=1.0, matcher=matcher)
            self.assertEqual(len(ids), 1)
            item = store.list_events(kind="face")[0]
            self.assertEqual(item["face_label"], "Enrolled Tester")
            self.assertAlmostEqual(item["face_similarity"], .82)
            self.assertGreaterEqual(len(store.event_photos(ids[0])), 2)
            store.close()


class ZoomTests(unittest.TestCase):
    def test_public_camera_blocked(self):
        with self.assertRaises(ValueError):
            validate_host("8.8.8.8")
        self.assertEqual(validate_host("192.168.18.249"), "192.168.18.249")
        with self.assertRaises(ValueError):
            validate_host("https://attacker.example")

    def test_zoom_is_bounded_and_always_stops(self):
        class FakePtz:
            def __init__(self):
                self.moves = []
                self.stops = []
            def create_type(self, name):
                return SimpleNamespace()
            def ContinuousMove(self, request):
                self.moves.append(request)
            def Stop(self, request):
                self.stops.append(request)

        controller = object.__new__(ZoomController)
        controller.ptz = FakePtz()
        controller.profile = SimpleNamespace(token="ptz0")
        controller.inspect = lambda: {"zoom_supported": True}
        result = controller.pulse("in", 0.1, 0.6)
        self.assertTrue(result["acknowledged"])
        self.assertFalse(result["physical_zoom_verified"])
        self.assertEqual(len(controller.ptz.moves), 1)
        self.assertEqual(len(controller.ptz.stops), 1)
        self.assertTrue(controller.ptz.stops[0].Zoom)

    def test_zoom_unsupported_never_moves(self):
        controller = object.__new__(ZoomController)
        controller.inspect = lambda: {"zoom_supported": False}
        with self.assertRaises(RuntimeError):
            controller.pulse("in", .2, .5)


if __name__ == "__main__":
    unittest.main()
