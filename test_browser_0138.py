"""UI interaction smoke. All provider replies are explicitly simulated in browser tests."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
BASE=Path(__file__).resolve().parent
JS=str(BASE/'src/pw-v0121118.js')

async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1180,'height':900})
  errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
  await page.route('**/assets/office-v2/**',lambda r:r.fulfill(path=str(BASE.parent/'pw0137_audit/stage/assets/office-v2'/r.request.url.rsplit('/',1)[-1]),content_type='image/png'))
  await page.set_content('''<!doctype html><html><head><base href="http://127.0.0.1:8765/"></head><body class="live-project" style="background:#bda987"><div id="officeStage"><div id="stationLayer"><button class="station" data-id="cafe" style="padding:20px">Fikarummet</button><button class="station" data-id="code" style="padding:20px">Programmering</button></div></div><select id="projectSelect"><option value="pussel">Pussel</option></select><nav id="gameDock"><button id="pw13StudioNav">Min studio</button></nav><div class="brand-title"><span class="version"></span></div></body></html>''')
  await page.evaluate('''() => {
   window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'pussel'}};
   window.__cafePosts=0;window.__cafeGets=0;
   window.pixelWorksApi=async(url,payload)=>{
    if(url.includes('/api/pw-v0138/cafe')){
      if(payload){window.__cafePosts++;return {created:true,session:{id:'0123456789ab',project:'pussel',title:'Prata om spelet',topic:'talk',state:'running',participants:[{name:'Greta',role:'Designer'},{name:'Gunnar',role:'Programmerare'}],turns:[],work_orders:[]}};}
      if(url.includes('session=')){
       window.__cafeGets++;
       return {session:{id:'0123456789ab',project:'pussel',title:'Prata om spelet',topic:'talk',state:'done',participants:[{name:'Greta',role:'Designer'},{name:'Gunnar',role:'Programmerare'}],turns:[{name:'Greta',text:'Jag tycker att vi borde få ett bättre intro.',round:1,source:'real_ai_response'},{name:'Gunnar',text:'Bra idé, Greta! Vi kan skapa ett intro i HTML5.',round:1,source:'real_ai_response'}],work_orders:['abc']}};
      }
      return {project:'pussel',history:[],colleagues:[{name:'Greta'}],topics:[]};
    }
    return {orders:[]};
   };
   window.pixelWorksStationOrders=()=>{};
  }''')
  await page.add_script_tag(path=JS)
  await page.locator('.station[data-id="cafe"]').click()
  assert await page.locator('#pw138Cafe').is_visible()
  assert 'Fikarummet' in await page.locator('#pw138Cafe h2').inner_text()
  assert await page.locator('#pw138Cafe .pw138-choice').count()==5
  await page.locator('#pw138Cafe [data-topic="talk"]').click()
  await page.wait_for_timeout(2700)
  assert await page.evaluate('window.__cafePosts')==1
  assert await page.evaluate('window.__cafeGets')>=1
  assert 'Jag tycker att vi borde få ett bättre intro' in await page.locator('#pw138Cafe').inner_text()
  assert 'Bra idé, Greta!' in await page.locator('#pw138Cafe').inner_text()
  assert '1 riktiga arbetsordrar' in await page.locator('#pw138Cafe').inner_text()
  assert not errors,errors
  await page.locator('#pw138Cafe').screenshot(path=str(BASE/'cafe_discussion_test.png'))
  assert await page.locator('#pw138CafeMarker').is_visible()
  await page.locator('#pw138Cafe [data-cafe="new"]').click()
  assert await page.locator('#pw138Cafe .pw138-choice').count()==5
  await page.locator('#pw138Cafe [data-cafe="close"]').last.click()
  assert not await page.locator('#pw138Cafe').is_visible()
  await page.locator('.station[data-id="code"]').click()
  assert await page.locator('#pw18Desk').is_visible()
  await browser.close()
  print('PASS: cafe separate from lead, topic starts one provider session, genuinely attributed messages shown, returns to desk flows')

if __name__=='__main__':asyncio.run(run())
