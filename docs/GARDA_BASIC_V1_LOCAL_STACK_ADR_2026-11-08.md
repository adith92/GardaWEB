# Architecture Decision: GARDA Basic v1 Local-First
Date: 2026-11-08. Decision for implementation preparation, not formal PUSADA procurement acceptance.

## Database recommendation
Use LOCAL PostgreSQL 18.6 for metadata (camera registry, encrypted RTSP source configuration, event/incident, permissions and audit). Store large video fMP4 segments on a separately mounted local disk rather than as database BLOBs.
Do not depend on Supabase Cloud or Vercel for local recording, authentication or data availability. Supabase can run fully self-hosted with Docker, but its complete service suite adds operational load. Evaluate it after local recorder and RBAC work; PostgreSQL now preserves compatibility.

## Version decisions checked against documentation
- Node 24 / Fastify 5.12.8 / @fastify/helmet 13.2.0 / pg 8.23.1
- PostgreSQL Docker image 18.6-bookworm, data volume at /var/lib/postgresql
- MediaMTX Docker image 1.21.3 with dynamic Control API paths and 7-day fMP4 segments
- Existing React frontend remains unchanged. Any dependency migration to latest React/Vite must be separately tested with existing UI.
- Direct dependency pins are present; audit transitive dependencies with a lockfile before production.

## Already in development branch
API for local encrypted camera registration, camera list and statuses, MediaMTX path recovery, recording index query, metadata schema, minimal audit, Docker Compose with loopback-only media/control HTTP endpoints, Node security tests.

## Not yet implemented or accepted
Live LAN browser video player, ONVIF discovery/PTZ, multiuser auth/RBAC/MFA, video retention holds and export, production backup/restore, AI Lite, storage calculation, TLS termination, UAT, full PUSADA 90-day KAK.
The admin token is a temporary bootstrap credential and must never be used as a substitute for real user authorization.

## Owner-fixed delivery timeline
8 weeks implementation, 2 weeks testing/UAT/commissioning, 12 months warranty and support from BAST. KAK scope is separately reviewed by PPK.

## Document precedence
AGENTS.md; decision register v0.3 (including October 16 V2 branch changes); GARDA_TIER1_BASIC_PRD_v1.0_DRAFT; PUSADA KAK gap matrix; infra/basic-v1/README.md; GitHub issue #8.

Official references:
https://supabase.com/docs/guides/self-hosting/docker
https://github.com/bluenviron/mediamtx/releases/tag/v1.21.3
https://github.com/bluenviron/mediamtx/blob/v1.21.3/api/openapi.yaml
https://github.com/fastify/fastify/blob/v5.12.7/docs/Guides/Migration-Guide-V5.md
https://www.postgresql.org/docs/18/
