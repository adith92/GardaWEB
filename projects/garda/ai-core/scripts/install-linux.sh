#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
test -f config.json || cp config.example.json config.json
echo "Set env vars GARDA_CAMERA_*_RTSP, GARDA_AI_API_KEY; then scripts/start-linux.sh"
