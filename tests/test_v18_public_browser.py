"""Offline desktop/mobile frontend test; separate preflight checks nested HTTP paths.

The sandbox can reject loopback browser navigation. This test uses the real
frontend modules and a test-only synthetic geographic topology with no network.
"""
from pathlib import Path
import base64,json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
FIPS=['01','02','04','05','06','08','09','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']


def test_observatory_and_story_desktop_mobile_offline():
    html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
    css=(SITE/'style.css').read_text()
    css=css.replace('./assets/cottage-meadow.svg','data:image/svg+xml;base64,'+base64.b64encode((SITE/'assets/cottage-meadow.svg').read_bytes()).decode())
    html=html.replace('</head>','<style>'+css+'</style></head>')
    js=(SITE/'garden-answer.js').read_text().replace('export ','')+(SITE/'civic-story.js').read_text().replace('export ','')+(SITE/'app.js').read_text().replace("import {civicQuestMarkup,mountCivicQuest} from './civic-story.js';",'').replace("import {askGarden} from './garden-answer.js';",'')
    payload={name:json.loads((SITE/'data'/name).read_text()) for name in ('snapshot.json','states.json','deployment.json')}
    arcs=[];geometries=[]
    for i,fips in enumerate(FIPS):
        x=i%10*90;y=i//10*90
        arcs.append([[x,y],[78,0],[0,75],[-78,0],[0,-75]])
        geometries.append({'type':'Polygon','id':int(fips),'arcs':[[i]]})
    payload['states-albers-10m.json']={'type':'Topology','arcs':arcs,'objects':{'states':{'type':'GeometryCollection','geometries':geometries}}}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width,height in ((1440,900),(390,844)):
                page=browser.new_page(viewport={'width':width,'height':height})
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.set_content(html,wait_until='domcontentloaded')
                page.evaluate('payload=>{window.fetch=(url)=>{const key=String(url).split("/").pop().split("?")[0];return payload[key]?Promise.resolve({ok:true,json:async()=>payload[key]}):Promise.reject(new Error("offline fixture"))}}',payload)
                page.evaluate('code=>(0,eval)(code)',js)
                page.wait_for_function('document.querySelectorAll(".us-state").length===51',timeout=16000)
                assert page.locator('.garden-flower').count()>0
                page.locator('.nav-pair[data-section="signals"] summary').click()
                page.locator('.nav-pair[data-section="signals"] button[data-view="sources"]').click()
                assert page.locator('.launch-health').count()==1
                assert 'Public garden build' in page.locator('.launch-health').inner_text()
                assert 'not-run' in page.locator('.launch-health').inner_text()
                page.locator('.nav-pair[data-section="learn"] summary').click()
                page.locator('button[data-view="game"]').click()
                assert page.locator('[data-story-person]').count()==3
                assert errors==[],errors
                page.close()
        finally:browser.close()
