import copy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'worker'))
from audit import audit_snapshot
from collect import collect_once

ROOT=Path(__file__).resolve().parents[1]

def fixture():return json.loads((ROOT/'site/data/snapshot.json').read_text())

def test_bundled_snapshot_audits():
    assert audit_snapshot(fixture()) == []

def test_rejects_unsupported_state():
    s=fixture();s['polls'][0]['state']='QQ'
    assert any('invalid state' in e for e in audit_snapshot(s))

def test_rejects_fabricated_bad_poll_percent():
    s=fixture();s['polls'][0]['answers'][0]['pct']=130
    assert any('invalid response share' in e for e in audit_snapshot(s))

def test_rejects_duplicate_polls():
    s=fixture();s['polls'].append(copy.deepcopy(s['polls'][0]))
    assert any('duplicate id' in e for e in audit_snapshot(s))

def test_rejects_non_secure_evidence():
    s=fixture();s['polls'][0]['source_url']='javascript:alert(1)'
    assert any('secure evidence link' in e for e in audit_snapshot(s))

def test_offline_does_not_claim_fresh_automated_poll_feed(tmp_path):
    s=fixture();s['sources']=[{'id':'pollresults','status':'operational','last_success':'2025-01-01T00:00:00Z'}]
    p=tmp_path/'snapshot.json';p.write_text(json.dumps(s))
    collect_once(snapshot_path=p,providers=('pollresults',),offline=True)
    assert json.loads(p.read_text())['live_collection_verified'] is False
