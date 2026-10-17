from worker import collect
import pytest, urllib.parse, json

def test_congress_uses_verified_schema_and_no_geography():
    row={'congress':119,'number':'42','type':'HR','title':'A housing bill','url':'https://api.congress.gov/v3/bill/119/hr/42','latestAction':{'actionDate':'2026-10-01','text':'Referred to committee'}}
    result=collect.normalize_congress_bill(row,'2026-10-15T00:00:00Z')
    assert result['state'] is None and result['topic']=='Housing'
    assert result['date']=='2026-10-01' and result['source_url'].startswith('https://www.congress.gov/')
    assert collect.normalize_congress_bill({**row,'congress':118},'2026-10-15T00:00:00Z') is None
    assert collect.normalize_congress_bill({**row,'url':'http://bad.example'},'2026-10-15T00:00:00Z') is None

def test_congress_free_key_and_pagination(monkeypatch):
    urls=[]
    def fake(url,timeout=18,headers=None):
        urls.append((url,headers))
        return {'bills':[{'congress':119,'number':1,'type':'S','title':'School programs','url':'https://api.congress.gov/v3/bill/119/s/1','latestAction':{'actionDate':'2026-09-10','text':'Introduced'}}]}
    monkeypatch.setenv('CONGRESS_API_KEY','unit-test-key')
    monkeypatch.setattr(collect,'get_json',fake)
    found=collect.collect_congress(max_pages=3)
    assert len(found)==1 and len(urls)==1
    assert 'api_key' not in urllib.parse.parse_qs(urllib.parse.urlsplit(urls[0][0]).query)
    assert urls[0][1]['X-Api-Key']=='unit-test-key'

def test_missing_congress_key_preserves_original(monkeypatch,tmp_path):
    monkeypatch.delenv('CONGRESS_API_KEY',raising=False)
    before=json.loads(collect.SNAP.read_text())
    path=tmp_path/'snapshot.json';path.write_text(json.dumps(before))
    changed=collect.collect_once(snapshot_path=path,providers=['congress'])
    after=json.loads(path.read_text())
    assert len(after['polls'])==len(before['polls'])
    assert any(s['id']=='congress' and s['status']=='credentials-required' for s in after['sources'])
    assert changed['failures']
