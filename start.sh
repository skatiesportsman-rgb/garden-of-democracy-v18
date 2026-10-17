#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pip install -r requirements.txt
python tools/build_deployment_manifest.py --collection not-run
exec python -m uvicorn server:app --host 127.0.0.1 --port 8000
