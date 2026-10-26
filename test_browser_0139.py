"""Simulated backend smoke: cafe owner messages, thumb feedback, manual work order.
Never calls real AI providers.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
BASE=Path(__file__).resolve().parent

async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1180,'height':900})
  errs=[];page.on('pageerror',lambda exc:errs.append(str(exc)))
  assetroot=BASE.parent/'pw0137_audit/stage/assets/office-v2'
  await page.route('**/assets/office-v2/**',lambda r:r.fulfill(path=str(assetroot/r.request.url.rsplit('/',1)[-1]),content_type='image/png'))
  await page.set_content('''<!doctype html><html><head><base href="http://127.0.0.1:8765/"></head><body class="live-project" style="background:#bda987"><div id="officeStage"><div id="stationLayer"><button class="station" data-id="cafe" style="padding:20px">Fikarummet</button><button class="station" data-id="code" style="padding:20px">Programmering</button></div></div><select id="projectSelect"><option value="pussel">Pussel</option></select><nav id="gameDock"><button id="pw13StudioNav">Min studio</button></nav><div class="brand-title"><span class="version"></span></div></body></html>''')
  await page.evaluate('''() => {
   window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'pussel'}};
   window.__backend={posts:[],gets:0,record:null};
   window.pixelWorksApi=async(url,body)=>{
     const m=window.__backend;
     if(url.includes('/api/pw-v0138/cafe')){
       if(body){
         m.posts.push(body);
         if(!body.action){
           m.record={id:'0123456789ab',project:'pussel',title:'Prata om spelet',topic:'talk',state:'running',
            participants:[{id:'greta',name:'Greta',role:'Designer'},{id:'gunnar',name:'Gunnar',role:'Programmerare'}],
            turns:[{name:'Du',source:'owner_message',text:body.note||'',round:0}],work_orders:[],reactions:{},followup_count:0};
           return {created:true,session:structuredClone(m.record)};
         }
         if(body.action==='reaction'){
           m.record.reactions[body.turn_index]=body.vote==='clear'?null:body.vote;
           return {created:false,session:structuredClone(m.record)};
         }
         if(body.action==='implement'){
           if(m.record.work_orders.length)return {created:false,session:structuredClone(m.record),order_id:'abc'};
           m.record.work_orders=['abc'];return {created:true,session:structuredClone(m.record),order_id:'abc'};
         }
         if(body.action==='message'){
           m.record.turns.push({name:'Du',source:'owner_message',text:body.message,round:3});
           m.record.followup_count++;
           m.record.state='running';
           m.record.turns.push({name:'Greta',source:'real_ai_response',text:'Jag svarar direkt på ditt inlägg.',round:3});
           m.record.turns.push({name:'Chefen',source:'real_ai_response',text:'Då planerar jag nästa steg.',round:3});
           m.record.state='done';
           return {created:true,session:structuredClone(m.record)};
         }
       }
       if(url.includes('session=')){
         m.gets++;
         m.record.state='done';
         if(m.record.turns.length===1){
            m.record.turns.push({name:'Greta',source:'real_ai_response',text:'Bra idé! Vi kan bygga ett intro.',round:1});
            m.record.turns.push({name:'Gunnar',source:'real_ai_response',text:'Jag kan göra en första kodversion.',round:1});
         }
         return {session:structuredClone(m.record)};
       }
       return {project:'pussel',history:[],active:null};
     }
     return {orders:[]};
   };
   window.pixelWorksStationOrders=()=>{};
  }''')
  await page.add_script_tag(path=str(BASE/'src/pw-v0121118.js'))
  await page.locator('.station[data-id="cafe"]').click()
  await page.locator('#pw138Note').fill('Jag vill ha ett pusselspel med fyra nivåer.')
  await page.locator('[data-topic="talk"]').click()
  await page.wait_for_timeout(2500)
  assert await page.locator('#pw138Cafe .pw139-owner').count()==1
  assert 'Du · Spelägaren' in await page.locator('#pw138Cafe .pw139-owner').inner_text()
  assert 'Jag vill ha ett pusselspel' in await page.locator('#pw138Cafe .pw139-owner').inner_text()
  assert not 'Riktigt AI-svar' in await page.locator('#pw138Cafe .pw139-owner').inner_text()
  assert await page.locator('#pw138Cafe [data-vote="up"]').count()==2
  await page.locator('#pw138Cafe [data-turn="1"][data-vote="up"]').click()
  assert await page.locator('#pw138Cafe [data-turn="1"][data-vote="up"]').get_attribute('aria-pressed')=='true'
  await page.locator('#pw138Cafe [data-idea="1"]').click()
  assert await page.locator('#pw139Station').count()==1
  await page.locator('#pw139Station').select_option('code')
  await page.locator('[data-order="1"]').click()
  assert 'Arbetsordern skapades' in await page.locator('#pw138Cafe').inner_text()
  assert await page.evaluate('window.__backend.record.work_orders.length')==1
  await page.locator('#pw139Owner').fill('Gunnar, gör första versionen så enkel som möjligt.')
  await page.locator('[data-cafe="speak"]').click()
  assert await page.locator('#pw138Cafe .pw139-owner').count()==2
  assert 'Gunnar, gör första versionen' in await page.locator('#pw138Cafe .pw139-owner').last.inner_text()
  assert 'Jag svarar direkt på ditt inlägg' in await page.locator('#pw138Cafe').inner_text()
  assert await page.evaluate("window.__backend.posts.filter(x=>x.action==='message').length") == 1
  assert not errs,errs
  await page.locator('#pw138Cafe').screenshot(path=str(BASE/'cafe_feedback_preview.png'))
  await browser.close()
  print('PASS: owner attributed correctly; thumbs; one manual work order; interactive follow-up; no JS errors')

if __name__=='__main__':asyncio.run(run())
