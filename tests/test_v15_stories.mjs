import test from 'node:test';
import assert from 'node:assert/strict';
import {STORY_CHARACTERS,STORY_WORLDS,STORY_STORE_KEY,createStoryRun,applyStoryChoice,rewindStory,storyEnding,storyCompletion,getStoryScene,getStoryEvidence,civicQuestMarkup} from '../site/civic-story.js';

test('three distinct characters have a starting scene and a choice-driven experience',()=>{
 assert.deepEqual(STORY_CHARACTERS.map(x=>x.id),['maya','jordan','elena']);
 assert.ok(STORY_STORE_KEY.includes('stories'));
 assert.match(civicQuestMarkup(),/The Stories/);
 assert.doesNotMatch(civicQuestMarkup(),/quiz|check my answer/i);
 for(const c of STORY_CHARACTERS){const run=createStoryRun(c.id);assert.equal(run.sceneId,'start');assert.equal(run.history.length,0);assert.ok(getStoryScene(c.id,'start').choices.length>=2)}
});
test('every choice points to a real scene or an ending and has a meaningful consequence',()=>{
 for(const [id,world] of Object.entries(STORY_WORLDS)){
  assert.equal(world.endings.length,3);
  for(const [sceneId,scene] of Object.entries(world.scenes)){
    assert.ok(scene.body.length>=2,`${id}/${sceneId} needs a narrative`);
    assert.ok(scene.quote&&scene.speaker,`${id}/${sceneId} needs character dialogue`);
    assert.ok(scene.choices.length>=2,`${id}/${sceneId} must branch`);
    for(const choice of scene.choices){
      assert.ok(choice.to==='end'||world.scenes[choice.to],`${id}/${sceneId} points to invalid ${choice.to}`);
      assert.ok(Object.values(choice.impact).some(n=>n>0),`${id}/${sceneId} has a choice without consequences`);
      assert.ok(choice.note.length>25);
    }
  }
 }
});
test('choices change which scene comes next and rewind restores the previous choice',()=>{
 let a=createStoryRun('maya');let b=createStoryRun('maya');
 a=applyStoryChoice(a,0);b=applyStoryChoice(b,1);
 assert.equal(a.sceneId,'neighbors');assert.equal(b.sceneId,'library');
 assert.equal(rewindStory(a).sceneId,'start');assert.equal(rewindStory(a).history.length,0);
 assert.throws(()=>applyStoryChoice(a,99));
});
test('every character has at least two distinct attainable endings',()=>{
 for(const person of STORY_CHARACTERS){
  const seen=new Set(),paths=[];
  function walk(run,limit){
    if(run.ended){seen.add(storyCompletion(run).id);paths.push(run);return}
    if(limit>=12)return;
    const s=getStoryScene(person.id,run.sceneId);
    for(let i=0;i<s.choices.length;i++)walk(applyStoryChoice(run,i),limit+1)
  }
  walk(createStoryRun(person.id),0);
  assert.ok(paths.length>=4,`${person.id} has insufficient story branches`);
  assert.equal(seen.size,3,`${person.id} should have three reachable endings, got ${[...seen]}`);
 }
});
test('data references only inspect real linked records; state and date rules are upheld',()=>{
 const fixture={polls:[
  {id:'national',title:'National housing poll',state:null,topic:'Housing',source_url:'https://example.org/national',published_at:'2026-10-01'},
  {id:'ga',subject:'Georgia housing poll',state:'GA',topic:'Housing',source_url:'https://example.org/ga',published_at:'2026-10-03'},
  {id:'future',subject:'Future housing poll',state:'GA',topic:'Housing',source_url:'https://example.org/future',published_at:'2026-11-02'},
  {id:'bad',subject:'Malicious URL',state:'GA',topic:'Housing',source_url:'javascript:alert(1)',published_at:'2026-10-05'}]};
 const ga=getStoryEvidence(fixture,'maya','library',{cutoff:'2026-10-10'});
 assert.deepEqual(ga.map(x=>x.id),['ga']);
 const national=getStoryEvidence(fixture,'maya','library',{state:'US',cutoff:'2026-10-10'});
 assert.ok(national.some(x=>x.id==='national'));
 assert.ok(!ga.some(x=>x.id==='national'));
 assert.deepEqual(getStoryEvidence({},'jordan','start'),[]);
});
