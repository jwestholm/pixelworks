"""0.13.6 GUI regression: fewer panels, actions remain available. Simulated API only."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

JS=Path(__file__).resolve().parents[1]/'src'/'pw-v013.js'

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1280,'height':840})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content('''<!doctype html><html><body class="live-project"><header><div class="brand-title"><span class="version"></span></div><nav id="gameDock"></nav></header><div class="right-rail" style="width:260px">
    <div id="pw17-projectbar">AKTIVT PROJEKT Pussel</div>
    <div id="pw17-access">✅ Studioarbete tillåtet</div>
    <div id="pw17-decisions"><h3>Arbete och beslut</h3><div>2 att granska</div><button id="approve">Granska Greta</button><button id="retry">Försök igen</button></div>
    <details id="pw117Stats"><summary>📊 Studiostatistik</summary>Verklig statistik</details>
    <details id="pw-people-state"><summary>👥 Personal</summary>Namn</details>
    <section id="pw116Activity"><h3>Studions aktiviteter</h3><div>Gunnar arbetar med koden</div></section>
    </div><section id="officeStage"></section></body></html>''')
  await page.evaluate('''() => {
   window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'pussel',project:{live:true},projects:[{id:'pussel',title:'Pussel'}]}};
   window.clicked=[];document.querySelector('#approve').onclick=()=>clicked.push('approve');document.querySelector('#retry').onclick=()=>clicked.push('retry');
   window.orderState={project:'pussel',orders:[
      {id:'1',title:'Skapa spelvärlden',station:'docs',state:'handoff',assignee:'Greta',reason:'Färdigt designutkast'},
      {id:'2',title:'Programmera spelet',station:'code',state:'running',assignee:'Gunnar',reason:'Arbetar'}],draft_plans:[]};
   window.pixelWorksApi=async(path,data)=>{
    if(path==='/api/pw-v013/studio')return {version:'0.13.6',projects:[{id:'pussel',name:'Pussel'}],staff:[],staff_count:0,project_count:1,shared:true};
    if(path.startsWith('/api/pw-v0133/production'))return window.orderState;
    if(path.startsWith('/api/pw-v0134/bootstrap'))return {project:'pussel',playable:true,can_bootstrap:false};
    return {};
   };
  }''')
  await page.add_script_tag(path=str(JS))
  await page.wait_for_timeout(2200)
  assert 'v0.13.7' in (await page.locator('.version').inner_text())
  for sel in ('#pw17-projectbar','#pw117Stats','#pw-people-state','#pw17-access'):
   assert not await page.locator(sel).is_visible(),sel
  assert await page.locator('#pw116Activity').is_visible(), 'Activity should remain visible'
  assert await page.locator('#pw13-summary').count()==0, 'No redundant studio box'
  assert await page.locator('#pw13StudioNav').count()==1, 'Min studio remains reachable'
  assert await page.locator('#pw13Production').is_visible()
  detail=page.locator('#pw13Production details')
  assert not await detail.evaluate('(e)=>e.open'), 'Production details should be collapsed initially'
  assert '1 arbetar' in await page.locator('#pw13Production summary').inner_text()
  assert not await page.get_by_text('Programmera spelet',exact=True).is_visible()
  await page.locator('#pw13Production summary').click()
  assert await page.get_by_text('Programmera spelet',exact=True).is_visible()
  assert await page.locator('#pw17-decisions #approve').is_visible()
  assert not await page.locator('#pw17-decisions #retry').is_visible(), 'Less urgent action should be folded'
  await page.locator('#pw17-decisions .pw13-more-decisions summary').click()
  assert await page.locator('#pw17-decisions #retry').is_visible()
  await page.locator('#pw17-decisions #retry').click()
  assert await page.evaluate('window.clicked')==['retry']
  # Poll of original UI should not lose the first actionable button.
  await page.locator('#pw17-decisions').evaluate('e=>{e.innerHTML="<h3>Arbete och beslut</h3><div>0 att granska · 0 väntar</div><p>☕ Inget behöver beslutas just nu.</p>"}')
  await page.wait_for_timeout(1700)
  assert not await page.locator('#pw17-decisions').is_visible(), 'Idle decisions should not take space'
  # Revoking access must restore the real consent prompt.
  await page.locator('#pw17-access').evaluate('e=>{e.textContent="🔒 Studioarbete är inte aktiverat"}')
  await page.wait_for_timeout(1700)
  assert await page.locator('#pw17-access').is_visible(), 'Missing consent must be visible'
  # No job: empty production box gone.
  await page.evaluate("window.orderState={project:'pussel',orders:[],draft_plans:[]}")
  await page.evaluate("window.dispatchEvent(new Event('pixelworks:project-changed'))")
  await page.wait_for_timeout(900)
  assert not await page.locator('#pw13Production').is_visible(), 'No persistent empty production panel'
  assert not errors,errors
  screenshot=Path(__file__).resolve().parent/'simple_rail.png';await page.screenshot(path=str(screenshot))
  await browser.close()
  print('PASS: compact HUD, actions, access warnings, no idle duplication, scripts clean')

if __name__=='__main__':asyncio.run(main())
