"""0.13.5 production UI smoke, simulated API; no real provider requests."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
JS=str(Path(__file__).parent/'src'/'pw-v013.js')

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await browser.new_page()
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content('<html><body><header><div class="brand-title">Pixel Works <span class="version"></span></div><nav id="gameDock"></nav></header><div class="right-rail"><div id="pw17-decisions">Arbete och beslut</div></div><section id="officeStage"></section></body></html>')
  await page.evaluate('''() => {
   window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'pussel',project:{live:true},projects:[{id:'pussel',title:'Pussel'}]}};
   window.pixelWorksApi=async(path,data)=>{
    if(path==='/api/pw-v013/studio')return {version:'0.13.5',projects:[{id:'pussel',name:'Pussel'}],staff:[],staff_count:0,project_count:1,shared:true};
    if(path.startsWith('/api/pw-v0133/production'))return {project:'pussel',flow_mode:'automatiskt',orders:[
     {id:'1',title:'Designa pussel','station':'docs',state:'handoff',assignee:'Greta',reason:'Designunderlag skickat vidare; valfri granskning.'},
     {id:'2',title:'Bygg pussel','station':'code',state:'ready',assignee:'Gunnar',reason:''},
     {id:'3',title:'Testa pussel','station':'qa',state:'dependency',assignee:'Gunnar',reason:'Väntar på kod'}],draft_plans:[]};
    if(path.startsWith('/api/pw-v0134/bootstrap'))return {project:'pussel',playable:true,can_bootstrap:false};
    return {};
   };
  }''')
  await page.add_script_tag(path=JS)
  await page.wait_for_timeout(1800)
  assert '0.13.5' in await page.locator('.version').inner_text()
  rail=await page.locator('#pw13Production').inner_text()
  assert 'Automatiskt arbetsflöde' in rail,rail
  assert 'Designunderlag lämnat vidare' in rail,rail
  assert 'Bygg pussel' in rail,rail
  assert await page.get_by_role('button',name='Granska produktionsplan').count()==0
  assert not errors,errors
  await browser.close()
  print('PASS: studio production automatic, handoff status, no extra review button, JS error-free')

if __name__=='__main__':asyncio.run(main())
