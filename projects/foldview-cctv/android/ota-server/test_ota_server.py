import hashlib
import tempfile
import unittest
from pathlib import Path

from garda_ota_server import build_manifest


class ServerManifestTests(unittest.TestCase):
    def test_manifest_matches_local_apk_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            content = b"GARDA TEST ONLY" * 12_000
            apk = Path(d) / "GARDA-test.apk"
            apk.write_bytes(content)
            manifest = build_manifest(apk, "192.168.18.3", 8877, 13, "0.11.0", "Fix")
            self.assertEqual(manifest["packageName"], "org.foldview.cctv")
            self.assertEqual(manifest["versionCode"], 13)
            self.assertEqual(manifest["sizeBytes"], len(content))
            self.assertEqual(manifest["sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(manifest["apkUrl"], "http://192.168.18.3:8877/GARDA-update.apk")

    def test_standard_edition_manifest_uses_distinct_package(self):
        with tempfile.TemporaryDirectory() as d:
            apk = Path(d) / "GARDA-standard.apk"
            apk.write_bytes(b"GARDA STANDARD TEST" * 10000)
            manifest = build_manifest(apk, "192.168.18.3", 8878, 14, "0.12.0",
                                      "Standard release", "org.garda.cctv.standard")
            self.assertEqual(manifest["packageName"], "org.garda.cctv.standard")
            self.assertEqual(manifest["versionCode"], 14)
            self.assertTrue(manifest["apkUrl"].endswith(":8878/GARDA-update.apk"))

    def test_refuses_non_apk(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "not-an-apk.zip"
            path.write_bytes(b"x" * 120_000)
            with self.assertRaises(ValueError):
                build_manifest(path, "192.168.18.3", 8877, 13, "0.11.0")

    def test_refuses_invalid_build(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "app.apk"
            path.write_bytes(b"x" * 120_000)
            with self.assertRaises(ValueError):
                build_manifest(path, "192.168.18.3", 8877, 0, "0.0")


if __name__ == "__main__":
    unittest.main()
