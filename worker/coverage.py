import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
snap=json.loads((ROOT/'site/data/snapshot.json').read_text())
states=json.loads((ROOT/'data/states.json').read_text());states.append(['DC','Washington, D.C.',38.91,-77.03]) if not any(s[0]=='DC' for s in states) else None
coverage=[]
for code,name,*_ in states:
    pp=[p for p in snap['polls'] if p.get('state')==code]
    dd=[d for d in snap.get('debates',[]) if d.get('state')==code]
    ll=[r for r in snap.get('legislation',[]) if r.get('state')==code]
    coverage.append({'state':code,'name':name,'poll_records':len(pp),'state_legislative_records':len(ll),'debate_records':len(dd),'verified_state_poll_coverage':bool(pp),'note':'No state-specific estimate inferred from national records' if not pp else None})
report={'generated_at':snap['generated_at'],'states':coverage,'national_poll_records':sum(p.get('state') is None for p in snap['polls']),'state_poll_records':sum(p.get('state') is not None for p in snap['polls'])}
for target in (ROOT/'site/data/coverage.json',ROOT/'docs/state_coverage.json'):target.write_text(json.dumps(report,indent=2)+'\n')
print('Coverage',len(coverage),'states/DC;',sum(x['verified_state_poll_coverage'] for x in coverage),'with verified state polls')
