#!/usr/bin/env python3
"""Write *public, non-secret* metadata for the deployed static garden.

Publication freshness and ingestion freshness remain distinct. Run only after
snapshot audit. No API credentials or external source content are included.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json, os, sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ALLOWED = {'success', 'partial', 'failed', 'not-run'}


def manifest(snapshot: dict, *, now: datetime | None = None, collection: str = 'not-run', environ: dict | None = None) -> dict:
    if collection not in ALLOWED:
        raise ValueError('Unknown collection outcome')
    env = os.environ if environ is None else environ
    now = now or datetime.now(timezone.utc)
    sources = snapshot.get('sources') or []
    if not isinstance(sources, list):
        sources = []
    status_counts = {kind: sum(1 for s in sources if isinstance(s, dict) and s.get('status') == kind)
                     for kind in ('operational', 'temporarily-unavailable', 'credentials-required')}
    sha = str(env.get('GITHUB_SHA', ''))
    sha = sha[:12] if re.fullmatch(r'[a-fA-F0-9]{40}', sha) else None
    event = str(env.get('GITHUB_EVENT_NAME', 'local'))
    if event not in ('push', 'schedule', 'workflow_dispatch'):
        event = 'local'
    repo = str(env.get('GITHUB_REPOSITORY', ''))
    run_id = str(env.get('GITHUB_RUN_ID', ''))
    run_url = f'https://github.com/{repo}/actions/runs/{run_id}' if re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) and re.fullmatch(r'\d+', run_id) else None
    return {
        'schema_version': 1,
        'site_built_at': now.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'record_snapshot_generated_at': snapshot.get('generated_at'),
        'collection_outcome': collection,
        'feed_freshness': snapshot.get('feed_freshness', 'not-currently-verified'),
        'source_status_counts': status_counts,
        'record_counts': {key: len(snapshot.get(key, [])) if isinstance(snapshot.get(key), list) else 0
                          for key in ('polls', 'finance', 'legislation', 'debates', 'news')},
        'build_event': event,
        'source_commit': sha,
        'workflow_run_url': run_url,
        'explanation': 'Site build time does not mean all political records were newly published or successfully refreshed.'
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--collection', choices=sorted(ALLOWED), default='not-run')
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'site/data/snapshot.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'site/data/deployment.json')
    args = parser.parse_args()
    from worker.audit import audit_snapshot
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
    errors = audit_snapshot(snapshot)
    if errors:
        raise SystemExit('Snapshot audit failed: ' + '; '.join(errors[:4]))
    output = manifest(snapshot, collection=args.collection)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Created public deployment manifest: {args.output} ({args.collection})')


if __name__ == '__main__':
    main()
