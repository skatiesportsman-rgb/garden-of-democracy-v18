#!/usr/bin/env python3
"""Offline GitHub Pages preflight: inspect artifacts and exercise nested-route serving.

A pass proves only that the static site can be served under a project URL, not
that GitHub permissions, Pages deployment, API credentials, or collectors work.
"""
from __future__ import annotations
import http.server
import json
from pathlib import Path
import shutil
import tempfile
import sys
import threading
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
sys.path.insert(0, str(ROOT))
ASSETS = ['index.html', 'app.js', 'garden-answer.js', 'style.css',
          'data/states.json', 'data/snapshot.json', 'data/deployment.json', 'assets/cottage-meadow.svg']


def inspect_static():
    from worker.audit import audit_snapshot
    errors = []
    for name in ASSETS:
        if not (SITE / name).is_file():
            errors.append('Missing public asset: ' + name)
    if errors:
        return errors
    try:
        snapshot = json.loads((SITE / 'data/snapshot.json').read_text())
        errors.extend(audit_snapshot(snapshot))
        launch = json.loads((SITE / 'data/deployment.json').read_text())
        if launch.get('schema_version') != 1 or launch.get('collection_outcome') not in ('success','partial','failed','not-run'):
            errors.append('Invalid public deployment manifest')
        for key in ('polls','finance','legislation','debates','news'):
            if launch.get('record_counts',{}).get(key) != len(snapshot.get(key, [])):
                errors.append(f'Deployment manifest {key} count differs from snapshot')
        states = json.loads((SITE / 'data/states.json').read_text())
        codes = [entry[0] for entry in states]
        if len(codes) != 51 or len(set(codes)) != 51 or 'DC' not in codes:
            errors.append('Expected 50 states + D.C. in state roster')
    except (OSError, ValueError, KeyError, IndexError) as exc:
        errors.append('Invalid public data file: ' + str(exc))
    html = (SITE / 'index.html').read_text()
    if 'href="./style.css"' not in html or 'src="./app.js"' not in html:
        errors.append('Frontend asset links must be relative for GitHub project Pages')
    if any((SITE / name).exists() for name in ('.env', 'secrets.json', '.git', '.venv')):
        errors.append('Potential credential or build directory inside public site/')
    workflow = (ROOT / '.github/workflows/deploy.yml')
    if not workflow.is_file():
        errors.append('Pages deployment workflow is missing')
    else:
        text = workflow.read_text()
        if 'actions/deploy-pages@' not in text or 'actions/upload-pages-artifact@' not in text:
            errors.append('Pages deployment/upload actions are missing')
    return errors


def test_nested_pages(slug='garden-of-democracy'):
    """Serve as /garden-of-democracy/, as project Pages would, then GET assets."""
    slug = slug.strip('/')
    if not slug or '/' in slug or slug in ('.', '..'):
        raise ValueError('slug must be one URL path segment')
    with tempfile.TemporaryDirectory(prefix='garden-preflight-') as temp:
        host_dir = Path(temp)
        shutil.copytree(SITE, host_dir / slug)
        # Disable access logs and listen on loopback only.
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=temp, **kwargs)
            def log_message(self, *args):
                pass
        with http.server.ThreadingHTTPServer(('127.0.0.1', 0), Quiet) as srv:
            worker = threading.Thread(target=srv.serve_forever, daemon=True)
            worker.start()
            try:
                base = f'http://127.0.0.1:{srv.server_port}/{slug}/'
                for name in ASSETS:
                    with urlopen(base + name, timeout=5) as response:
                        if response.status != 200 or not response.read():
                            raise ValueError('Failed to serve nested asset: ' + name)
                with urlopen(base, timeout=5) as response:
                    if response.status != 200 or b'Garden of Democracy' not in response.read():
                        raise ValueError('Project Pages index not accessible')
            finally:
                srv.shutdown()
                worker.join(timeout=5)


def main():
    errors = inspect_static()
    if errors:
        for error in errors:
            print('FAIL:', error)
        return 1
    try:
        test_nested_pages()
    except Exception as exc:
        print('FAIL: Nested GitHub Pages-style smoke test:', exc)
        return 1
    print('PASS: Snapshot audit, 51 jurisdictions, relative frontend paths,')
    print('      protected public site directory, and nested Pages HTTP assets.')
    print('NOT VERIFIED: Hosted GitHub workflow, external API connectivity, or public URL.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
