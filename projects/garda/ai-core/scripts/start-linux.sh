#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${GARDA_AI_API_KEY:?Missing GARDA_AI_API_KEY}"
: "${GARDA_CAMERA_PTZ_RTSP:?Missing GARDA_CAMERA_PTZ_RTSP}"
: "${GARDA_CAMERA_WIDE_RTSP:?Missing GARDA_CAMERA_WIDE_RTSP}"
.venv/bin/python -m garda_ai check --config config.json
.venv/bin/python -m garda_ai api --listen 127.0.0.1 --port 8808 &
API_PID=$!
trap 'kill "$API_PID" 2>/dev/null || true' EXIT INT TERM
.venv/bin/python -m garda_ai run --config config.json
