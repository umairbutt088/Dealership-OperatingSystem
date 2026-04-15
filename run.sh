#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"
echo "Open http://${HOST}:${PORT}/"
exec uvicorn dealershipos.main:app --host "${HOST}" --port "${PORT}"
