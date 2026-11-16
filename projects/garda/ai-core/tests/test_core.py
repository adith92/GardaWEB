from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from garda_ai.config import CameraConfig, load_config
from garda_ai.processor import FaceSessions, FrameProcessor, PlateConsensus, overlap
from garda_ai.storage import EventStore
from garda_ai.vision import Detection, MotionDetector, crop_box


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = EventStore(self.temp.name)
        self.frame = np.full((144, 256, 3), 80, dtype=np.uint8)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_event_photo_and_search(self):
        eid = self.store.add_event("gate01", "Gate", "plate", .93, "B1234XYZ")
        pid = self.store.add_photo(eid, self.frame, "plate")
        result = self.store.list_events(kind="plate", plate_prefix="b12")
        self.assertEqual(result[0]["plate_text"], "B1234XYZ")
        self.assertEqual(self.store.stats()["plate"], 1)
        self.assertEqual(len(self.store.event_photos(eid)), 1)
        self.assertTrue(self.store.photo_path(eid, pid).is_file())
        self.assertIsNone(self.store.photo_path("wrong", pid))
        self.assertIsNone(self.store.photo_path(eid, "not-found"))

    def test_retention_purges_file_and_event(self):
        when = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        eid = self.store.add_event("gate01", "Gate", "motion", when=when)
        pid = self.store.add_photo(eid, self.frame, "scene")
        self.assertTrue(self.store.photo_path(eid, pid).exists())
        deleted = self.store.purge(90)
        self.assertEqual(deleted, {"events": 1, "photos": 1})
        self.assertEqual(self.store.list_events(), [])
        self.assertIsNone(self.store.photo_path(eid, pid))

    def test_refuses_invalid_kinds_and_labels(self):
        with self.assertRaises(ValueError):
            self.store.add_event("gate", "Gate", "unknown")
        eid = self.store.add_event("gate", "Gate", "face")
        with self.assertRaises(ValueError):
            self.store.add_photo(eid, self.frame, "../bad")

    def test_audit_does_not_embed_secret(self):
        self.store.audit("list_events")
        count = self.store.db.execute("SELECT COUNT(*) FROM access_audit").fetchone()[0]
        self.assertEqual(count, 1)


class VisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = EventStore(self.temp.name)
        self.camera = CameraConfig("gate1", "rtsp://localhost:554/", "Gate Entrance")
        self.frame = np.full((240, 320, 3), 100, dtype=np.uint8)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_face_sighting_three_snapshots_and_revisit(self):
        faces = FaceSessions(self.store, self.camera)
        detection = [Detection((30, 40, 90, 120), 0.86)]
        self.assertEqual(len(faces.update(self.frame, detection, 0.0)), 1)
        self.assertEqual(faces.update(self.frame, detection, 0.3), [])
        self.assertEqual(faces.update(self.frame, detection, 0.7), [])
        self.assertEqual(faces.update(self.frame, detection, 1.4), [])
        rows = self.store.list_events(kind="face")
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(self.store.event_photos(rows[0]["id"])), 6)
        self.assertEqual(len(faces.update(self.frame, detection, 7.0)), 1)
        self.assertEqual(len(self.store.list_events(kind="face")), 2)

    def test_plate_needs_two_confirmations_and_cooldown(self):
        plates = PlateConsensus(self.store, self.camera)
        detection = [Detection((65, 90, 165, 130), .91, "B1234XYZ")]
        self.assertEqual(plates.update(self.frame, detection, 0.0), [])
        self.assertEqual(len(plates.update(self.frame, detection, 1.0)), 1)
        self.assertEqual(plates.update(self.frame, detection, 2.0), [])
        self.assertEqual(len(self.store.list_events(kind="plate")), 1)
        saved = self.store.list_events(kind="plate")[0]
        self.assertEqual(saved["plate_text"], "B1234XYZ")
        self.assertEqual(len(self.store.event_photos(saved["id"])), 2)
        self.assertEqual(plates.update(self.frame, detection, 10.0), [])
        self.assertEqual(plates.update(self.frame, detection, 67.0), [])
        self.assertEqual(len(plates.update(self.frame, detection, 68.0)), 1)
        self.assertEqual(len(self.store.list_events(kind="plate")), 2)

    def test_motion_warmup_and_changes(self):
        motion = MotionDetector(minimum_fraction=.015, warmup_frames=5)
        for _ in range(8):
            self.assertFalse(motion.detect(np.zeros((120, 200, 3), dtype=np.uint8))[0])
        frame = np.zeros((120, 200, 3), dtype=np.uint8)
        frame[35:85, 60:140] = 255
        active, fraction = motion.detect(frame)
        self.assertTrue(active)
        self.assertGreater(fraction, .01)

    def test_crop_never_exceeds_bounds(self):
        box = crop_box(self.frame, (-20, -10, 400, 290))
        self.assertEqual(box.shape, self.frame.shape)
        self.assertEqual(overlap((0,0,20,20),(0,0,20,20)), 1)
        self.assertEqual(overlap((0,0,20,20),(30,30,50,50)), 0)

    def test_processor_uses_fake_detectors(self):
        class FakeFace:
            def detect(self, frame):
                return [Detection((30, 30, 80, 80), 0.89)]
        class FakePlate:
            def detect(self, frame):
                return [Detection((130, 120, 220, 155), .85, "D1234AX")]
        p = FrameProcessor(self.camera, self.store, FakeFace(), FakePlate())
        p.motion.detect = lambda frame: (False, 0.0)
        self.assertEqual(p.process(self.frame, now=0)["face"], 1)
        self.assertEqual(p.process(self.frame, now=1)["face"], 0)
        self.assertEqual(p.process(self.frame, now=6)["plate"], 1)
        self.assertEqual(self.store.stats()["plate"], 1)


class ConfigurationTests(unittest.TestCase):
    def test_no_urls_in_config_and_bounded_camera_count(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps({"cameras": [{"id":"gate1", "rtsp_env":"GARDA_TEST_CAMERA_RTSP"}]}))
            with patch.dict(os.environ, {"GARDA_TEST_CAMERA_RTSP": "rtsp://localhost:554/"}):
                config = load_config(path)
                self.assertEqual(config.cameras[0].id, "gate1")
            with patch.dict(os.environ, {"GARDA_TEST_CAMERA_RTSP": ""}):
                with self.assertRaises(ValueError):
                    load_config(path)
            path.write_text(json.dumps({"cameras": []}))
            with self.assertRaises(ValueError):
                load_config(path)

    def test_api_requires_real_key_and_guards_evidence(self):
        from garda_ai.api import create_app
        from fastapi.testclient import TestClient
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(RuntimeError):
                create_app(folder, "short")
            app = create_app(folder, "a-very-long-random-secret-for-tests")
            with TestClient(app) as client:
                self.assertEqual(client.get("/health").status_code, 200)
                self.assertEqual(client.get("/api/events").status_code, 401)
                headers={"X-GARDA-KEY": "a-very-long-random-secret-for-tests"}
                self.assertEqual(client.get("/api/events", headers=headers).status_code, 200)
                self.assertEqual(client.get("/api/stats", headers=headers).json()["face"], 0)
                self.assertEqual(client.get("/api/events/notfound/photos/x", headers=headers).status_code, 404)


if __name__ == "__main__":
    unittest.main()
