"""OpenStates adapter tests using synthetic transport responses only.
No test fixtures are published to the site's political snapshot.
"""
import copy
import datetime as dt
import json
from urllib.parse import parse_qs, urlsplit
import pytest
from worker import collect


def bill(state='GA', name='Georgia', **kwargs):
    return {
        'id':'ocd-bill/76be2aab-0000-4000-9000-000000000001',
        'identifier':'HB 99', 'session':'2025-2026',
        'jurisdiction':{'id':'ocd-jurisdiction/country:us/state:'+state.lower(),'name':name},
        'title':'A bill to address housing affordability',
        'openstates_url':'https://openstates.org/ga/bills/2025_26/HB99/',
        'updated_at':'2026-10-13T18:00:00+00:00',
        'latest_action_date':'2026-10-13',
        'latest_action_description':'Referred to committee',
        'subject':['HOUSING'],
        **kwargs,
    }


def test_reject_false_geographic_association():
    assert collect.normalize_openstates_bill(bill(),'2026-10-15T00:00:00Z','NY') is None
    output=collect.normalize_openstates_bill(bill(),'2026-10-15T00:00:00Z','GA')
    assert output['state']=='GA' and output['topic']=='Housing'
    assert output['source_id']=='openstates' and output['type']=='state_bill'
    assert output['source_url'].startswith('https://')
    assert output['published_at']=='2026-10-13'
    assert output['note'].find('does not mean enactment')!=-1


def test_reject_missing_original_source():
    x=bill();x['openstates_url']='http://untrusted.example/'
    assert collect.normalize_openstates_bill(x,'2026-10-15T00:00:00Z','GA') is None


def test_preserve_history_and_corrections():
    first=collect.normalize_openstates_bill(bill(),'2026-10-15T00:00:00Z','GA')
    other=copy.deepcopy(first);other['action']='Bill passed committee';other['retrieved_at']='2026-10-15T01:00:00Z'
    items,new,rev=collect.merge_records([first],[other])
    assert (new,rev)==(0,1) and len(items)==1 and items[0]['action']=='Bill passed committee'
    last=copy.deepcopy(other);last['retrieved_at']='2026-10-15T02:00:00Z'
    _,new,rev=collect.merge_records(items,[last])
    assert (new,rev)==(0,0)


def test_key_header_and_bounded_pages(monkeypatch):
    seen=[]
    def fake(url,timeout=18,headers=None):
        seen.append((url,headers))
        return {'results':[bill()]}
    monkeypatch.setenv('OPENSTATES_API_KEY','FAKE-KEY-NOT-REAL')
    monkeypatch.setattr(collect,'get_json',fake)
    result=collect.collect_openstates(max_pages=2,states='GA')
    assert len(result)==1 and len(seen)==1
    url,headers=seen[0]
    assert urlsplit(url).netloc=='v3.openstates.org'
    assert parse_qs(urlsplit(url).query)['jurisdiction']==['Georgia']
    assert headers['X-API-KEY']=='FAKE-KEY-NOT-REAL'
    assert 'FAKE-KEY-NOT-REAL' not in url


def test_fetch_all_jurisdictions_and_small_rotation():
    all_states=collect.openstates_jurisdictions('all')
    assert len(all_states)==51 and len(set(x[0] for x in all_states))==51
    assert ('DC','District of Columbia') in all_states
    at=dt.datetime(2026,10,15,12,tzinfo=dt.timezone.utc)
    batch=collect.openstates_jurisdictions(at=at)
    assert len(batch)==4 and batch==collect.openstates_jurisdictions(at=at)
    assert collect.openstates_jurisdictions('GA,NY')==[('GA','Georgia'),('NY','New York')]
    with pytest.raises(ValueError):collect.openstates_jurisdictions('GA,XX')


def test_no_key_retains_existing_data(monkeypatch,tmp_path):
    monkeypatch.delenv('OPENSTATES_API_KEY',raising=False)
    original=json.loads(collect.SNAP.read_text())
    p=tmp_path/'snapshot.json';p.write_text(json.dumps(original))
    diff=collect.collect_once(snapshot_path=p,providers=['openstates'],openstates_states='GA')
    saved=json.loads(p.read_text())
    assert saved['polls']==original['polls']
    assert any(e['id']=='openstates' and e['status']=='credentials-required' for e in saved['sources'])
    assert len(diff['failures'])==1


def test_single_state_import_passes_publication_audit(monkeypatch,tmp_path):
    monkeypatch.setenv('OPENSTATES_API_KEY','NOT-A-REAL-KEY')
    monkeypatch.setattr(collect,'get_json',lambda url,timeout=18,headers=None:{'results':[bill()]})
    snap=json.loads(collect.SNAP.read_text());p=tmp_path/'snapshot.json';p.write_text(json.dumps(snap))
    diff=collect.collect_once(snapshot_path=p,providers=['openstates'],openstates_states='GA')
    assert diff['new_legislation']==1 and not diff['failures']
    saved=json.loads(p.read_text())
    assert any(x['state']=='GA' and x['source_id']=='openstates' for x in saved['legislation'])
    from worker.audit import audit_snapshot
    assert audit_snapshot(saved)==[]
