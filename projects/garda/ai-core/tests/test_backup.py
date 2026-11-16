"""Offline encrypted GARDA metadata archive regression tests; synthetic files only."""
import os
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from cryptography.exceptions import InvalidTag

from garda_ai.backup import create_backup, verify_backup, restore_backup, _safe_name


class BackupRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "live"
        self.root.mkdir()
        for name in ("garda.db", "identity.db"):
            with closing(sqlite3.connect(self.root / name)) as db, db:
                db.execute("CREATE TABLE items (value TEXT NOT NULL)")
                db.execute("INSERT INTO items VALUES (?)", ("secret-" + name,))
        (self.root / "camera.key").write_bytes(b"camera-key-lab")
        (self.root / "face.key").write_bytes(b"face-key-lab")
        (self.root / "cameras.encrypted").write_bytes(b"encrypted-camera-data")
        evidence = self.root / "evidence" / "2026-11-16" / "CAM-01"
        evidence.mkdir(parents=True)
        (evidence / "abc.jpg").write_bytes(b"synthetic-jpeg-image")
        template = self.root / "templates" / "sface"
        template.mkdir(parents=True)
        with closing(sqlite3.connect(template / "garda.db")) as db, db:
            db.execute("CREATE TABLE reference (label TEXT)")
            db.execute("INSERT INTO reference VALUES ('reference-one')")
        self.archive = Path(self.temp.name) / "backup.garda"
        self.password = "a-long-offline-backup-passphrase"

    def tearDown(self):
        self.temp.cleanup()

    def test_round_trip_and_sqlite_wal_safe_metadata(self):
        summary = create_backup(self.root, self.archive, self.password)
        self.assertTrue(summary["encrypted"])
        self.assertEqual(summary["files"], 7)
        raw = self.archive.read_bytes()
        self.assertNotIn(b"secret-garda.db", raw)
        self.assertNotIn(b"camera-key-lab", raw)
        self.assertTrue(verify_backup(self.archive, self.password)["verified"])
        target = Path(self.temp.name) / "restored"
        result = restore_backup(self.archive, target, self.password)
        self.assertTrue(result["restored"])
        self.assertTrue(result["requires_operator_validation"])
        self.assertEqual((target / "camera.key").read_bytes(), b"camera-key-lab")
        self.assertEqual((target / "cameras.encrypted").read_bytes(), b"encrypted-camera-data")
        self.assertEqual((target / "evidence/2026-11-16/CAM-01/abc.jpg").read_bytes(),
                         b"synthetic-jpeg-image")
        with closing(sqlite3.connect(target / "garda.db")) as db:
            self.assertEqual(db.execute("SELECT value FROM items").fetchone()[0],
                             "secret-garda.db")
        with closing(sqlite3.connect(target / "templates/sface/garda.db")) as db:
            self.assertEqual(db.execute("SELECT label FROM reference").fetchone()[0],
                             "reference-one")

    def test_password_tamper_and_overwrite_fail_closed(self):
        create_backup(self.root, self.archive, self.password)
        with self.assertRaises((InvalidTag, ValueError)):
            verify_backup(self.archive, "incorrect-passphrase")
        raw = bytearray(self.archive.read_bytes())
        raw[-1] ^= 0x01
        corrupted = Path(self.temp.name) / "tampered.garda"
        corrupted.write_bytes(raw)
        with self.assertRaises((InvalidTag, ValueError)):
            verify_backup(corrupted, self.password)
        with self.assertRaises(FileExistsError):
            create_backup(self.root, self.archive, self.password)
        existing = Path(self.temp.name) / "existing"
        existing.mkdir()
        with self.assertRaises(FileExistsError):
            restore_backup(self.archive, existing, self.password)

    def test_snapshot_opt_out_and_source_symlink_rejected(self):
        create_backup(self.root, self.archive, self.password, include_snapshots=False)
        target = Path(self.temp.name) / "restored"
        restore_backup(self.archive, target, self.password)
        self.assertFalse((target / "evidence").exists())
        self.assertTrue((target / "garda.db").exists())
        self.assertFalse(_safe_name("../garda.db"))
        self.assertFalse(_safe_name("evidence/../../camera.key"))
        self.assertFalse(_safe_name("evidence/foo/script.py"))
        self.assertFalse(_safe_name("/etc/passwd"))
        if os.name != "nt":
            evil = self.root / "camera.key"
            evil.unlink()
            evil.symlink_to(self.archive)
            with self.assertRaises(ValueError):
                create_backup(self.root, Path(self.temp.name) / "bad.garda", self.password)

    def test_reject_weak_passphrase_and_empty_metadata(self):
        with self.assertRaises(ValueError):
            create_backup(self.root, self.archive, "short")
        empty = Path(self.temp.name) / "empty"
        empty.mkdir()
        with self.assertRaises(ValueError):
            create_backup(empty, self.archive, self.password)


if __name__ == "__main__":
    unittest.main()
