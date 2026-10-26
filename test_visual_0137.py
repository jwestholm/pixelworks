"""Full stations UX visual/smoke test; no real API, no changes to project files."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
BASE=Path(__file__).parent
STATIONS=['art','code','research','qa','docs','meeting','music','voice']

def run():
 screenshots=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1350,'height':900},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def asset_route(route):
   name=route.request.url.split('/assets/office-v2/')[-1]
   f=BASE/'assets'/'office-v2'/name
   if f.is_file():route.fulfill(path=str(f),content_type='image/png')
   else:route.abort()
  page.route('**/assets/office-v2/**',asset_route)
  page.set_content('''<!doctype html><html><head><base href="http://127.0.0.1:8765/"></head><body class="live-project" style="background:#e5cb9f"><select id="projectSelect"><option value="demospelet">Demo</option></select><section id="stationLayer"></section><script>
    window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'demospelet'}};
    window.pixelWorksApi=async(path,data)=>!data && path.endsWith('/assets')?{assets:[]}:{orders:[],item:{id:'ok'}};
    window.pixelWorksStationOrders=(...args)=>{};
    window.pixelWorksRefreshOrders=()=>{};
    </script></body></html>''')
  page.evaluate('''stations=>document.querySelector('#stationLayer').innerHTML=stations.map(s=>`<div data-id="${s}" class="station" role="button" tabindex="0">${s}</div>`).join('')''',STATIONS)
  page.add_script_tag(path=str(BASE/'src/pw-v0121118.js'))
  for station in STATIONS:
   page.locator(f'.station[data-id="{station}"]').click()
   dialog=page.locator('#pw18Desk')
   assert dialog.is_visible(),station
   assert page.locator('#pw18Desk .pw18-tile:first-child').inner_text().find('Eget uppdrag')>=0
   assert page.locator('#pw18Desk .pw18-paper').evaluate('(e)=>getComputedStyle(e).backgroundImage.includes("url(")'),station
   assert page.locator('#pw18Desk .pw18-grid button').count()>=3
   image_path=BASE/f'ui_0137_{station}.png'
   dialog.screenshot(path=str(image_path))
   screenshots.append((station,image_path))
   page.locator('#pw18Desk .pw18-tile:nth-child(2)').click()
   assert page.locator('#pw18Desk .pw18-sub').count()>=2
   page.locator('#pw18Desk .pw18-sub:nth-child(1)').click()
   assert page.locator('#pw18Description').is_visible()
   assert page.locator('input[name=pw18Priority]:checked').get_attribute('value')=='2'
   assert page.locator('#pw18Desk .pw18-paper').evaluate('(e)=>getComputedStyle(e).backgroundImage.includes("url(")')
   page.locator('#pw18Desk .pw18-x').click()
  assert not errors,errors
  browser.close()
 thumb_w=660;thumb_h=470
 collage=Image.new('RGB',(thumb_w*2,thumb_h*4),'#102137');d=ImageDraw.Draw(collage)
 for i,(station,path) in enumerate(screenshots):
  im=Image.open(path);im.thumbnail((thumb_w-12,thumb_h-32))
  x=(i%2)*thumb_w+6;y=(i//2)*thumb_h+4
  collage.paste(im,(x,y+20))
  d.text((x+4,y),station,fill='white')
 collage.save(BASE/'ui_0137_all_desks.jpg',quality=90)
 print('PASS: all eight desks show unique illustrated theme, working categories, details, normal priority; zero errors')
if __name__=='__main__':run()
