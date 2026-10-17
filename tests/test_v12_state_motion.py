import pytest
pytestmark=pytest.mark.skip(reason="V12 state-lock behavior intentionally removed at user request in V17; see test_v17_restored_map.py")
"""Geographic animation regression tests using synthetic rectangles strictly in-memory.

Rectangles are test geometry only. No invented political data or false boundaries
are ever written into the shipped website.
"""
from pathlib import Path
import base64,json

BASE=Path(__file__).resolve().parents[1]
SITE=BASE/'site'
FIPS=['01','02','04','05','06','08','09','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']

def test_topology_and_css_behavior():
    app=(SITE/'app.js').read_text()
    assert 'stateClipLayer(stems,code)' in app
    assert 'stateClipLayer(flowers,code)' in app
    assert 'stateClipLayer(parent,code)' in app
    assert 'clipPathUnits:\'userSpaceOnUse\'' in app
    assert 'flower-anchor' in app and 'mapLayerGroups.clear()' in app
    assert 'stateShape' in app
    assert 'fairMapPolls' in app
    assert 'national-only records remain' in app


def test_state_boundaries_browser():
    from playwright.sync_api import sync_playwright
    html=(SITE/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css">','').replace('<script type="module" src="./app.js"></script>','')
    css=(SITE/'style.css').read_text()
    css=css.replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap');",'')
    css=css.replace('./assets/cottage-meadow.svg','data:image/svg+xml;base64,'+base64.b64encode((SITE/'assets'/'cottage-meadow.svg').read_bytes()).decode())
    html=html.replace('</head>','<style>'+css+'</style></head>')
    js=(SITE/'garden-answer.js').read_text().replace('export const ','const ').replace('export function ','function ')+(SITE/'app.js').read_text().replace("import {askGarden} from './garden-answer.js';",'')
    payload={name:json.loads((SITE/'data'/name).read_text()) for name in ('snapshot.json','states.json')}
    # Synthetic border geometry (test only) for all 51 geographic entities.
    arcs=[];geometries=[]
    for i,fips in enumerate(FIPS):
        col=i%10;row=i//10;x=col*90;y=row*90
        arcs.append([[x,y],[78,0],[0,75],[-78,0],[0,-75]])
        geometries.append({'type':'Polygon','id':int(fips),'arcs':[[i]]})
    payload['states-albers-10m.json']={'type':'Topology','arcs':arcs,'objects':{'states':{'type':'GeometryCollection','geometries':geometries}}}
    # Sourced published records from existing fixture. No fabricated data is added.
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        for width,height in ((1440,900),(390,844)):
            page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='no-preference')
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(html,wait_until='domcontentloaded')
            page.evaluate('payload=>{window.fetch=(url)=>{let key=String(url).split("/").pop().split("?")[0];return payload[key]?Promise.resolve({ok:true,json:async()=>payload[key]}):Promise.reject(new Error("Test offline"))}}',payload)
            page.evaluate('code=>(0,eval)(code)',js)
            page.wait_for_function("document.querySelector('#canvasStatus')?.textContent.includes('accurate geographic clipping')",timeout=16000)
            result=page.evaluate('''() => {
              const svg=document.querySelector('#gardenMap');
              const clips=[...svg.querySelectorAll('clipPath[id^="garden-state-"]')];
              const anchors=[...svg.querySelectorAll('#mapFlowers .flower-anchor')];
              const badges=[...svg.querySelectorAll('#mapEvents [data-garden-state]')];
              const vines=[...svg.querySelectorAll('#mapStems .data-vine')];
              const records=[];
              for(const a of anchors){const layer=a.closest('[data-garden-state]');
                const match=a.getAttribute('transform').match(/translate\\(([^ ]+) ([^)]*)\\)/);
                const point=svg.createSVGPoint();point.x=Number(match[1]);point.y=Number(match[2]);
                const shape=document.querySelector('.us-state[data-state="'+layer.dataset.gardenState+'"]');
                records.push({state:layer.dataset.gardenState,inside:shape.isPointInFill(point),
                  hasClip:layer.getAttribute('clip-path')==='url(#garden-state-'+layer.dataset.gardenState+')',
                  centered:!!a.querySelector('.garden-flower')});
              }
              return {clipCount:clips.length,flowers:records,events:badges.length,vines:vines.length,
                status:document.querySelector('#canvasStatus').textContent,
                svgClipped:getComputedStyle(svg).overflow==='hidden'};
            }''')
            assert result['clipCount']==51,result
            assert result['flowers'] and all(r['inside'] and r['hasClip'] and r['centered'] for r in result['flowers']),result
            assert result['svgClipped']
            assert not errors,errors
            # Toggle a layer and verify a redraw cannot lose the state clip.
            page.locator('#layerPolls').uncheck()
            assert page.locator('#mapFlowers .garden-flower').count()==0
            page.locator('#layerPolls').check()
            assert page.locator('#mapFlowers [data-garden-state]').count()>0
            screenshot=BASE/'docs'/f'v12-geographic-garden-{width}.png'
            page.screenshot(path=str(screenshot),full_page=True)
            print(f'V12 {width}x{height}: {len(result["flowers"])} mapped poll flowers, {result["clipCount"]} jurisdiction clips; geographic anchor and layer controls verified')
            page.close()
        browser.close()
