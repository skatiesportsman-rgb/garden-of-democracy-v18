"""Regression: V11 cottage-garden national map restored, newer story remains.

The rectangles in the browser test are *test-only* geographic shapes; they are
not shipped as political/geographic information. The production site loads its
real state boundaries from the documented atlas source.
"""
from pathlib import Path
import base64,json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
FIPS=['01','02','04','05','06','08','09','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']

def test_restored_map_source_contract():
    js=(SITE/'app.js').read_text()
    css=(SITE/'style.css').read_text()
    # Keep the Version 11 aesthetic and stories, but ensure evidence stays in a state.
    assert 'statePoint(' in js
    assert 'createStateSlots(' in js
    assert 'stateLayer(' in js
    assert "svgEl('clipPath'" in js
    assert 'mapPollSelection()' in js
    assert "class:'garden-flower flower-anchor'" in js
    assert 'flower-stem-sway' in js
    assert '@keyframes rootedWind' in css
    assert '#mapFlowers .garden-flower{animation:none!important' in css
    assert 'animation:financeDrift' not in css
    assert 'import {civicQuestMarkup,mountCivicQuest}' in js


def test_original_map_and_story_in_browser():
    html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
    css=(SITE/'style.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap');",'')
    css=css.replace('./assets/cottage-meadow.svg','data:image/svg+xml;base64,'+base64.b64encode((SITE/'assets/cottage-meadow.svg').read_bytes()).decode())
    html=html.replace('</head>','<style>'+css+'</style></head>')
    js=(SITE/'garden-answer.js').read_text().replace('export ','')+(SITE/'civic-story.js').read_text().replace('export ','')+(SITE/'app.js').read_text().replace("import {civicQuestMarkup,mountCivicQuest} from './civic-story.js';",'').replace("import {askGarden} from './garden-answer.js';",'')
    payload={name:json.loads((SITE/'data'/name).read_text()) for name in ('snapshot.json','states.json')}
    arcs=[];geometries=[]
    for i,fips in enumerate(FIPS):
        col=i%10;row=i//10;x=col*90;y=row*90
        arcs.append([[x,y],[78,0],[0,75],[-78,0],[0,-75]])
        geometries.append({'type':'Polygon','id':int(fips),'arcs':[[i]]})
    # Test-only crowded state datasets; never included in published snapshots.
    import copy
    sample=payload['snapshot.json']['polls'][0]
    for state in ('GA','TX','MI'):
        for j in range(18):
            rec=copy.deepcopy(sample)
            rec.update(id=f'test-poll-{state}-{j}',state=state,published_at='2026-10-01',source_url='https://example.org/verified-poll',topic='Housing')
            payload['snapshot.json']['polls'].append(rec)
        for j in range(12):
            payload['snapshot.json'].setdefault('finance',[]).append({'id':f'test-finance-{state}-{j}','state':state,'published_at':'2026-10-01','source_url':'https://example.org/filing','candidate':'Synthetic test candidate','topic':'Housing'})
    payload['states-albers-10m.json']={'type':'Topology','arcs':arcs,'objects':{'states':{'type':'GeometryCollection','geometries':geometries}}}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        for width,height in [(1440,900),(390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='no-preference')
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(html,wait_until='domcontentloaded')
            page.evaluate('payload=>{window.fetch=(url)=>{const key=String(url).split("/").pop().split("?")[0];return payload[key]?Promise.resolve({ok:true,json:async()=>payload[key]}):Promise.reject(new Error("offline test"))}}',payload)
            page.evaluate('code=>(0,eval)(code)',js)
            page.wait_for_function('document.querySelectorAll(".us-state").length===51', timeout=16000)
            assert page.locator('#mapFlowers .garden-flower').count()>0
            assert page.locator('clipPath[id^="garden-clip-"]').count()==51
            assert page.locator('#mapFlowers .flower-anchor').count()>0
            assert page.locator('#mapEvents').count()==1
            assert page.locator('#mapFlowers .garden-flower').first.evaluate('(el)=>getComputedStyle(el).animationName')=='none'
            assert page.locator('#mapFlowers .flower-stem-sway').first.evaluate('(el)=>getComputedStyle(el).animationName')=='rootedWind'
            # All anchor coordinates are inside the exact state clip geometry.
            verification=page.evaluate("""() => {
             const result={count:0,failed:[]};
             for (const group of document.querySelectorAll('#mapFlowers [id^="state-layer-"] , #mapEvents [id^="state-layer-"]')) {
              const code=group.id.split('-').at(-1);
              const poly=document.querySelector(`#garden-clip-${code} path`);
              for (const mark of group.children){
               let x,y;
               if(mark.classList.contains('flower-anchor')){
                const m=mark.getAttribute('transform').match(/translate\\(([^ ]+) ([^)]+)\\)/);
                x=+m[1];y=+m[2];
               } else if (mark.tagName.toLowerCase()==='text') {x=+mark.getAttribute('x');y=+mark.getAttribute('y')}
               else continue;
               result.count++;
               if(!poly.isPointInFill(new DOMPoint(x,y))) result.failed.push(`${code}: ${x},${y}`);
              }
             }
             return result;
            }""")
            assert verification['count']>25,verification
            assert not verification['failed'],verification
            first=page.locator('#mapFlowers .flower-anchor').first
            planted=first.get_attribute('transform')
            page.wait_for_timeout(350)
            assert first.get_attribute('transform')==planted

            page.locator('#layerPolls').uncheck()
            assert page.locator('#mapFlowers .garden-flower').count()==0
            page.locator('#layerPolls').check()
            assert page.locator('#mapFlowers .garden-flower').count()>0
            page.locator('.nav-pair[data-section="learn"] > summary').click()
            page.locator('button[data-view="game"]').click()
            assert page.locator('[data-story-person]').count()==3
            assert not errors,errors
            page.close()
        browser.close()
