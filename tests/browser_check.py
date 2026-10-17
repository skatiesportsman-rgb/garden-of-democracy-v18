import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
static=root/'site'
data={key:json.loads((static/'data'/key).read_text()) for key in ['snapshot.json','states.json','usa_coastline.json','state_lines.json']}
js=(static/'app.js').read_text()
# Chromium in this sandbox blocks all navigations. Test via in-memory HTML+JS+CSS instead.
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for label,width,height in [('desktop',1440,900),('mobile',390,844)]:
  page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
  errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
  html=(static/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
  page.set_content(html.replace('</head>', '<style>'+((static/'style.css').read_text().split('\n',1)[1])+'</style></head>'))
  page.evaluate("""(payload)=>{window.fetch=(url)=>{let key=String(url).split('/').pop().split('?')[0];return payload[key]?Promise.resolve({ok:true,json:async()=>payload[key]}):Promise.reject(Error('Test: outside network disabled'))}}""",data)
  page.evaluate('(code)=>{(0,eval)(code)}',js)
  page.wait_for_timeout(2000)
  print(label,'title',page.title(),'data',page.locator('#canvasStatus').inner_text(),'errors',errors[:5])
  print('cards',page.locator('#recentCards .record-card').count())
  if os.environ.get('GARDEN_CAPTURE')=='1':page.screenshot(path=str(root/'docs'/f'{label}-preview.png'),full_page=True,animations='disabled',timeout=7000)
  page.locator('.nav[data-view="polls"]').click()
  print('polls',page.locator('.poll-tile').count())
  assert page.locator('.poll-tile').count()==10
  page.locator('.poll-tile').first.click()
  print('detail',page.locator('#detailTitle').inner_text(),'errors',errors[:5])
  page.locator('.nav[data-view="sources"]').click()
  print('sources',page.locator('.source-row').count())
  page.locator('.nav[data-view="debates"]').click()
  print('debates',page.locator('.source-row').count())
  page.locator('.nav[data-view="issues"]').click()
  print('issues',page.locator('.issue-card').count())
  page.locator('#audioToggle').click();print('audio',page.locator('#audioBadge').inner_text())
  page.locator('#studioToggle').click();page.locator('#themeSelect').select_option('bio')
  print('theme',page.locator('body').get_attribute('class'))
  assert not errors,errors
  page.close()
 browser.close()
