"""V13: verified collection events, no duplicate harvests, and nested static Pages."""
import copy
import json
from pathlib import Path
from worker import collect
from worker.audit import audit_snapshot
from tools.deployment_doctor import inspect_static, test_nested_pages as check_pages

ROOT=Path(__file__).resolve().parents[1]


def test_garden_data_preflight():
    assert inspect_static()==[]


def test_nested_github_pages_static_routes():
    check_pages('garden-of-democracy')


def test_harvest_only_for_actual_new_and_revised_records(monkeypatch,tmp_path):
    data=json.loads(collect.SNAP.read_text())
    old=data['polls'][0]
    new={**old,'id':'unit-test-only-harvest-poll','subject':'Test-only imported measurement'}
    state={'record':new}
    monkeypatch.setattr(collect,'collect_votehub',lambda max_pages:[copy.deepcopy(state['record'])])
    path=tmp_path/'snapshot.json';path.write_text(json.dumps(data))
    first=collect.collect_once(path,providers=['votehub'])
    saved=json.loads(path.read_text())
    assert first['new_polls']==1
    events=[x for x in saved['harvest'] if x['id']==new['id']]
    assert len(events)==1 and events[0]['change']=='new'
    assert audit_snapshot(saved)==[]
    repeat=collect.collect_once(path,providers=['votehub'])
    assert repeat['new_polls']==0 and repeat['revised_polls']==0
    assert len([x for x in json.loads(path.read_text())['harvest'] if x['id']==new['id']])==1
    changed=copy.deepcopy(new);changed['answers']=[{'choice':'Test response','pct':30}]
    state['record']=changed
    third=collect.collect_once(path,providers=['votehub'])
    assert third['revised_polls']==1
    result=json.loads(path.read_text())
    events=[x for x in result['harvest'] if x['id']==new['id']]
    assert len(events)==2 and events[-1]['change']=='revised'
    assert len([p for p in result['polls'] if p['id']==new['id']])==1


def test_auditor_rejects_malformed_harvest():
    snap=json.loads(collect.SNAP.read_text())
    snap['harvest']=[{'id':'foo','kind':'impossible','source_id':'test','change':'new','collected_at':'2026-10-16'}]
    assert any('harvest' in x for x in audit_snapshot(snap))


def test_harvest_does_not_repeat_syndicated_duplicate(monkeypatch,tmp_path):
    data=json.loads(collect.SNAP.read_text())
    record={**data['polls'][0],'id':'test-duplicate-from-one-provider'}
    monkeypatch.setattr(collect,'collect_votehub',lambda max_pages:[copy.deepcopy(record),copy.deepcopy(record)])
    path=tmp_path/'snapshot.json';path.write_text(json.dumps(data))
    output=collect.collect_once(path,providers=['votehub'])
    after=json.loads(path.read_text())
    assert output['new_polls']==1
    assert len([event for event in after['harvest'] if event['id']==record['id']])==1
