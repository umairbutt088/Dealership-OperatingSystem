#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt
echo "Open http://127.0.0.1:8765/"
exec uvicorn dealershipos.main:app --host 127.0.0.1 --port 8765
