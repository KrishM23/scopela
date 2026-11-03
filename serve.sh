#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/site"
PORT="${1:-8787}"
echo "SCOPE LA oral health map → http://127.0.0.1:${PORT}"
python3 -m http.server "$PORT" --bind 127.0.0.1
