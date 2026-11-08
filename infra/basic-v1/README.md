# GARDA Basic v1.0: on-prem LAN foundation
Status: development scaffold only. NOT deployed, camera-tested, production-secured or KAK accepted.

## Stack
PostgreSQL 18.6 (metadata), Fastify 5.12.8 / Node 24 (local API), node-postgres 8.23.1, MediaMTX 1.21.3 (RTSP ingest and local fMP4 recording). The existing React/Vite UI stays a synthetic demo until the browser video player is integrated.

## Local Linux lab setup
1. From repository root copy example env:
   cp infra/basic-v1/.env.example infra/basic-v1/.env
2. Generate four DIFFERENT secrets with openssl rand -hex 32 for POSTGRES_PASSWORD, GARDA_ADMIN_TOKEN, GARDA_CAMERA_KEY_HEX and MEDIAMTX_API_PASSWORD. Replace example placeholders. Use URL-safe values for Postgres password.
3. chmod 600 infra/basic-v1/.env
4. For production, set GARDA_RECORDINGS_DIR to a separate mounted video disk, not OS filesystem.
5. Start services from repository root:
   docker compose --env-file infra/basic-v1/.env -f infra/basic-v1/docker-compose.yml up -d --build
6. Inspect:
   docker compose --env-file infra/basic-v1/.env -f infra/basic-v1/docker-compose.yml ps
   curl http://127.0.0.1:8088/healthz
7. Read admin token on the local server:
   set -a; . infra/basic-v1/.env; set +a
   curl -H "Authorization: Bearer $GARDA_ADMIN_TOKEN" http://127.0.0.1:8088/v1/cameras
8. To register physical CCTV securely, make /secure/path/camera-registration.json outside Git, with 0600 permissions. Content:
   { "name": "Test CCTV", "rtspUrl": "rtsp://user:password@192.168.x.x:554/live" }
   Then on server:
   curl -X POST http://127.0.0.1:8088/v1/cameras -H "Authorization: Bearer $GARDA_ADMIN_TOKEN" -H "Content-Type: application/json" --data-binary @/secure/path/camera-registration.json
9. Query the returned ID:
   GET /v1/cameras/:id/status
   GET /v1/cameras/:id/recordings
   Both endpoints require the bearer token.
10. Test physical storage path for new fMP4 segments, camera outage/reconnect, browser closed, API restart, MediaMTX restart and power loss.

## Important safety limits
- Bootstrap bearer token is not full RBAC, MFA or operator session management.
- API and HLS/RTSP/playback are published on HOST LOOPBACK ONLY. No browser streaming across LAN until secured same-origin media gateway and per-user authorization are built.
- The database is internal to Docker; no Postgres port is published. RTSP camera sources are encrypted AES-256-GCM at rest using GARDA_CAMERA_KEY_HEX.
- The MediaMTX control API is not exposed to the host. Internal dedicated user password is injected using MTX_AUTHINTERNALUSERS_0_PASS.
- Recorder defaults to 7-day rolling segments, but evidence legal-hold protection is NOT implemented. Do not use for critical/customer evidence until protected retention is added and verified.
- Never commit camera RTSP URLs, credentials, network addresses, production video, personal data, or classified data.
- Supabase self-hosted may be added later if there is concrete need for Auth/Realtime/Storage. Supabase Cloud is not a required dependency.
- PUSADA KAK 90-day retention, face identity, Ask Garda and enterprise infrastructure remain separate gap items. Basic product must not be represented as KAK compliant.

## Test
From services/garda-api run: npm install && npm run check && npm test
Direct dependencies are pinned, but a lockfile is not yet generated; review/commit lockfile before production.
CLI logic checks do NOT prove a working camera, disk performance, video export, UAT or operational security.

## Next implementation
Secure local user login/RBAC and stream proxy; ONVIF discovery/capability; HLS/WebRTC frontend component; real timeline/playback/export; protected evidence Vault; incident and audit hardening; offline NVR backup verification; person/face presence and ANPR Lite workers.
