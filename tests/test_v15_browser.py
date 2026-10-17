"""Browser regression of storybook using real website JS and bundled, source-linked data.
A local host is not required; the harness keeps external API calls disabled.
"""
from pathlib import Path
import base64,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'

def test_storybook_real_browser():
    html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
    css=(SITE/'style.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap');",'')
    css=css.replace('./assets/cottage-meadow.svg','data:image/svg+xml;base64,'+base64.b64encode((SITE/'assets/cottage-meadow.svg').read_bytes()).decode())
    html=html.replace('</head>','<style>'+css+'</style></head>')
    js=(SITE/'garden-answer.js').read_text().replace('export ','')+(SITE/'civic-story.js').read_text().replace('export ','')+(SITE/'app.js').read_text().replace("import {civicQuestMarkup,mountCivicQuest} from './civic-story.js';",'').replace("import {askGarden} from './garden-answer.js';",'')
    payload={name:json.loads((SITE/'data'/name).read_text()) for name in ('snapshot.json','states.json')}
    with sync_playwright() as playwright:
      browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
      for w,h in ((1440,900),(390,844)):
        page=browser.new_page(viewport={'width':w,'height':h},reduced_motion='reduce')
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded')
        page.evaluate('payload=>{window.fetch=(url)=>{const k=String(url).split("/").pop().split("?")[0];return payload[k]?Promise.resolve({ok:true,json:async()=>payload[k]}):Promise.reject(Error("Offline test"))}}',payload)
        page.evaluate('code=>(0,eval)(code)',js)
        page.locator('.nav-pair[data-section="learn"] > summary').click()
        page.locator('button[data-view="game"]').click()
        page.locator('[data-story-person="maya"]').wait_for(timeout=15000)
        assert page.locator('[data-story-person]').count()==3
        page.locator('[data-story-person="maya"]').click()
        assert 'The notice on the table' in page.locator('.story-scene-text h3').inner_text()
        page.locator('[data-story-choice="0"]').click()
        assert 'Different doors' in page.locator('.story-scene-text h3').inner_text()
        page.locator('#storyUndo').click()
        assert 'The notice on the table' in page.locator('.story-scene-text h3').inner_text()
        page.locator('[data-story-choice="1"]').click()
        assert 'A flower is not a forecast' in page.locator('.story-scene-text h3').inner_text()
        page.locator('#storyDepth').select_option('detailed')
        assert page.locator('.story-context').is_visible()
        page.locator('#storyEvidenceToggle').click()
        assert page.locator('.story-evidence').is_visible()
        page.locator('[data-story-person="jordan"]').click()
        assert 'Twenty seconds' in page.locator('.story-scene-text h3').inner_text()
        page.locator('[data-story-person="maya"]').click()
        assert 'A flower is not a forecast' in page.locator('.story-scene-text h3').inner_text()
        assert not errors,errors
        page.locator('[data-story-person="elena"]').click()
        page.screenshot(path=str(ROOT/'docs'/f'v15-stories-{w}.png'),full_page=True)
        page.close()
      browser.close()
