"""Exercise real client code and test-only harvested journal entries in Chromium."""
from pathlib import Path
import base64
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'


def test_harvest_desktop_and_mobile():
    html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
    css=(SITE/'style.css').read_text()
    css=css.replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap');",'')
    css=css.replace('./assets/cottage-meadow.svg','data:image/svg+xml;base64,'+base64.b64encode((SITE/'assets/cottage-meadow.svg').read_bytes()).decode())
    html=html.replace('</head>','<style>'+css+'</style></head>')
    js=(SITE/'garden-answer.js').read_text().replace('export ','')+(SITE/'civic-story.js').read_text().replace('export ','')+(SITE/'app.js').read_text().replace("import {askGarden} from './garden-answer.js';",'').replace("import {civicQuestMarkup,mountCivicQuest} from './civic-story.js';",'')
    payload={name:json.loads((SITE/'data'/name).read_text()) for name in ('snapshot.json','states.json')}
    # A test-only harvest event references a genuine bundled survey (no invented poll).
    poll=payload['snapshot.json']['polls'][0]
    payload['snapshot.json']['harvest']=[{'id':poll['id'],'kind':'polls','source_id':poll['source_id'],'change':'new','collected_at':'2026-10-16T10:00:00Z'}]
    with sync_playwright() as browser_driver:
        browser=browser_driver.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        for width,height in ((1440,900),(390,844)):
            page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(html,wait_until='domcontentloaded')
            page.evaluate('(payload)=>{window.fetch=(url)=>{const k=String(url).split("/").pop().split("?")[0];return payload[k]?Promise.resolve({ok:true,json:async()=>payload[k]}):Promise.reject(Error("Offline test"))}}',payload)
            page.evaluate('(code)=>(0,eval)(code)',js)
            page.locator('#harvestSummary').get_by_text('1',exact=False).first.wait_for(timeout=16000)
            assert page.locator('.harvest-entry').count()==1
            assert page.locator('[data-harvest-poll]').count()==1
            page.locator('.harvest-filter[data-harvest-kind="finance"]').click()
            assert page.locator('.harvest-entry').count()==0
            assert page.locator('.harvest-empty').count()==1
            page.locator('.harvest-filter[data-harvest-kind="polls"]').click()
            page.locator('[data-harvest-poll]').click()
            assert 'Published survey' in page.locator('#detailsBody').inner_text() or 'responses' in page.locator('#detailsBody').inner_text().lower()
            page.locator('#harvestSources').click()
            assert 'Every bloom has a provenance' in page.locator('#mainCanvas').inner_text()
            assert 'Collection snapshot:' in page.locator('#mainCanvas').inner_text()
            assert not errors,errors
            # Screenshot of actual app using a test-only ingestion event.
            page.locator('#brand').click()
            page.screenshot(path=str(ROOT/'docs'/f'v13-harvest-{width}.png'),full_page=True)
            page.close()
        browser.close()
