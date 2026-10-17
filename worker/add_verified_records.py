"""Curated dated records verified against cited original reporting, not synthetic fixtures."""
import json,pathlib
root=pathlib.Path(__file__).resolve().parents[1];path=root/'site/data/snapshot.json';s=json.loads(path.read_text())
base={'source_id':'fox-editorial','source_name':'Fox News Poll','pollster':'Beacon Research / Shaw & Company Research','sponsor':'Fox News','topic':'Representation','type':'senate','question_exact':False,'method':'Mixed-mode phone and text-to-online random statewide voter-file survey','verification':'published_report','completeness_note':'Reported rounded options only. Exact survey wording appears in original poll toplines. No other shares are inferred.','retrieved_at':'2026-10-15T14:00:00Z'}
def rec(id,state,office,subject,answers,pop,n,moe,start,end,published,url):
    return dict(base,id=id,state=state,type=office,subject=subject,question=f'{subject}, among {pop.lower()} (summary, not verbatim question)',answers=[{'choice':a,'pct':b} for a,b in answers],population=pop,sample_size=n,moe=moe,start_date=start,end_date=end,published_at=published,source_url=url)
mi='https://www.foxnews.com/politics/fox-news-poll-michigan-voters-split-between-el-sayed-rogers/'
tx='https://www.foxnews.com/politics/fox-news-poll-its-lone-star-senate-showdown-between-talarico-paxton'
ga='https://www.foxnews.com/politics/fox-news-poll-early-look-georgia-senate-race.amp'
records=[
 rec('fox-mi-2026-sep-senate-lv','MI','senate','Michigan 2026 Senate — likely voters',[('Abdul El-Sayed',50),('Mike Rogers',49)],'Likely voters',1028,3,'2026-09-24','2026-09-28','2026-09-30',mi),
 rec('fox-mi-2026-sep-senate-rv','MI','senate','Michigan 2026 Senate — registered voters',[('Abdul El-Sayed',51),('Mike Rogers',48)],'Registered voters',1203,2.5,'2026-09-24','2026-09-28','2026-09-30',mi),
 rec('fox-mi-2026-sep-governor-lv','MI','governor','Michigan 2026 Governor — likely voters',[('Jocelyn Benson',54),('John James',45)],'Likely voters',1028,3,'2026-09-24','2026-09-28','2026-09-30',mi),
 rec('fox-tx-2026-sep-senate-lv','TX','senate','Texas 2026 Senate — likely voters',[('James Talarico',51),('Ken Paxton',49)],'Likely voters',881,3,'2026-09-24','2026-09-28','2026-10-01',tx),
 rec('fox-ga-2026-jun-senate-rv','GA','senate','Georgia 2026 Senate — registered voters',[('Jon Ossoff',56),('Mike Collins',43)],'Registered voters',1002,3,'2026-06-23','2026-06-27','2026-07-01',ga),
]
existing={r['id']:r for r in s.get('polls',[])};existing.update({r['id']:r for r in records});s['polls']=sorted(existing.values(),key=lambda p:p['published_at'],reverse=True)
s['debates']=[{'id':'mi-2026-senate-debate-20261008','state':'MI','race':'2026 U.S. Senate','date':'2026-10-08','place':'Grand Rapids, Michigan','participants':['Abdul El-Sayed','Mike Rogers'],'topics':['Affordability','Healthcare','Foreign policy'],'source_url':'https://www.foxnews.com/politics/michigan-senate-debate-erupts-personal-attacks-rogers-el-sayed-clash-over-israel-iran-more','source':'Fox News reporting on completed debate','transcript_url':None,'winner':None,'verification':'reported-event','note':'Debate record verified in contemporaneous reporting; full transcript not available in the present dataset.'}]
path.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n');print('Curated verified polls:',len(s['polls']),'debates:',len(s['debates']))
