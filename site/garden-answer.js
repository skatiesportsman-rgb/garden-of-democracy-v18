/* Evidence-grounded Ask the Garden engine. Runs on GitHub Pages for $0;
 * local FastAPI may optionally enhance its explanations using local Ollama.
 * No external third-party AI calls, no hidden extrapolations.
 */
export const ANSWER_LEVELS = ['simple', 'standard', 'detailed'];
const terms = str => String(str??'').toLowerCase().replace(/[^a-z0-9]+/g,' ').split(/\s+/).filter(Boolean);
const IGNORE = new Set('a an and are as at be can could did do does explain for from how i is it me my of on or our say says show should so the their there these this to us what when where which who why with would you your 2026 midterm election elections political poll polls polling survey surveys latest current data information opinion people about state states voter voters public garden candidate candidates debates debate took place happened recent available records recorded finance funding financial legislation bill bills issue issues news media articles articles latest newest'.split(' '));
const TOPICS = {
  Affordability:['economy','economic','inflation','price','prices','cost','costs','groceries','wage','wages','affordable','affordability'],
  Healthcare:['health','healthcare','medicaid','medicare','insurance','abortion'],
  Housing:['housing','rent','home','homes','mortgage','apartment'],
  Immigration:['immigration','border','migrant','asylum'],
  Education:['education','school','student','university','college'],
  Elections:['vote','voting','ballot','election','registration','turnout'],
  Representation:['congress','congressional','house','senate','generic ballot'],
  Leadership:['approval','president','governor','favorability','leadership']
};
const CATEGORY_WORDS={polls:/\b(polls?|polling|survey|approval|support|favorability|voters? think)\b/i,finance:/\b(finance|financing|contribution|spending|fundraising|money|donation|fec|receipts|expenditures|cash)\b/i,legislation:/\b(legislation|bill|congress|law|laws|policy|legislative|committee|sponsor)\b/i,debates:/\b(debate|debates|butterflies|moderator|candidate statements)\b/i,news:/\b(articles?|coverage|news|headlines?|fireflies|media)\b/i};
const recordDate=(r,type)=>String(r.published_at||r.filing_date||r.reported_at||r.date||r.created_at||'').slice(0,10);
const cleanURL=s=>{try{const u=new URL(String(s));return u.protocol==='https:'||u.protocol==='http:'?u.href:null}catch{return null}};
const fmtD=d=>{if(!d)return'date not reported';const dt=new Date(d+'T12:00:00Z');return isNaN(+dt)?'date not reported':dt.toLocaleDateString('en-US',{year:'numeric',month:'short',day:'numeric',timeZone:'UTC'})};
const money=n=>Number.isFinite(Number(n))?'$'+Number(n).toLocaleString('en-US',{maximumFractionDigits:0}):'amount not reported';
const textField=(r,t)=>t==='polls'?[r.subject,r.question,r.pollster,r.topic,r.type,...(r.answers||[]).map(x=>x.choice)].join(' '):t==='finance'?[r.committee,r.candidate,r.type,r.topic].join(' '):t==='legislation'?[r.title,r.topic,r.action,r.note].join(' '):t==='debates'?[r.race,r.place,...(r.participants||[]),...(r.topics||[])].join(' '):[r.title,r.topic,r.domain].join(' ');
const recTitle=(r,t)=>t==='polls'?r.subject||r.question||'Published poll':t==='debates'?r.race||'Documented debate':t==='finance'?r.candidate||r.committee||'Campaign finance record':t==='legislation'?r.title||'Congressional bill':r.title||'News article';
const recUrl=(r,t)=>cleanURL(r.source_url||(t==='news'?r.url:null));
const recPublisher=(r,t)=>t==='polls'?r.pollster||r.source_name||'Poll publisher':t==='finance'?'Federal Election Commission':t==='legislation'?(r.source_id==='openstates'?'Plural Open / OpenStates':'Congress.gov'):t==='debates'?r.source||'Debate publisher':r.domain||'Article publisher';
export function askGarden(snapshot,question,options={}){
  const q=String(question||'').trim();
  const level=ANSWER_LEVELS.includes(options.level)?options.level:'standard';
  const states=Array.isArray(options.states)?options.states:[];
  if(!q||q.length>500)return {answer:'Enter a question of 1–500 characters about the published records in this garden.',evidence:[],mode:'evidence',insufficient:true};
  const normalized=' '+q.toLowerCase().replace(/[^a-z0-9]+/g,' ')+' ';
  const explicit=states.find(s=>normalized.includes(' '+String(s[1]).toLowerCase().replace(/[^a-z0-9]+/g,' ')+' '));
  const state=explicit?.[0]||(options.state&&options.state!=='US'&&!/\b(national|nationwide|across the us|across america|united states)\b/i.test(q)?options.state:null);
  const location=state?(states.find(s=>s[0]===state)?.[1]||state):'the United States';
  const cutoff=options.cutoff||new Date().toISOString().slice(0,10);
  const topic=Object.keys(TOPICS).find(t=>normalized.includes(' '+t.toLowerCase()+' ')) || Object.entries(TOPICS).find(([k,words])=>words.some(w=>normalized.includes(' '+w+' ')))?.[0]||null;
  const kinds=Object.entries(CATEGORY_WORDS).filter(([k,re])=>re.test(q)).map(([k])=>k);
  const types=kinds.length?kinds:['polls','debates','legislation','finance','news'];
  const locationTerms=state?terms(states.find(s=>s[0]===state)?.[1]||''):[];
  const queryTokens=terms(q).filter(t=>!IGNORE.has(t)&&t.length>2&&!locationTerms.includes(t)&&!Object.values(TOPICS).flat().includes(t));
  const noForecast=/\b(who will win|will (they|he|she|it|the|democrats|republicans) win|predict|forecast|winning probability|chance of winning|projected winner)\b/i.test(q);
  const debateWinner=/\b(won the debate|debate winner|who won.*debate)\b/i.test(q);
  const candidates=[];
  for(const type of types){for(const r of snapshot[type]||[]){if(!recUrl(r,type))continue;
      const dt=recordDate(r,type);if(!dt||dt>cutoff)continue;
      // Explicit state scope: do NOT assign national records to a state.
      if(state&&r.state!==state)continue;
      const title=recTitle(r,type);const hay=' '+textField(r,type).toLowerCase().replace(/[^a-z0-9]+/g,' ')+' ';
      const topics=[r.topic,...(r.topics||[])].filter(Boolean);
      if(topic&&!topics.includes(topic)&&!TOPICS[topic].some(w=>hay.includes(' '+w+' ')))continue;
      const overlap=queryTokens.filter(t=>hay.includes(' '+t+' ')).length;
      // A narrow named query should not return unrelated, recent records.
      if(queryTokens.length>=2&&!overlap&&!topic)continue;
      const score=overlap*5+(topic?7:0)+(state?3:0)+(type===types[0]?2:0);
      candidates.push({type,record:r,date:dt,title,publisher:recPublisher(r,type),url:recUrl(r,type),score});
  }}
  candidates.sort((a,b)=>b.score-a.score || b.date.localeCompare(a.date) || String(a.record.id).localeCompare(String(b.record.id)));
  const limit=level==='simple'?2:level==='standard'?4:7;
  const selected=candidates.slice(0,limit);
  if(noForecast){return {answer:'This garden does not predict election winners. Polls describe surveyed groups at particular times; they are not election results. Explore the dated measurements and their methodologies below instead.',evidence:selected.map(({record,type,url,date,title,publisher})=>({id:record.id,type,url,date,title,publisher})),mode:'evidence',insufficient:true,scope:location,level};}
  if(debateWinner){return {answer:'The Garden does not choose debate winners. Without a source-linked, methodologically documented post-debate survey, there is no measured winner to report. The available event records are listed below.',evidence:selected.map(({record,type,url,date,title,publisher})=>({id:record.id,type,url,date,title,publisher})),mode:'evidence',insufficient:true,scope:location,level};}
  if(!selected.length){return {answer:`I couldn't find a matching, dated, source-linked record for ${location}${topic?' about '+topic.toLowerCase():''} in the garden through ${fmtD(cutoff)}. That is a data-coverage limitation, not evidence that nothing is happening. Try a broader issue, another location, or inspect the Source Observatory.`,evidence:[],mode:'evidence',insufficient:true,scope:location,level};}
  const sentence=c=>{const {record:r,type}=c;
    if(type==='polls'){const answers=(r.answers||[]).filter(a=>Number.isFinite(Number(a.pct))).slice(0,level==='simple'?2:6).map(a=>`${a.choice}: ${a.pct}%`).join('; ');
      const meta=level==='simple'?'':` Surveyed ${r.population||'an unspecified population'}${r.sample_size?' (n='+r.sample_size+')':''}${r.start_date&&r.end_date?', fieldwork '+fmtD(r.start_date)+'–'+fmtD(r.end_date):''}${r.moe!=null?'; reported margin of error ±'+r.moe+' points':''}.`;
      return `${c.title} (${c.publisher}, ${fmtD(c.date)}; ${r.state||'national'}): ${answers||'response percentages not recorded'}.${meta}${level==='detailed'&&r.question?' Question: “'+r.question+'”':''}`;
    }
    if(type==='finance'){return `${c.title}: the FEC record reports ${money(r.receipts??r.amount)} in candidate-cycle receipts${r.disbursements!=null?' and '+money(r.disbursements)+' in disbursements':''} (published ${fmtD(c.date)}). This is a filing-based aggregate, not a live transaction or support measurement.`;}
    if(type==='legislation'){return `${c.title} (${c.publisher}, ${r.state||'national'}, ${fmtD(c.date)}): ${r.action||'latest action not specified'}. A bill record is not proof that it became law.`;}
    if(type==='debates'){return `${c.title} (${fmtD(c.date)}): participants ${((r.participants||[]).join(' and '))||'not reported'}; documented issues ${((r.topics||[]).join(', '))||'not reported'}. A debate record is not a measure of who performed better.`;}
    return `${c.title} (${c.publisher}, ${fmtD(c.date)}). This is observed news coverage, not representative public opinion.`;
  };
  const head=`I found ${candidates.length} matching record${candidates.length===1?'':'s'} in the garden for ${location}${topic?' about '+topic.toLowerCase():''}, through ${fmtD(cutoff)}. Here ${selected.length===1?'is':'are'} ${selected.length} source-linked example${selected.length===1?'':'s'}:`;
  const body=selected.map((c,i)=>`${i+1}. ${sentence(c)}`).join('\n\n');
  const end=level==='detailed'?'\n\nThese records have different collection methods, populations, geographic scopes and publication dates; they are not directly interchangeable. Check individual original sources before comparing values. News volume, campaign money and legislative actions are not opinion polls.':'\n\nThese are dated observations, not election forecasts; they do not represent everyone’s views.';
  return {answer:head+'\n\n'+body+end,evidence:selected.map(({record,type,url,date,title,publisher})=>({id:record.id,type,url,date,title,publisher})),mode:'evidence',insufficient:false,scope:location,level,total:candidates.length};
}
