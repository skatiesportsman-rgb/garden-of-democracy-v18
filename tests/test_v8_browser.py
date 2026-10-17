"""In-memory Chromium smoke test; avoids sandbox local-network restrictions."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA={key:json.loads((SITE/'data'/key).read_text()) for key in ('snapshot.json','states.json','usa_coastline.json','state_lines.json')}


def run():
    source=(SITE/'garden-answer.js').read_text().replace('export const ','const ').replace('export function ','function ')
    app=(SITE/'app.js').read_text().replace("import {askGarden} from './garden-answer.js';",'')
    html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
    html=html.replace('</head>','<style>'+ (SITE/'style.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap');",'')+'</style></head>')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        for label,width,height in [('desktop',1440,900),('mobile',390,844)]:
            print(label,'starting',flush=True)
            page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
            errors=[]
            page.on('pageerror',lambda x:errors.append(str(x)))
            page.set_content(html,wait_until='domcontentloaded')
            print(label,'set content',flush=True)
            page.evaluate('(payload)=>{window.fetch=(url)=>{let key=String(url).split("/").pop().split("?")[0];return payload[key]?Promise.resolve({ok:true,json:async()=>payload[key]}):Promise.reject(Error("Outside sandbox network disabled"))}}',DATA)
            page.evaluate('(code)=>{(0,eval)(code)}',source+'\n'+app)
            print(label,'eval',flush=True)
            page.wait_for_timeout(600)
            assert page.locator('details.nav-pair').count()==5
            assert all(page.locator('details.nav-pair').nth(i).locator('button.nav').count()==2 for i in range(5))
            print(label,'nav',flush=True)
            page.locator('details.nav-pair').first.locator('summary').click()
            assert page.locator('details.nav-pair').first.get_attribute('open') is not None
            # One submenu navigation link changes the view and closes the menu.
            page.locator('.nav[data-view="polls"]').click()
            assert page.locator('.poll-tile').count()==10
            assert page.locator('details.nav-pair[open]').count()==0
            page.locator('.nav-ask').click()
            assert page.locator('#gardenAskForm').count()==1
            print(label,'screenshot',flush=True)
            assert page.locator('#gardenAskForm').is_visible()
            page.screenshot(path=str(ROOT/'docs'/f'v8-ask-{label}.png'),full_page=True,animations='disabled',timeout=15000)
            print(label,'question',flush=True)
            assert page.locator('#askSubmit').is_visible()
            page.locator('#askQuestion').fill('What do polls say about Georgia?')
            page.locator('#askLevel').select_option('simple')
            page.locator('#askSubmit').click()
            page.wait_for_timeout(350)
            assert 'Georgia' in page.locator('#askAnswer').inner_text()
            assert page.locator('#askAnswer .ask-source').count()>=1
            print(label,'question',flush=True)
            page.locator('#askQuestion').fill('Who will win the 2026 election?')
            page.locator('#askSubmit').click()
            page.wait_for_timeout(200)
            assert 'does not predict election winners' in page.locator('#askAnswer').inner_text()
            assert not errors, (label,errors)
            print(label,'passed paired nav + question + sources + forecast refusal')
            page.close()
        browser.close()

if __name__=='__main__':run()
