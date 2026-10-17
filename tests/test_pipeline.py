"""Unit and integration tests: source validation, geographic non-inference, ingestion idempotence."""
import json, pathlib, sys, tempfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from worker.collect import normalize_votehub,normalize_pollresults,merge_records,collect_once,topic_of
from server import app
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]

def test_votehub_does_not_infer_geography_from_text():
    p=normalize_votehub({'id':'real-provider-id','poll_type':'senate','subject':'North Carolina race', 'seat_name':'NC Senate','pollster':'University','start_date':'2026-08-01','end_date':'2026-08-04','answers':[{'choice':'A','pct':48},{'choice':'B','pct':47}]},'2026-08-05T01:00:00Z')
    assert p['state'] is None
    assert p['answers'][0]['pct']==48
    assert p['question_exact'] is False

def test_votehub_uses_explicit_state_only():
    p=normalize_votehub({'id':'state-abc','state':'GA','end_date':'2026-09-20','answers':[{'choice':'A','pct':53}]},'2026-09-21T00:00:00Z')
    assert p['state']=='GA'

def test_invalid_measurements_are_rejected():
    x={'id':'bad','end_date':'2026-09-20','answers':[{'choice':'A','pct':110},{'choice':'B','pct':-5}]}
    assert normalize_votehub(x,'2026-09-21T00:00:00Z') is None

def test_malformed_record_no_phantom_votes():
    p=normalize_votehub({'id':'incomplete','end_date':'2026-09-20','answers':[{'choice':'A','pct':48}]},'2026-09-21T00:00:00Z')
    assert len(p['answers'])==1 and sum(x['pct'] for x in p['answers'])==48

def test_duplicate_revisions_update_not_double_count():
    old={'id':'abc','answers':[{'choice':'A','pct':41}],'source_url':'https://example.com'}
    new={**old,'answers':[{'choice':'A','pct':43}]}
    result,n,changed=merge_records([old],[new,new])
    assert len(result)==1 and n==0 and changed==1

def test_pollresults_unknown_response_stays_unverified():
    assert normalize_pollresults({'id':'z','end_date':'2026-10-01','pollster':'X'},'senate','2026-10-01T00:00:00Z') is None

def test_offline_refresh_preserves_verifiable_seed():
    raw=json.loads((ROOT/'site/data/snapshot.json').read_text())
    with tempfile.TemporaryDirectory() as t:
        dst=pathlib.Path(t)/'snapshot.json';dst.write_text(json.dumps(raw))
        changed=collect_once(snapshot_path=dst,offline=True)
        after=json.loads(dst.read_text())
        assert changed['new_polls']==0
        assert len(after['polls'])==len(raw['polls'])

def test_all_states_and_dc_present_and_no_missing_ghost_polls():
    states=json.loads((ROOT/'site/data/states.json').read_text())
    assert len(states)==51
    assert len({s[0] for s in states})==51
    assert any(s[0]=='DC' for s in states)
    snap=json.loads((ROOT/'site/data/snapshot.json').read_text())
    assert len(snap['polls'])>=10
    assert all(p['source_url'].startswith('https://') for p in snap['polls'])
    assert all(p['verification'] in ('published_report','structured-feed') for p in snap['polls'])

def test_http_api():
    with TestClient(app) as api:
        assert api.get('/health').status_code==200
        assert len(api.get('/api/polls').json())>=10
        assert api.get('/api/states/GA').json()['polls'][0]['state']=='GA'
        assert api.get('/api/states/ZZ').status_code==404
        assert api.get('/api/polls?limit=50000').status_code==400
        assert api.get('/').status_code==200

# Version 4: federal candidate totals are aggregate disclosures, never donor profiles.
def test_fec_candidate_totals_normalization():
    from worker.collect import normalize_fec_candidate_totals
    record=normalize_fec_candidate_totals({'candidate_id':'H0GA01234','name':'Example candidate','state':'GA','cycle':2026,'receipts':120000.5,'disbursements':95000.2},'2026-10-15T14:00:00Z')
    assert record['state']=='GA' and record['type']=='candidate_cycle_aggregate'
    assert record['amount']==120000.5 and record['disbursements']==95000.2
    assert 'individual' not in record
    assert normalize_fec_candidate_totals({'candidate_id':'Z','cycle':2024,'receipts':100},'2026-10-15T14:00:00Z') is None
    assert normalize_fec_candidate_totals({'candidate_id':'Z','cycle':2026,'receipts':-100},'2026-10-15T14:00:00Z') is None

def test_fec_adapter_bounds_pages_and_uses_env_key(monkeypatch):
    from worker import collect
    import urllib.parse
    urls=[]
    def fake_request(url,timeout=18,headers=None):
        urls.append((url,headers))
        return {'results':[{'candidate_id':'S6GA00001','state':'GA','cycle':2026,'receipts':500,'name':'Test'}]}
    monkeypatch.setenv('FEC_API_KEY','fake-test-only')
    monkeypatch.setattr(collect,'get_json',fake_request)
    found=collect.collect_fec(max_pages=3)
    assert len(found)==1 and len(urls)==1
    parsed=urllib.parse.parse_qs(urllib.parse.urlsplit(urls[0][0]).query)
    assert parsed['cycle']==['2026'] and 'api_key' not in parsed
    assert urls[0][1]['X-Api-Key']=='fake-test-only'

def test_missing_fec_key_does_not_poison_snapshot(tmp_path,monkeypatch):
    from worker import collect
    monkeypatch.delenv('FEC_API_KEY',raising=False)
    original=json.loads((ROOT/'site/data/snapshot.json').read_text())
    path=tmp_path/'snap.json';path.write_text(json.dumps(original))
    delta=collect.collect_once(snapshot_path=path,providers=['fec'])
    after=json.loads(path.read_text())
    assert delta['failures'] and len(after['polls'])==len(original['polls'])
    assert any(s['id']=='fec' and s['status']=='credentials-required' for s in after['sources'])
