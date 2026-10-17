"""Run against a locally started server with GARDEN_TEST_URL (default http://127.0.0.1:8847)."""
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
URL=os.environ.get('GARDEN_TEST_URL','http://127.0.0.1:8847')
OUT=Path(__file__).resolve().parents[1]/'docs'
SITE=Path(__file__).resolve().parents[1]/'site'
PAYLOAD={x:json.loads((SITE/'data'/x).read_text()) for x in ('snapshot.json','states.json','usa_coastline.json','state_lines.json')}
HTML=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
CSS=(SITE/'style.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap');",'')
CSS=CSS.replace("./assets/cottage-meadow.svg",'data:image/svg+xml;base64,'+__import__('base64').b64encode((SITE/'assets'/'cottage-meadow.svg').read_bytes()).decode())
HTML=HTML.replace('</head>','<style>'+CSS+'</style></head>')
JS=(SITE/'garden-answer.js').read_text().replace('export const ','const ').replace('export function ','function ')+(SITE/'app.js').read_text().replace("import {askGarden} from './garden-answer.js';",'')

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        for w,h in ((1440,950),(390,844)):
            page=browser.new_page(viewport={'width':w,'height':h}, reduced_motion='reduce')
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(HTML,wait_until='domcontentloaded')
            page.evaluate('(payload)=>{window.fetch=(url)=>{const k=String(url).split("/").pop().split("?")[0];return payload[k]?Promise.resolve({ok:true,json:async()=>payload[k]}):Promise.reject(Error("Offline assets"))}}',PAYLOAD)
            page.evaluate('(code)=>{(0,eval)(code)}',JS)
            page.locator('#canvasStatus').wait_for(timeout=18000)
            page.wait_for_timeout(1500)
            assert page.locator('body').get_attribute('class').find('theme-meadow')>=0
            assert page.locator('#gardenMap').count()==1
            assert page.locator('#mapFlowers .garden-flower').count()>0
            page.screenshot(path=str(OUT/f'v11-garden-{w}.png'),full_page=True)
            page.locator('#compareBtn').click()
            assert page.locator('.parallel-plot').count()==2
            assert page.locator('#compare-0').input_value()=='GA'
            assert page.locator('#compare-1').input_value()=='MI'
            assert page.locator('.parallel-stats').count()==2
            assert page.locator('#parallelJournal').count()==1
            page.screenshot(path=str(OUT/f'v11-compare-{w}.png'),full_page=True)
            page.locator('[data-quest="source"]').click()
            assert '0 of 4' in page.locator('#parallelScore').inner_text(), 'Source badge must require opening evidence'
            page.locator('[data-quest="timeline"]').click()
            assert '0 of 4' in page.locator('#parallelScore').inner_text(), 'Time badge must require an earlier publication date'
            p_flower=page.locator('[data-bed-kind="polls"]')
            if p_flower.count():
                p_flower.first.click()
                assert page.locator('#parallelJournal li:not(.journal-empty)').count()>=1
            else:
                page.locator('.parallel-stat[data-kind="polls"]').first.click()
            page.locator('[data-quest="coverage"]').click()
            assert '1 of 4' in page.locator('#parallelScore').inner_text() or '2 of 4' in page.locator('#parallelScore').inner_text()
            page.locator('#parallelShuffle').click()
            assert page.locator('#compare-0').input_value()!=page.locator('#compare-1').input_value()
            page.locator('#parallelTopic').select_option('Housing')
            assert page.locator('.parallel-plot').count()==2
            page.locator('#parallelReset').click()
            assert '0 of 4' in page.locator('#parallelScore').inner_text()
            assert not errors,errors
            print(f'V11 desktop/mobile botanical comparison passed {w}x{h}; evidence sources, quest progress, shuffle, filters, reset')
            page.close()
        browser.close()

if __name__=='__main__':run()
