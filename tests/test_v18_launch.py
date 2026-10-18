"""Launch manifest/public site regression tests (offline, no provider keys)."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location('garden_manifest', ROOT/'tools/build_deployment_manifest.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_manifest_does_not_expose_any_environment_secrets():
    payload = {'generated_at': '2026-10-15T13:00:00Z', 'feed_freshness': 'not-currently-verified',
               'polls': [{'id': 'a'}], 'finance': [], 'legislation': [], 'news': [], 'debates': [],
               'sources': [{'status': 'temporarily-unavailable'}, {'status': 'operational'}]}
    env = {'GITHUB_REPOSITORY': 'researcher/garden-of-democracy', 'GITHUB_RUN_ID': '123',
           'GITHUB_SHA': 'a'*40, 'GITHUB_EVENT_NAME': 'schedule',
           'FEC_API_KEY': 'secretFECKey7777', 'OPENSTATES_API_KEY': 'secretOpenStates8888',
           'CONGRESS_API_KEY': 'secretCongress9999'}
    x = mod.manifest(payload, now=datetime(2026, 10, 17, tzinfo=timezone.utc), collection='partial', environ=env)
    raw = json.dumps(x)
    assert 'secret' not in raw
    assert x['record_counts']['polls'] == 1
    assert x['source_status_counts']['operational'] == 1
    assert x['collection_outcome'] == 'partial'
    assert x['workflow_run_url'] == 'https://github.com/researcher/garden-of-democracy/actions/runs/123'
    assert x['site_built_at'] == '2026-10-17T00:00:00Z'


def test_untrusted_github_metadata_is_rejected():
    x = mod.manifest({}, collection='not-run', environ={
        'GITHUB_REPOSITORY': 'x/y\" onclick=alert(1)',
        'GITHUB_RUN_ID': '1/../../../2',
        'GITHUB_EVENT_NAME': 'evil', 'GITHUB_SHA': 'not valid'})
    assert x['source_commit'] is None
    assert x['workflow_run_url'] is None
    assert x['build_event'] == 'local'


def test_public_manifest_matches_bundled_snapshot():
    snap = json.loads((ROOT/'site/data/snapshot.json').read_text())
    public = json.loads((ROOT/'site/data/deployment.json').read_text())
    for typ in ('polls','finance','legislation','debates','news'):
        assert public['record_counts'][typ] == len(snap.get(typ,[]))
    assert public['collection_outcome'] == 'not-run'
    assert public['record_snapshot_generated_at'] == snap['generated_at']


def test_workflow_keeps_pages_upload_and_source_checks_separate():
    workflow = (ROOT/'.github/workflows/deploy.yml').read_text()
    assert 'actions/deploy-pages@v4' in workflow
    assert 'actions/upload-pages-artifact@v4' in workflow
    assert 'continue-on-error: true' in workflow
    assert 'build_deployment_manifest.py' in workflow
    assert 'workflow_dispatch:' in workflow
    assert 'schedule:' in workflow
    assert 'git add site/data/deployment.json' not in workflow
    assert 'python worker/audit.py' in workflow
    assert 'path: site' in workflow
    assert re.search(r'cron:\s*\'23 \*/2', workflow)


def test_launch_does_not_change_preferred_original_map_or_story():
    js = (ROOT/'site/app.js').read_text()
    assert 'mapPollSelection()' in js
    assert 'statePoint(' in js
    assert 'flower-stem-sway' in js
    assert 'stateClipLayer(' not in js
    assert 'The Stories We Grow' in js
