#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
HOST_IP="${1:?Usage: bash setup-server.sh LAN-IP [recording-folder] [data-folder]}"
RECORDING_ROOT="${2:-/var/lib/garda-recordings}"
DATA_ROOT="${3:-/var/lib/garda}"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-unified.txt 'fast-alpr[onnx]==0.4.0'
.venv/bin/python -m garda_ai.server provision-ai --data "$DATA_ROOT"
.venv/bin/python -m garda_ai.server configure-nvr --data "$DATA_ROOT" --nvr-binary "$PWD/bin/mediamtx" --recordings-root "$RECORDING_ROOT" --retention-days 1
.venv/bin/python -m garda_ai.server configure-https --data "$DATA_ROOT" --host "$HOST_IP" --web-root "$PWD/web"
printf '%s\n' 'Setup complete. Run .venv/bin/python -m garda_ai.server serve --data <data-folder>; install the systemd unit for boot recovery.'
