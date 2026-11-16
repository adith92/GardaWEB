"""Offline, authenticated-encrypted GARDA metadata/snapshot backup and restore.

This tool does NOT back up continuous NVR video, model weights, or certify DR.
Restore is intentionally restricted to a NEW data directory, never a live one.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import io
import json
import os
import secrets
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"GARDA-BACKUP-v1\n"
MAX_TOTAL = 128 * 1024 * 1024
MAX_FILES = 10000
SALT_BYTES = 16
NONCE_BYTES = 12
METADATA = ("camera.key", "cameras.encrypted", "face.key", "model-provisioning.json")
DATABASES = ("garda.db", "identity.db")


def _safe_name(name: str) -> bool:
    p = Path(name)
    if (not name or "\\" in name or name.startswith("/") or name.startswith(".") or
            "//" in name or ":" in name or p.is_absolute() or
            any(part in ("", ".", "..") for part in p.parts)):
        return False
    if name in METADATA or name in DATABASES:
        return True
    if name.startswith("templates/") and len(p.parts) == 3:
        return p.parts[2] == "garda.db" and p.parts[1] in ("sface", "deepface", "insightface")
    if name.startswith("evidence/") and len(p.parts) >= 3:
        return p.suffix.lower() == ".jpg"
    return False


def _read_checked(root: Path, source: Path) -> bytes:
    if source.is_symlink() or not source.resolve().is_relative_to(root.resolve()):
        raise ValueError("Refusing evidence/secret symlink or path escape")
    before = source.stat()
    if not source.is_file() or before.st_size > MAX_TOTAL:
        raise ValueError("Source file is missing or oversized")
    data = source.read_bytes()
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("Source changed during backup; retry from a stable state")
    return data


def _sqlite_snapshot(src: Path) -> bytes:
    """SQLite online-backup API gives a consistent snapshot of WAL-mode metadata."""
    if src.is_symlink():
        raise ValueError("Refusing SQLite symlink")
    with tempfile.TemporaryDirectory(prefix="garda-sqlite-") as folder:
        dst = Path(folder) / "snapshot.db"
        with sqlite3.connect(src.as_uri() + "?mode=ro", uri=True, timeout=20) as source:
            with sqlite3.connect(dst) as target:
                source.backup(target)
        if dst.stat().st_size > MAX_TOTAL:
            raise ValueError("SQLite snapshot too large for bounded backup")
        return dst.read_bytes()


def _collect(root: Path, include_snapshots: bool) -> dict[str, bytes]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("GARDA data directory must be a real directory")
    data = {}
    for name in DATABASES:
        file = root / name
        if file.is_file():
            data[name] = _sqlite_snapshot(file)
    for file in sorted((root / "templates").glob("*/garda.db")):
        name = file.relative_to(root).as_posix()
        if not _safe_name(name) or not file.resolve().is_relative_to(root.resolve()):
            raise ValueError("Unexpected template database path")
        data[name] = _sqlite_snapshot(file)
    for name in METADATA:
        file = root / name
        if file.exists() or file.is_symlink():
            data[name] = _read_checked(root, file)
    if include_snapshots and (root / "evidence").exists():
        if (root / "evidence").is_symlink():
            raise ValueError("Refusing symlinked evidence root")
        for file in sorted((root / "evidence").rglob("*")):
            if file.is_symlink():
                raise ValueError("Symlink inside evidence directory is forbidden")
            if file.is_file():
                name = file.relative_to(root).as_posix()
                if not _safe_name(name):
                    raise ValueError("Unexpected evidence file path: " + name)
                data[name] = _read_checked(root, file)
                if len(data) > MAX_FILES or sum(map(len, data.values())) > MAX_TOTAL:
                    raise ValueError("Snapshot inventory exceeds bounded backup size")
    if not any(name in data for name in DATABASES):
        raise ValueError("No GARDA metadata DB found; refuse empty backup")
    if len(data) > MAX_FILES or sum(map(len, data.values())) > MAX_TOTAL:
        raise ValueError("GARDA metadata exceeds bounded backup size")
    return data


def _archive(data: dict[str, bytes]) -> bytes:
    entries = [{"path": k, "bytes": len(v), "sha256": hashlib.sha256(v).hexdigest()}
               for k, v in sorted(data.items())]
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        bundle.writestr("manifest.json", json.dumps({"format": 1, "files": entries},
                                                     separators=(",", ":"), sort_keys=True))
        for name, payload in sorted(data.items()):
            bundle.writestr("files/" + name, payload)
    return output.getvalue()


def _key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.scrypt(passphrase.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)


def create_backup(data_dir: str | Path, archive: str | Path, passphrase: str,
                  include_snapshots: bool = True) -> dict:
    if len(passphrase) < 16:
        raise ValueError("Use a backup passphrase of at least 16 characters")
    root = Path(data_dir).resolve()
    output = Path(archive).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("Refusing to overwrite an existing backup")
    if output.resolve().is_relative_to(root):
        raise ValueError("Backup archive must be outside the GARDA data directory")
    data = _collect(root, include_snapshots)
    salt, nonce = secrets.token_bytes(SALT_BYTES), secrets.token_bytes(NONCE_BYTES)
    ciphertext = AESGCM(_key(passphrase, salt)).encrypt(nonce, _archive(data), MAGIC)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(MAGIC + salt + nonce + ciphertext)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return {"files": len(data), "bytes_uncompressed": sum(len(x) for x in data.values()),
            "snapshots_included": include_snapshots, "encrypted": True}


def _unseal(archive: str | Path, passphrase: str) -> dict[str, bytes]:
    path = Path(archive)
    if path.is_symlink() or path.stat().st_size > MAX_TOTAL + 8 * 1024 * 1024:
        raise ValueError("Invalid or oversized backup archive")
    raw = path.read_bytes()
    head = len(MAGIC)
    if not raw.startswith(MAGIC) or len(raw) < head + SALT_BYTES + NONCE_BYTES + 16:
        raise ValueError("Not a GARDA encrypted backup")
    salt = raw[head:head + SALT_BYTES]
    nonce = raw[head + SALT_BYTES:head + SALT_BYTES + NONCE_BYTES]
    # Invalid password and tampering both fail closed with authentication error.
    plain = AESGCM(_key(passphrase, salt)).decrypt(nonce, raw[head + SALT_BYTES + NONCE_BYTES:], MAGIC)
    records = {}
    with zipfile.ZipFile(io.BytesIO(plain), "r") as bundle:
        infos = bundle.infolist()
        if len(infos) > MAX_FILES + 1 or len({i.filename for i in infos}) != len(infos):
            raise ValueError("Unexpected archive inventory")
        manifest_info = bundle.getinfo("manifest.json")
        if manifest_info.file_size > 4 * 1024 * 1024:
            raise ValueError("Manifest too large")
        manifest = json.loads(bundle.read(manifest_info))
        if manifest.get("format") != 1 or not isinstance(manifest.get("files"), list):
            raise ValueError("Unknown manifest format")
        declared = manifest["files"]
        names = [item.get("path") for item in declared]
        if (len(names) > MAX_FILES or len(names) != len(set(names)) or
                any(not isinstance(name, str) or not _safe_name(name) for name in names) or
                set(i.filename for i in infos) != {"manifest.json"} | {"files/" + name for name in names}):
            raise ValueError("Unexpected backup paths")
        total = 0
        for entry in declared:
            name = entry["path"]
            info = bundle.getinfo("files/" + name)
            total += info.file_size
            if info.file_size > MAX_TOTAL or total > MAX_TOTAL:
                raise ValueError("Backup expands beyond allowed limit")
            payload = bundle.read(info)
            if (entry.get("bytes") != len(payload) or
                    entry.get("sha256") != hashlib.sha256(payload).hexdigest()):
                raise ValueError("Backup checksum mismatch")
            records[name] = payload
    if not any(name in records for name in DATABASES):
        raise ValueError("Missing required GARDA metadata DB")
    return records


def verify_backup(archive: str | Path, passphrase: str) -> dict:
    data = _unseal(archive, passphrase)
    return {"verified": True, "files": len(data),
            "bytes_uncompressed": sum(len(x) for x in data.values())}


def restore_backup(archive: str | Path, new_data_dir: str | Path, passphrase: str) -> dict:
    """Restore to a NEW directory only; no in-place overwrites or live DB replacement."""
    target = Path(new_data_dir).absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError("Restore directory must not exist; never overwrite running GARDA")
    data = _unseal(archive, passphrase)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".garda-restore-", dir=target.parent) as stage:
        staging = Path(stage)
        for name, payload in sorted(data.items()):
            dest = staging / name
            dest.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
        # stage still holds all validated bytes, replace into a non-existing destination.
        os.rename(staging, target)
    return {"restored": True, "files": len(data), "location": str(target),
            "requires_operator_validation": True}


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline GARDA metadata/snapshot backup (NOT NVR video)")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--data", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--no-snapshots", action="store_true")
    verify = sub.add_parser("verify")
    verify.add_argument("--archive", required=True)
    restore = sub.add_parser("restore")
    restore.add_argument("--archive", required=True)
    restore.add_argument("--new-data-dir", required=True)
    args = parser.parse_args()
    password = getpass.getpass("GARDA backup passphrase (never logged): ")
    if args.command == "create":
        if password != getpass.getpass("Confirm backup passphrase: "):
            raise ValueError("Passphrases do not match")
        outcome = create_backup(args.data, args.output, password,
                                include_snapshots=not args.no_snapshots)
    elif args.command == "verify":
        outcome = verify_backup(args.archive, password)
    else:
        outcome = restore_backup(args.archive, args.new_data_dir, password)
    print(json.dumps(outcome, ensure_ascii=False))


if __name__ == "__main__":
    main()
