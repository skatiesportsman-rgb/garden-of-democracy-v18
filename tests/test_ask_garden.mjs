import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {askGarden} from '../site/garden-answer.js';
const data=JSON.parse(readFileSync(new URL('../site/data/snapshot.json',import.meta.url)));
const states=JSON.parse(readFileSync(new URL('../data/states.json',import.meta.url)));
const answer=(q,level='standard',opts={})=>askGarden(data,q,{states,level,cutoff:'2026-10-15',...opts});

test('simple vs detailed changes source volume and depth',()=>{
 const simple=answer('What do polls say about Michigan?','simple'), detailed=answer('What do polls say about Michigan?','detailed');
 assert.ok(simple.answer.includes('%'));assert.ok(detailed.answer.includes('Surveyed'));
 assert.ok(detailed.evidence.length>=simple.evidence.length);
});
test('explicit state geography must not include national-only polls',()=>{
 const a=answer('What do polls say about Georgia?');
 assert.ok(a.evidence.length>0);assert.ok(a.evidence.every(x=>data.polls.find(p=>p.id===x.id).state==='GA'));
});
test('candidate debates are returned for named state',()=>{
 const a=answer('Which debates took place in Georgia?');
 assert.ok(a.evidence.length>0);assert.ok(a.evidence.every(x=>x.type==='debates'));
});
test('no hallucinated legislative facts when the archive is empty',()=>{
 const a=askGarden(
   {...data, legislation: []},
   'What legislation is recorded?',
   {states, level:'standard', cutoff:'2026-10-15'}
 );
 assert.equal(a.evidence.length,0);
 assert.equal(a.insufficient,true);
});
test('no election forecast or invented debate winner',()=>{
 assert.match(answer('Who will win Georgia?').answer,/does not predict election winners/);
 assert.match(answer('Who won the Georgia debate?').answer,/does not choose debate winners/);
});
test('historical replay excludes records published afterward',()=>{
 const a=answer('What do polls say about affordability?','detailed',{cutoff:'2026-01-01'});
 assert.equal(a.evidence.length,0);
});
test('malicious content is not interpreted as facts without a source',()=>{
 const a=answer('What do survey records say about non-existing Moonflower-X9?');
 assert.equal(a.evidence.length,0);
});
test('changes to selected state restrict evidence',()=>{
 const a=answer('Which debates are available?','detailed',{state:'MI'});
 assert.ok(a.evidence.length>0);assert.ok(a.evidence.every(x=>data.debates.find(d=>d.id===x.id).state==='MI'));
});

test('OpenStates bill is state-scoped, sourced, and uses distinct publisher',()=>{
 const seeded={...data,legislation:[{id:'fixture-openstates-ga',state:'GA',source_id:'openstates',type:'state_bill',title:'Georgia public housing program bill',topic:'Housing',action:'Introduced in House',published_at:'2026-10-01',source_url:'https://openstates.org/ga/bills/2025/HB123/'}]};
 const a=askGarden(seeded,'What housing legislation is recorded in Georgia?',{states,level:'standard',cutoff:'2026-10-15'});
 assert.equal(a.evidence.length,1);
 assert.equal(a.evidence[0].publisher,'Plural Open / OpenStates');
 assert.match(a.answer,/Introduced in House/);
 assert.ok(!a.answer.includes('Congress.gov'));
});
