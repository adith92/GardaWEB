# GARDA offline encrypted metadata backup & guarded restore — review candidate

**Status:** Source/test candidate, **NOT** disaster-recovery or KAK certification.  
**Target:** A single locally managed GARDA AI server data directory.  
**Security:** Password-prompted AES-256-GCM encryption; per-archive 16-byte random salt and 12-byte nonce; Scrypt password derivation; authenticated manifest/checksums. No cloud service or default passphrase.

## Backed up

- Consistent SQLite snapshots of `garda.db` and `identity.db` via SQLite's online backup API, including enrolled face templates stored in the GARDA database.
- Existing provider gallery databases at `templates/{sface,deepface,insightface}/garda.db` (if installed).
- `camera.key`, `cameras.encrypted`, `face.key` and `model-provisioning.json` if they exist.
- Optional existing JPEG snapshots under `evidence/` (enabled by default).

### Explicit exclusions and limitations

- **No** continuous RTSP/NVR recording segments, MediaMTX storage, external NAS, PostgreSQL from PR #9, media in Android local storage, model weights, Docker volumes, operating system configuration, TLS CA/private keys, or third-party VMS assets.
- A hard **128 MiB uncompressed** / **10,000 files** cap protects this metadata tool; use a separately designed disk/NAS/S3 backup for large video and evidence.
- Snapshots copied while a service writes can change between two files; individual stat stability is checked but this is **not an atomic multi-resource capture**. A complete site backup should quiesce services or use a coordinated snapshot.
- No continuous backup scheduler, retention policy, DR orchestration, signing or tested restore on alternate physical hardware is claimed.
- A valid backup requires protection and separate secure storage of the passphrase. Losing the passphrase means losing the ability to decrypt.
- Restore is **only to a never-created destination directory**; existing or live locations are rejected by design. No automatic cutover.

## Commands

From `projects/garda/ai-core` with `requirements-unified.txt` installed:

```sh
# Write an encrypted archive OUTSIDE the GARDA data directory.
python -m garda_ai.backup create --data ./var --output ../garda-metadata-2026-11-16.garda

# Verify authenticated archive and all per-file checksums.
python -m garda_ai.backup verify --archive ../garda-metadata-2026-11-16.garda

# Restore into a NEW path only; never run on an active server data path.
python -m garda_ai.backup restore --archive ../garda-metadata-2026-11-16.garda --new-data-dir ../garda-restored-test
```

Every command securely prompts for the passphrase without embedding it in shell history. `create` prompts twice. Use `--no-snapshots` to back up metadata only if the snapshot cap is exceeded.

### Recovery verification procedure

1. Run **restore into an isolated directory**; do not replace production data.
2. Validate the restored `garda.db` / `identity.db` using SQLite integrity checks with the server stopped.
3. Securely reprovision model weights, verify license/provenance and confirm `model-provisioning.json` paths match the new host.
4. Reconfigure TLS and network isolation separately, review cameras, users and permissions.
5. Only after a signed maintenance procedure, copy/cut over offline with restricted filesystem permissions.
6. Confirm event retrieval, camera configuration, biometric authorization, snapshot hashes, service restart and offline recovery. **No cutover automation is provided.**

## Codex verification / CI

```sh
PYTHONPATH=projects/garda/ai-core python -m pytest projects/garda/ai-core/tests/test_backup.py -q
PYTHONPATH=projects/garda/ai-core python -m pytest projects/garda/ai-core/tests -q
```

Test matrix: round trip with SQLite, encrypted camera secrets and JPEGs; snapshot exclusion; tampered ciphertext and wrong password failure; overwrite prevention; path traversal and symlink rejection; weak password and empty backup failure.

### Follow-up before GREEN PRODUCTION

Implement a dedicated recording archive backup/restore with retention/legal hold, encryption key custody, offsite replication, scheduled differential/incremental snapshots, online consistency coordination, and restore drills on physical hardware. Align 7-day Basic vs 90-day PUSADA contractual retention separately.

**Codex:** This feature is intentionally isolated from PR #9 (Fastify/Postgres/MediaMTX) and the incident-ledger PR. If other backends are selected, expand inventory and validate transactional recovery before acceptance.
