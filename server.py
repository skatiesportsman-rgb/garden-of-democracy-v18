"""Local API and website server. Production $0 option uses GitHub Pages snapshots.
Run: uvicorn server:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations
import asyncio,json,os,pathlib,sqlite3
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from worker.local_ai import generate
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
ROOT=pathlib.Path(__file__).parent
SNAP=ROOT/'site/data/snapshot.json'
DB=pathlib.Path(os.environ.get('GARDEN_SQLITE_PATH', ROOT/'data/garden.sqlite'))
app=FastAPI(title='The Garden of Democracy',version='0.1.0')

def data():return json.loads(SNAP.read_text())
def initialize():
    DB.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute('CREATE TABLE IF NOT EXISTS ingestion_log (id INTEGER PRIMARY KEY, source TEXT NOT NULL, fetched_at TEXT NOT NULL, count INTEGER NOT NULL, status TEXT NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS poll_cache (id TEXT PRIMARY KEY, source_id TEXT NOT NULL, published_at TEXT, state TEXT, payload TEXT NOT NULL)')
        for p in data().get('polls',[]):c.execute('INSERT INTO poll_cache(id,source_id,published_at,state,payload) VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,published_at=excluded.published_at,state=excluded.state',(p['id'],p.get('source_id',''),p.get('published_at'),p.get('state'),json.dumps(p)))
initialize()
@app.get('/health')
def health():return {'ok':True,'snapshot_exists':SNAP.exists(),'database_exists':DB.exists()}
@app.get('/api/snapshot')
def snapshot():return data()
@app.get('/api/polls')
def polls(state:str|None=None,topic:str|None=None,limit:int=100):
    if not 1<=limit<=300:raise HTTPException(400,'limit must be 1–300')
    pp=data().get('polls',[])
    if state and state.upper()!='US':pp=[p for p in pp if p.get('state')==state.upper()]
    if topic:pp=[p for p in pp if p.get('topic')==topic]
    return pp[:limit]
@app.get('/api/states/{code}')
def by_state(code:str):
    st=json.loads((ROOT/'data/states.json').read_text());match=next((s for s in st if s[0]==code.upper()),None)
    if not match:raise HTTPException(404,'Unknown state code')
    return {'code':match[0],'name':match[1],'polls':[p for p in data()['polls'] if p.get('state')==match[0]]}
@app.get('/api/sources')
def sources():return data().get('sources',[])
@app.get('/api/events')
async def events():
    async def generate():
        last=''
        while True:
            try:
                fresh=data();digest=fresh.get('generated_at','')
                if digest!=last:
                    yield 'event: snapshot\ndata: '+json.dumps({'generated_at':digest,'poll_count':len(fresh.get('polls',[]))})+'\n\n';last=digest
                else:yield ': keepalive\n\n'
            except Exception:yield ': snapshot temporarily unavailable\n\n'
            await asyncio.sleep(15)
    return StreamingResponse(generate(),media_type='text/event-stream',headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'})

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    level: str = 'standard'
    state: str = 'US'
    cutoff: str | None = None

@app.post('/api/ask')
async def ask(request: AskRequest):
    if request.level not in ('simple','standard','detailed'):
        raise HTTPException(400,'Invalid answer length')
    if request.state not in ('US',*[s[0] for s in json.loads((ROOT/'data/states.json').read_text())]):
        raise HTTPException(400,'Invalid state')
    if request.cutoff and (len(request.cutoff)!=10 or not request.cutoff[0:4].isdigit()):
        raise HTTPException(400,'Invalid historical date')
    return await generate(data(),request.question,request.level,request.state,request.cutoff,json.loads((ROOT/'data/states.json').read_text()))

app.mount('/',StaticFiles(directory=ROOT/'site',html=True),name='site')
