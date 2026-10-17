"""Browser-level integration of a synthetic state bill; no demo political data is published."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
PAYLOAD={x:json.loads((SITE/'data'/x).read_text()) for x in ('snapshot.json','states.json','usa_coastline.json','state_lines.json')}
PAYLOAD['snapshot.json']['legislation']=[
 {'id':'unit-bill-001','title':'Sample state housing bill (TEST ONLY)','type':'state_bill','state':'GA',
  'source_id':'openstates','topic':'Housing','action':'Introduced',
  'published_at':'2026-10-13','source_url':'https://openstates.org/ga/bills/2025/HB99/',
  'note':'Fictitious test record not published'}]

def run():
 source=(SITE/'garden-answer.js').read_text().replace('export const ','const ').replace('export function ','function ')
 app=(SITE/'app.js').read_text().replace("import {askGarden} from './garden-answer.js';",'')
 html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
 css=(SITE/'style.css').read_text()
 css=css.replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap');",'')
 html=html.replace('</head>','<style>'+css+'</style></head>')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width,height in [(1440,900),(390,844)]:
   page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.set_content(html,wait_until='domcontentloaded')
   page.evaluate('(payload)=>{window.fetch=(url)=>{const k=String(url).split("/").pop().split("?")[0];return payload[k]?Promise.resolve({ok:true,json:async()=>payload[k]}):Promise.reject(Error("sandbox network disabled"))}}',PAYLOAD)
   page.evaluate('(code)=>{(0,eval)(code)}',source+'\n'+app)
   page.wait_for_timeout(400)
   page.locator('.chip[data-state="GA"]').click()
   page.wait_for_timeout(100)
   assert '1 legislation' in page.locator('#layerDataStatus').inner_text()
   page.locator('details.nav-pair').nth(1).locator('summary').click()
   page.locator('.nav[data-view="legislation"]').click()
   assert 'Sample state housing bill (TEST ONLY)' in page.locator('#mainCanvas').inner_text()
   assert 'Plural Open' in page.locator('#mainCanvas').inner_text()
   page.locator('.nav-ask').click()
   page.locator('#askQuestion').fill('What housing legislation is recorded in Georgia?')
   page.locator('#askSubmit').click()
   page.wait_for_timeout(150)
   assert 'Sample state housing bill (TEST ONLY)' in page.locator('#askAnswer').inner_text()
   assert not errors,errors
   print(f'V9 synthetic state legislation browser check passed {width}x{height}')
   page.close()
  browser.close()

if __name__=='__main__':run()
