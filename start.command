#!/bin/bash
# Double-click on macOS (or run: bash start.command) to launch the local garden.
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3.11+ from python.org."
  read -r -p 'Press Return to close...'
  exit 1
fi
if [ ! -f .venv/bin/activate ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install -r requirements.txt
# Refresh accurate local build metadata after importing older live records.
python tools/build_deployment_manifest.py --collection not-run
# Fetch and cache authentic state outlines if network access permits. Safe offline.
python tools/cache_state_boundaries.py
# If an earlier Garden version is still running, use another local port.
# No processes are killed and no older project's data is changed.
PORT=$(python - <<'PYPORT'
import socket
for port in (8000, 8001, 8002, 8003):
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            continue
        print(port)
        break
else:
    raise SystemExit('Ports 8000–8003 are busy. Close another Garden Terminal and retry.')
PYPORT
)
printf '\nOpening The Garden of Democracy at http://127.0.0.1:%s\n' "$PORT"
( sleep 2; open "http://127.0.0.1:$PORT" ) &
exec python -m uvicorn server:app --host 127.0.0.1 --port "$PORT"
