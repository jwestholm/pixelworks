"""DOM smoke for 0.13.4 plan editor; simulated APIs, no Codex/Gemini calls."""
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
   window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'mines',project:{live:true},projects:[{id:'mines',title:'Minesweeper'}]}};
   window.testPosts=[];
   const steps=[
    {id:'000000000001',title:'Grafik',station:'art',instruction:'Designa grafik som tydligt visar rutornas status.',priority:2,assigned_agent_id:'sofia',depends_on_order_ids:[],staff_choices:[{id:'sofia',name:'Sofia',role:'Grafiker'}]},
    {id:'000000000002',title:'Kod',station:'code',instruction:'Skapa riktig minröjarlogik för första banan.',priority:1,assigned_agent_id:'gunnar',depends_on_order_ids:['000000000001'],staff_choices:[{id:'gunnar',name:'Gunnar',role:'Programmerare'}]}
   ];
   window.pixelWorksApi=async(path,data)=>{
    if(path==='/api/pw-v013/studio')return {version:'0.13.4',projects:[{id:'mines',name:'Minesweeper'}],staff:[],staff_count:0,project_count:1,shared:true};
    if(path.startsWith('/api/pw-v0133/production'))return {project:'mines',orders:[
        {id:'000000000001',title:'Grafik',station:'art',state:'draft',assignee:'Sofia',reason:'Väntar på planbeslut'},
        {id:'000000000002',title:'Kod',station:'code',state:'draft',assignee:'Gunnar',reason:'Väntar på planbeslut'}],
        draft_plans:[{id:'abcdef123456',project:'mines',revision:0,summary:'Plan',steps}]};
    if(path.startsWith('/api/pw-v0134/bootstrap'))return {project:'mines',playable:true,can_bootstrap:false};
    if(data){window.testPosts.push([path,data]);return {message:'Planen godkänd',released:path.endsWith('/release'),revision:1}}
    return {};
   }
  }''')
  await page.add_script_tag(path=JS)
  await page.wait_for_timeout(1650)
  assert 'v0.13.4' in await page.locator('.version').inner_text()
  btn=page.get_by_role('button',name='Granska produktionsplan')
  await btn.click()
  modal=page.locator('#pw13PlanEditor')
  assert await modal.is_visible()
  assert await modal.locator('[data-plan-step]').count()==2
  await modal.locator('[data-edit-title]').first.fill('Designa spelets nya grafik')
  await modal.get_by_role('button',name='Spara utkast').click()
  await page.wait_for_timeout(100)
  posts=await page.evaluate('window.testPosts')
  assert posts and posts[0][0]=='/api/pw-v0133/plan/save',posts
  assert posts[0][1]['steps'][0]['title']=='Designa spelets nya grafik',posts
  # Simulator returns revision 0 after GET: do not assert production persistence.
  assert not errors,errors
  await browser.close()
  print('PASS: 0.13.4 plan editor, two steps, saved text, scoped API, JS error-free')

if __name__=='__main__':asyncio.run(main())
