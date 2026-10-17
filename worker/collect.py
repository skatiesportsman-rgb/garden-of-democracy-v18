"""Authorized, incremental civic-data ingestion. Runs once; schedule externally.

Public sources only; no login scraping or inferred political profiles.
If unreachable, preserves prior verified data and records the failure.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, logging, os, pathlib, sqlite3, tempfile, time, urllib.error, urllib.parse, urllib.request
from typing import Any
try:
    from .audit import audit_snapshot
except ImportError:
    from audit import audit_snapshot

ROOT=pathlib.Path(__file__).resolve().parents[1]
SNAP=ROOT/'site/data/snapshot.json'
UA='GardenOfDemocracy/0.1 (student research; evidence links retained)'
LOG=logging.getLogger('garden.collect')
POLLRESULT_TYPES=('senate','house','governor','approval','other')
ISSUE_KEYWORDS={'Affordability':('inflation','affordab','cost of living','economy','wage','housing prices'), 'Healthcare':('healthcare','medicare','medicaid','health care'),'Housing':('housing','rent','mortgage'),'Immigration':('immigration','border'),'Education':('education','school','student'),'Elections':('voting','election security','ballot measure'),'Leadership':('approval','favorability','president','congress')}

def iso_now(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def unique_id(prefix,raw): return prefix+'-'+hashlib.sha256(str(raw).encode('utf8')).hexdigest()[:22]
def topic_of(text):
    x=(text or '').lower()
    return next((topic for topic, words in ISSUE_KEYWORDS.items() if any(w in x for w in words)),'Representation')
def checked_date(s):
    if not s: return None
    x=str(s)[:10]
    try:return dt.date.fromisoformat(x).isoformat()
    except ValueError:return None

def get_json(url, timeout=18, headers=None):
    request_headers={'User-Agent':UA,'Accept':'application/json'}
    request_headers.update(headers or {})
    req=urllib.request.Request(url,headers=request_headers)
    with urllib.request.urlopen(req,timeout=timeout) as response:
        if response.status!=200:raise ValueError(f'HTTP {response.status}')
        raw=response.read(8_000_000+1)
        if len(raw)>8_000_000:raise ValueError('oversized response')
        return json.loads(raw.decode('utf8'))

def pct_answers(xs):
    out=[]
    for v in xs if isinstance(xs,list) else []:
        if not isinstance(v,dict):continue
        name=v.get('choice') or v.get('answer') or v.get('name') or v.get('label')
        pct=v.get('pct',v.get('percentage',v.get('value')))
        try:n=float(pct)
        except (TypeError,ValueError):continue
        if name is not None and 0<=n<=100:out.append({'choice':str(name)[:120], 'pct':int(n) if n.is_integer() else round(n,2)})
    return out[:15]

def state_of(item):
    """Use only explicit state abbreviations/identifiers, never text inference."""
    valid={s[0] for s in json.loads((ROOT/'data/states.json').read_text())}
    valid.add('DC')
    for key in ('state','state_code','state_abbr','postal_code'):
        x=item.get(key)
        if isinstance(x,str) and x.upper() in valid:return x.upper()
    return None

def normalize_votehub(item, retrieved):
    if not isinstance(item,dict):return None
    answers=pct_answers(item.get('answers',[]))
    if not answers:return None
    pollster=str(item.get('pollster') or 'Unspecified pollster')
    date=checked_date(item.get('end_date') or item.get('created_at'))
    if not date:return None
    raw_id=item.get('id') or json.dumps([pollster,date,answers],sort_keys=True)
    subject=str(item.get('subject') or item.get('seat_name') or 'Published political poll')
    url=item.get('url');url=str(url) if isinstance(url,str) and url.startswith('https://') else 'https://votehub.com/polls/api/'
    pop={'rv':'Registered voters','lv':'Likely voters','a':'Adults'}.get(item.get('population'),item.get('population') or 'Unreported')
    try:sample=int(item.get('sample_size'))
    except(TypeError,ValueError):sample=None
    return {'id':'votehub-'+str(raw_id)[:90],'source_id':'votehub','source_name':'VoteHub','pollster':pollster,'sponsor':', '.join(map(str,item.get('sponsors') or [])),'type':str(item.get('poll_type') or 'poll'),'subject':subject,'topic':topic_of(subject+' '+str(item.get('poll_type'))),'state':state_of(item),'question':f'Published survey concerning {subject}. Exact wording available from the originating poll, if published.','question_exact':False,'answers':answers,'population':pop,'sample_size':sample,'start_date':checked_date(item.get('start_date')),'end_date':date,'published_at':checked_date(item.get('created_at')) or date,'retrieved_at':retrieved,'moe':None,'method':None,'source_url':url,'verification':'structured-feed','completeness_note':'Preserved published response options. Review original poll for exact question wording and missing methodological details.'}

def normalize_pollresults(item, poll_type,retrieved):
    """Conservative schema-adaptive decoder: unsupported payloads are rejected."""
    if not isinstance(item,dict):return None
    answer_keys=('answers','results','responses','options')
    answers=[]
    for k in answer_keys:
        if isinstance(item.get(k),list):answers=pct_answers(item[k]);break
    if not answers:return None
    date=checked_date(item.get('end_date') or item.get('field_end') or item.get('date') or item.get('published_at'))
    if not date:return None
    source=item.get('url') or item.get('source_url') or 'https://pollresults.org/'
    if not isinstance(source,str) or not source.startswith('https://'):source='https://pollresults.org/'
    subject=str(item.get('subject') or item.get('race') or item.get('poll_title') or poll_type)
    published=checked_date(item.get('published_at') or item.get('published_date') or item.get('date')) or date
    raw_id=item.get('id') or item.get('poll_id') or json.dumps([date,source,answers],sort_keys=True)
    sample=item.get('sample_size') or item.get('sample');
    try:sample=int(sample)
    except (TypeError,ValueError):sample=None
    return {'id':'pollresults-'+str(raw_id)[:90],'source_id':'pollresults','source_name':'PollResults.org','pollster':str(item.get('pollster') or 'Unreported'),'sponsor':str(item.get('sponsor') or ''),'type':poll_type,'subject':subject,'topic':topic_of(subject+' '+poll_type),'state':state_of(item),'question':str(item.get('question') or f'Published {poll_type} survey: {subject}'),'question_exact':bool(item.get('question')),'answers':answers,'population':str(item.get('population') or 'Unreported'),'sample_size':sample,'start_date':checked_date(item.get('start_date') or item.get('field_start')),'end_date':date,'published_at':published,'retrieved_at':retrieved,'moe':item.get('moe'),'method':item.get('method'),'source_url':source,'verification':'structured-feed','completeness_note':'Check original record and methodology; not all optional fields were published.'}

def collect_votehub(max_pages=1):
    # Beta API may change; stop at a bounded single request rather than assuming pagination.
    url='https://api.votehub.com/polls?'+urllib.parse.urlencode({'from_date':'2026-01-01'})
    payload=get_json(url)
    arr=payload.get('polls') if isinstance(payload,dict) else payload
    if not isinstance(arr,list):raise ValueError('VoteHub schema did not include polls list')
    collected=[p for item in arr if (p:=normalize_votehub(item,iso_now()))]
    return collected

def collect_pollresults(max_pages=2):
    results=[]
    for typ in POLLRESULT_TYPES:
        cursor=None
        for page in range(max_pages):
            q={'limit':'100'}
            if cursor:q['cursor']=cursor
            data=get_json('https://api.pollresults.org/v1.0/politics/results/'+typ+'?'+urllib.parse.urlencode(q))
            if isinstance(data,list):arr=data;cursor=None
            elif isinstance(data,dict):
                arr=next((data[k] for k in ('results','data','polls','items') if isinstance(data.get(k),list)),None)
                cursor=data.get('next_cursor') or data.get('cursor') or data.get('next')
            else:arr=None
            if arr is None:raise ValueError(f'Unrecognized PollResults schema ({typ})')
            results.extend(p for item in arr if (p:=normalize_pollresults(item,typ,iso_now())))
            if not cursor:break
    return results

def collect_gdelt():
    params={'query':'("midterm election" OR "2026 Senate race" OR "2026 House race") sourcelang:english','mode':'artlist','format':'json','timespan':'1d','maxrecords':'75'}
    raw=get_json('https://api.gdeltproject.org/api/v2/doc/doc?'+urllib.parse.urlencode(params))
    arr=raw.get('articles',[]) if isinstance(raw,dict) else []
    news=[]
    for a in arr:
        url=a.get('url','') if isinstance(a,dict) else ''
        if not url.startswith('https://'):continue
        title=str(a.get('title') or '')[:230]
        if not title:continue
        pub=a.get('seendate') or ''
        news.append({'id':unique_id('gdelt',url),'type':'news','title':title,'source_id':'gdelt','url':url,'domain':a.get('domain'),'published_at':str(pub),'retrieved_at':iso_now(),'state':None,'topic':topic_of(title),'note':'Article metadata only. Coverage volume does not measure public opinion.'})
    return news

def normalize_fec_candidate_totals(item, retrieved):
    """Candidate cycle-to-date aggregate, not an individual contribution or a new payment."""
    if not isinstance(item,dict):return None
    candidate_id=item.get('candidate_id')
    if not candidate_id:return None
    state=state_of(item)
    cycle=item.get('cycle') or 2026
    if str(cycle)!='2026':return None
    try:receipts=float(item.get('receipts'))
    except (TypeError,ValueError):return None
    if not (0<=receipts<1e12):return None
    try:disbursements=float(item.get('disbursements'))
    except (TypeError,ValueError):disbursements=None
    name=str(item.get('name') or item.get('candidate_name') or candidate_id)[:140]
    return {'id':'fec-candidate-'+str(candidate_id)+'-2026','source_id':'fec','candidate':name,'candidate_id':str(candidate_id),
            'state':state,'type':'candidate_cycle_aggregate','cycle':2026,'amount':round(receipts,2),
            'receipts':round(receipts,2),'disbursements':round(disbursements,2) if disbursements is not None else None,
            'published_at':retrieved[:10],'retrieved_at':retrieved,'as_of':retrieved,
            'source_url':'https://www.fec.gov/data/candidate/'+urllib.parse.quote(str(candidate_id),safe='')+'/?cycle=2026',
            'note':'Candidate summary of reported 2026-cycle receipts and disbursements; not new transactions or real-time transfers.'}

def collect_fec(max_pages=2):
    """Federal candidate receipts, paged and bounded. Requires a free FEC key."""
    key=os.environ.get('FEC_API_KEY','').strip()
    if not key:raise ValueError('Free FEC_API_KEY is not configured; apply at api.open.fec.gov/developers/')
    out=[]
    for page in range(1,max_pages+1):
        params={'cycle':2026,'per_page':100,'page':page,'sort':'-receipts'}
        raw=get_json('https://api.open.fec.gov/v1/candidates/totals/?'+urllib.parse.urlencode(params),headers={'X-Api-Key':key})
        arr=raw.get('results') if isinstance(raw,dict) else None
        if not isinstance(arr,list):raise ValueError('Unexpected FEC response schema')
        out.extend(r for item in arr if (r:=normalize_fec_candidate_totals(item,iso_now())))
        if len(arr)<100:break
    return out

def normalize_congress_bill(item, retrieved):
    """National federal legislative action only; no inferred state or party support."""
    if not isinstance(item,dict):return None
    congress=item.get('congress'); number=item.get('number'); typ=item.get('type')
    if str(congress)!='119' or not number or not typ:return None
    action=item.get('latestAction') or {}
    if not isinstance(action,dict):action={}
    date=checked_date(action.get('actionDate') or item.get('updateDate'))
    if not date:return None
    url=item.get('url') or ''
    if not isinstance(url,str) or not url.startswith('https://api.congress.gov/'):return None
    title=str(item.get('title') or 'Untitled federal bill')[:400]
    bill_url='https://www.congress.gov/bill/119th-congress/'+({'HR':'house-bill','S':'senate-bill','HJRES':'house-joint-resolution','SJRES':'senate-joint-resolution'}.get(str(typ).upper(),'house-bill'))+'/'+str(number)
    return {'id':unique_id('congress',f'{congress}-{typ}-{number}'),'source_id':'congress','title':title,
            'type':'federal_bill','bill_type':str(typ),'number':str(number),'congress':119,
            'state':None,'topic':topic_of(title),'date':date,'published_at':date,'retrieved_at':retrieved,
            'action':str(action.get('text') or 'Latest action detail unavailable')[:600],
            'source_url':bill_url,'note':'Latest recorded congressional action. Not a measurement of public opinion or proof of enactment.'}

def collect_congress(max_pages=2):
    key=os.environ.get('CONGRESS_API_KEY','').strip()
    if not key:raise ValueError('Free CONGRESS_API_KEY is not configured; request it at api.congress.gov/sign-up')
    records=[]
    for page in range(max_pages):
        params={'format':'json','limit':100,'offset':page*100}
        response=get_json('https://api.congress.gov/v3/bill/119?'+urllib.parse.urlencode(params),headers={'X-Api-Key':key})
        rows=response.get('bills') if isinstance(response,dict) else None
        if not isinstance(rows,list):raise ValueError('Unexpected Congress.gov bill response schema')
        records.extend(record for item in rows if (record:=normalize_congress_bill(item,iso_now())))
        if len(rows)<100:break
    return records


def openstates_jurisdictions(states=None, at=None):
    """Rotate small batches of 51 state/DC jurisdictions to conserve the free key.

    Explicit --openstates-states GA,NY or --openstates-states all bypasses rotation.
    Exactly 51 state/DC entries, no Puerto Rico or municipal jurisdictions.
    """
    jurisdictions=json.loads((ROOT/'data/states.json').read_text())
    choices={code: ('District of Columbia' if code=='DC' else name) for code,name,*_ in jurisdictions}
    if states and states.lower()=='all':return list(choices.items())
    if states:
        keys=[x.strip().upper() for x in states.split(',') if x.strip()]
        if not keys or len(keys)!=len(set(keys)) or any(x not in choices for x in keys):
            raise ValueError('State selection must be distinct two-letter state/DC codes, or all')
        return [(x,choices[x]) for x in keys]
    current=at or dt.datetime.now(dt.timezone.utc)
    # A consistent UTC window aligns with the project's 2-hour GitHub Actions job.
    window=(current.date().toordinal()*12 + current.hour//2)
    start=(window*4)%len(jurisdictions)
    return [(jurisdictions[(start+n)%len(jurisdictions)][0],choices[jurisdictions[(start+n)%len(jurisdictions)][0]]) for n in range(4)]


def normalize_openstates_bill(item, retrieved, requested_state):
    """No state assignment without matching authoritative API jurisdiction."""
    if not isinstance(item,dict):return None
    jid=item.get('jurisdiction')
    if not isinstance(jid,dict):return None
    state_id=jid.get('id') or ''
    name=jid.get('name') or ''
    states={code:('District of Columbia' if code=='DC' else label) for code,label,*_ in json.loads((ROOT/'data/states.json').read_text())}
    expected=states.get(requested_state)
    matches=(isinstance(state_id,str) and state_id.lower().endswith('/state:'+requested_state.lower())) or name==expected
    if requested_state=='DC':
        matches=matches or (isinstance(state_id,str) and state_id.lower().endswith('/district:dc'))
    if not matches:return None
    bill_id=item.get('id')
    identifier=item.get('identifier')
    session=item.get('session')
    title=item.get('title')
    if not all(isinstance(v,str) and v.strip() for v in (bill_id,identifier,session,title)):return None
    if not bill_id.startswith('ocd-bill/'):return None
    published=checked_date(item.get('latest_action_date') or item.get('first_action_date') or item.get('updated_at'))
    if not published:return None
    evidence=item.get('openstates_url')
    if not (isinstance(evidence,str) and evidence.startswith('https://')):
        # Prefer an original agency link rather than making up a public bill URL.
        for source in item.get('sources') or []:
            if isinstance(source,dict) and isinstance(source.get('url'),str) and source['url'].startswith('https://'):
                evidence=source['url'];break
    if not (isinstance(evidence,str) and evidence.startswith('https://')):return None
    subjects=item.get('subject') if isinstance(item.get('subject'),list) else []
    subject_list=[str(x)[:120] for x in subjects if isinstance(x,str)][:12]
    action=str(item.get('latest_action_description') or 'Latest action not reported')[:700]
    title=title[:450]
    return {'id':unique_id('openstates',bill_id),'source_id':'openstates',
        'type':'state_bill','state':requested_state,'jurisdiction':expected,
        'external_id':bill_id,'identifier':identifier[:90],'session':session[:120],
        'title':title,'topic':(topic_of(' '.join(subject_list)) if topic_of(' '.join(subject_list))!='Representation' else topic_of(title)),
        'subjects':subject_list,'classification':item.get('classification') if isinstance(item.get('classification'),list) else [],
        'action':action,'date':published,'published_at':published,
        'updated_at':checked_date(item.get('updated_at')),
        'retrieved_at':retrieved,'source_url':evidence,
        'note':'State bill or resolution with a documented legislative action; introduction or action does not mean enactment or public support.'}


def collect_openstates(max_pages=1, states=None):
    """Authenticated, bounded 2026 state legislative updates from Plural Open.

    The API key is sent only in the X-API-KEY header, never the URL.
    The default 4-state rotation respects low-cost project request budgets.
    """
    key=os.environ.get('OPENSTATES_API_KEY','').strip()
    if not key:
        raise ValueError('OPENSTATES_API_KEY is missing; request a free key at open.pluralpolicy.com')
    records=[]
    # Limit calls to at most two 20-record pages per state and stop when exhausted.
    for state,jurisdiction in openstates_jurisdictions(states):
        for page in range(1,min(2,max_pages)+1):
            query={'jurisdiction':jurisdiction,'sort':'updated_desc','per_page':20,'page':page}
            url='https://v3.openstates.org/bills?'+urllib.parse.urlencode(query)
            response=get_json(url,timeout=35,headers={'X-API-KEY':key})
            rows=response.get('results') if isinstance(response,dict) else None
            if not isinstance(rows,list):raise ValueError('Unrecognized OpenStates bill list schema for '+state)
            received=iso_now()
            records.extend(v for item in rows if (v:=normalize_openstates_bill(item,received,state)))
            if len(rows)<20:break
    return records

def update_source(sources,id,status,error=None,at=None):
    s=next((x for x in sources if x.get('id')==id),None)
    if s is None:s={'id':id,'name':id,'url':''};sources.append(s)
    s['status']=status;s['last_attempt']=at or iso_now();s['last_error']=str(error)[:260] if error else None
    if status=='operational':s['last_success']=at or iso_now()

def merge_records(existing,incoming):
    """Upsert by source ID; revisions replace prior records, never double-count."""
    by_id={item['id']:item for item in existing if isinstance(item,dict) and item.get('id')}
    new=0;revised=0
    for item in incoming:
        key=item['id'];old=by_id.get(key)
        if old is None:new+=1
        elif any(old.get(k)!=item.get(k) for k in ('answers','start_date','end_date','state','question','source_url','receipts','disbursements','amount','action','date','title','published_at','updated_at')):revised+=1
        by_id[key]={**old,**item} if old else item
    return sorted(by_id.values(),key=lambda x:(x.get('published_at') or ''),reverse=True),new,revised

def collect_once(snapshot_path=SNAP,providers=('votehub','pollresults','gdelt'),max_pages=2, offline=False, openstates_states=None):
    snap=json.loads(pathlib.Path(snapshot_path).read_text());snap.setdefault('sources',[])
    changes={'new_polls':0,'revised_polls':0,'new_news':0,'new_finance':0,'revised_finance':0,'new_legislation':0,'revised_legislation':0,'failures':[]}
    # Source-linked activity history is distinct from publication date and is never
    # synthesized from decorative animations. Store identifiers, not personal profiles.
    harvest=list(snap.get('harvest',[])) if isinstance(snap.get('harvest',[]),list) else []
    for name,fetch in [('votehub',lambda:collect_votehub(max_pages)),('pollresults',lambda:collect_pollresults(max_pages)),('gdelt',collect_gdelt),('fec',lambda:collect_fec(max_pages)),('congress',lambda:collect_congress(max_pages)),('openstates',lambda:collect_openstates(max_pages,openstates_states))]:
        if name not in providers:continue
        if offline:
            LOG.info('offline: preserving %s source status and records',name);continue
        try:
            found=fetch();kind='news' if name=='gdelt' else 'finance' if name=='fec' else 'legislation' if name in ('congress','openstates') else 'polls'
            before={item['id']:item for item in snap.get(kind,[]) if isinstance(item,dict) and item.get('id')}
            snap[kind],new,revised=merge_records(snap.get(kind,[]),found)
            # Record only confirmed inserts or substantive revisions; a repeated
            # API check produces no extra "new bloom" events.
            # De-duplicate repeated records within one provider response before
            # emitting events; merge_records already enforces the same data rule.
            for record in {item['id']:item for item in found}.values():
                old=before.get(record['id'])
                if old is None:action='new'
                elif any(old.get(k)!=record.get(k) for k in ('answers','start_date','end_date','state','question','source_url','receipts','disbursements','amount','action','date','title','published_at','updated_at')):action='revised'
                else:continue
                harvest.append({'id':record['id'],'kind':kind,'source_id':name,'change':action,'collected_at':iso_now()})
            changes['new_'+kind]+=new
            if kind=='polls':changes['revised_polls']+=revised
            if kind=='finance':changes['revised_finance']+=revised
            if kind=='legislation':changes['revised_legislation']+=revised
            update_source(snap['sources'],name,'operational');LOG.info('%s: fetched %d, new %d, revised %d',name,len(found),new,revised)
        except Exception as exc:
            changes['failures'].append(f'{name}: {type(exc).__name__}: {str(exc)[:120]}');update_source(snap['sources'],name,'credentials-required' if name in ('fec','congress','openstates') and not os.environ.get({'fec':'FEC_API_KEY','congress':'CONGRESS_API_KEY','openstates':'OPENSTATES_API_KEY'}[name]) else 'temporarily-unavailable',error=exc);LOG.warning('%s: %s',name,exc)
    # A previous successful run is not evidence of a currently fresh live feed.
    now=dt.datetime.now(dt.timezone.utc)
    def recent_success(source, hours=36):
        if source.get('status')!='operational' or not source.get('last_success'):return False
        try:
            stamp=dt.datetime.fromisoformat(source['last_success'].replace('Z','+00:00'))
            return dt.timedelta(0)<=now-stamp<=dt.timedelta(hours=hours)
        except (ValueError,TypeError):return False
    # Keep the last 250 unique record changes; preserve real ingestion timestamps
    # even when this run does not add any records.
    snap['harvest']=harvest[-250:]
    snap['generated_at']=iso_now()
    snap['live_collection_verified']=any(recent_success(s) for s in snap['sources'] if s['id'] in ('votehub','pollresults'))
    snap['feed_freshness']='recent-success' if snap['live_collection_verified'] else 'not-currently-verified'
    snap['data_note']='Every record is published, date-labeled and source-linked. Public API integrations are enabled only after a successful runtime ingestion; gaps are not imputed.'
    # Atomic publication: reject bad records and leave the existing verified snapshot intact.
    problems=audit_snapshot(snap)
    if problems:
        raise ValueError('Snapshot quality gate rejected update: '+'; '.join(problems[:6]))
    out=pathlib.Path(snapshot_path);out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',dir=out.parent,delete=False,encoding='utf8') as f:
        json.dump(snap,f,ensure_ascii=False,indent=2);tmp=f.name
    os.replace(tmp,out)
    # Local durable cache; read-only static deployment can use the exported JSON snapshot.
    db=ROOT/'data/garden.sqlite'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS poll_cache (id TEXT PRIMARY KEY, source_id TEXT NOT NULL, published_at TEXT, state TEXT, payload TEXT NOT NULL)')
        for poll in snap['polls']:
            conn.execute('INSERT INTO poll_cache(id,source_id,published_at,state,payload) VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET published_at=excluded.published_at,state=excluded.state,payload=excluded.payload',(poll['id'],poll.get('source_id',''),poll.get('published_at'),poll.get('state'),json.dumps(poll)))
    return changes

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');parser.add_argument('--max-pages',type=int,default=2);parser.add_argument('--providers',default='votehub,pollresults,gdelt,fec,congress,openstates');parser.add_argument('--openstates-states',default=None,help='Comma-separated state codes (GA,NY) or all; default: 4-state rotating batch');args=parser.parse_args();logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s');print(json.dumps(collect_once(providers=args.providers.split(','),max_pages=max(1,min(5,args.max_pages)),offline=args.offline,openstates_states=args.openstates_states),indent=2))
