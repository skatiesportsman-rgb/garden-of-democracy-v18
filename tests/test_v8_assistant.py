import asyncio
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from worker.local_ai import retrieve,generate
from tools.import_existing_snapshot import import_snapshot
from server import app

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'site/data/snapshot.json').read_text())
STATES=json.loads((ROOT/'data/states.json').read_text())


def test_local_api_refuses_bad_answer_length():
    r=TestClient(app).post('/api/ask',json={'question':'Tell me about the polls','level':'unlimited'})
    assert r.status_code==400


def test_local_api_no_model_does_not_falsely_claim_ai(monkeypatch):
    monkeypatch.delenv('GARDEN_ENABLE_OLLAMA',raising=False)
    r=TestClient(app).post('/api/ask',json={'question':'What do Michigan polls say?','level':'simple'})
    assert r.status_code==200
    assert r.json()['mode']=='unavailable'


def test_local_model_retrieval_state_filters():
    results=retrieve(DATA,'What do polls say in Georgia?',state='GA',cutoff='2026-10-15',states=STATES)
    assert results
    assert all(v['state']=='GA' for v in results)


def test_no_model_when_evidence_missing(monkeypatch):
    monkeypatch.setenv('GARDEN_ENABLE_OLLAMA','1')
    value=asyncio.run(generate({'polls':[]},'What are Georgia poll results?','simple','GA','2026-10-15',STATES))
    assert value['mode']=='unavailable'


def test_snapshot_migration_backups_and_preserves_data(tmp_path):
    old=tmp_path/'old.json'; dest=tmp_path/'snapshot.json'
    old.write_text(json.dumps(DATA))
    dest.write_text(json.dumps({'polls':[]}))
    counts=import_snapshot(old,dest)
    assert counts['polls']==len(DATA['polls'])
    assert dest.with_suffix('.json.backup').exists()


def test_snapshot_migration_rejects_fake_data_without_changes(tmp_path):
    invalid=json.loads(json.dumps(DATA));invalid['polls'][0]['answers'][0]['pct']=300
    old=tmp_path/'old.json'; dest=tmp_path/'snapshot.json'
    old.write_text(json.dumps(invalid));dest.write_text(json.dumps(DATA))
    try:
        import_snapshot(old,dest)
    except ValueError:
        pass
    else:
        assert False,'should reject invalid percentages'
    assert json.loads(dest.read_text())['polls'][0]['answers'][0]['pct']!=300


def test_mocked_local_ai_explains_only_server_retrieved_evidence(monkeypatch):
    import httpx
    monkeypatch.setenv('GARDEN_ENABLE_OLLAMA','1')
    monkeypatch.setenv('GARDEN_OLLAMA_MODEL','gemma3:1b')
    requested=[]
    def handler(request):
        content=json.loads(request.content)
        requested.append(content)
        assert content['model']=='gemma3:1b'
        assert 'Georgia' in content['messages'][1]['content']
        assert 'Beacon Research' in content['messages'][1]['content']
        return httpx.Response(200,json={'message':{'content':'A Georgia Senate poll reported 56% for Jon Ossoff and 43% for Mike Collins; this is not an election result.'}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await generate(DATA,'What do the polls say about Georgia?','standard','GA','2026-10-15',STATES,client=client)
    result=asyncio.run(run())
    assert result['mode']=='local-ai'
    assert result['evidence'][0]['url'].startswith('https://')
    assert len(requested)==1
