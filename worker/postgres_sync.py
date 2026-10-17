"""Optional verified snapshot -> Supabase PostgreSQL mirror. Requires DATABASE_URL secret."""
import json,os,pathlib
URL=os.environ.get('DATABASE_URL')
if not URL:raise SystemExit('DATABASE_URL not present; skipping optional PostgreSQL mirror')
import psycopg
root=pathlib.Path(__file__).resolve().parents[1]
snap=json.loads((root/'site/data/snapshot.json').read_text())
with psycopg.connect(URL,connect_timeout=15,sslmode='require') as conn:
    with conn.cursor() as cur:
        cur.execute((root/'database/schema.sql').read_text())
        for s in snap['sources']:
            cur.execute('INSERT INTO civic_sources(source_id,name,status,metadata) VALUES(%s,%s,%s,%s::jsonb) ON CONFLICT(source_id) DO UPDATE SET status=excluded.status,metadata=excluded.metadata,updated_at=now()', (s['id'],s['name'],s['status'],json.dumps(s)))
        for p in snap['polls']:
            cur.execute('INSERT INTO civic_polls(poll_id,source_id,state_code,published_at,fieldwork_start,fieldwork_end,pollster,subject,payload) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT(poll_id) DO UPDATE SET payload=excluded.payload,imported_at=now()', (p['id'],p['source_id'],p.get('state'),p.get('published_at'),p.get('start_date'),p.get('end_date'),p.get('pollster'),p.get('subject'),json.dumps(p)))
        for a in snap.get('news',[]):
            cur.execute('INSERT INTO civic_news(article_id,source_id,url,payload) VALUES(%s,%s,%s,%s::jsonb) ON CONFLICT(article_id) DO UPDATE SET payload=excluded.payload,imported_at=now()', (a['id'],a['source_id'],a['url'],json.dumps(a)))
    conn.commit()
print('Synced',len(snap['polls']),'polls to PostgreSQL')
