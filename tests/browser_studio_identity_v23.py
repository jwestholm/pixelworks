"""Offline regressions for shared studio: no unsafe person/name merging."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

JS = Path(__file__).resolve().parents[1] / 'src' / 'pw-agent-help-bridge.js'

async def main():
 async with async_playwright() as p:
  browser = await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page = await browser.new_page(viewport={'width':390,'height':800})
  await page.goto('about:blank')
  await page.set_content('''
   <select id="projectSelect"><option value="hack">Hackertoolkit</option><option value="pussel">Pussel</option></select>
   <div id="agentLayer"><button class="agent" data-id="gunnar-hack">Gunnar</button></div>
   <dialog id="pw13Dialog"><div class="pw13-shell"><h2>Min studio</h2><div class="pw13-projects"></div><div class="pw13-staff"></div></div></dialog>
  ''')
  await page.evaluate('''() => {
    window.logs=[];
    window.studio={project_count:2,staff_count:2,projects:[{id:'hack',name:'Hackertoolkit'},{id:'pussel',name:'Pussel'}],
      staff:[{studio_id:'pw-aaaaaaaaaaaaaaaaaaaa',agent_id:'gunnar-hack',name:'Gunnar',project_id:'hack',project_name:'Hackertoolkit'},
      {studio_id:'pw-bbbbbbbbbbbbbbbbbbbb',agent_id:'gunnar-pussel',name:'Gunnar',project_id:'pussel',project_name:'Pussel'}]};
    window.byProject={hack:[{id:'aaaaaaaaaaaa',agent_id:'gunnar-hack',agent_name:'Gunnar',state:'failed',friendly_reason:'Gunnar fick Git-konflikt.'}],
      pussel:[{id:'bbbbbbbbbbbb',agent_id:'gunnar-pussel',agent_name:'Gunnar',state:'review',friendly_reason:'Ändringen behöver granskas.'}]};
    window.rosterHack=[{id:'gunnar-hack',name:'Gunnar'}];
    window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'hack',project:{live:true,agents:[{id:'gunnar-hack',name:'Gunnar'}]},
      getAgent:id=>id==='gunnar-hack'?{id,name:'Gunnar'}:null},ui:{selectAgent:id=>logs.push(['DRAWER',id])}};
    window.pixelWorksApi=async url=>{
      if(url==='/api/pw-v013/studio')return studio;
      if(url==='/api/projects/hack/help')return {cases:byProject.hack};
      if(url==='/api/projects/pussel/help')return {cases:byProject.pussel};
      if(url==='/api/projects/hack/staff')return {staff:rosterHack};
      throw Error('unexpected '+url);
    };
    window.pixelWorksHelpLive=async (slug,id)=>logs.push(['HELP',slug,id]);
    window.pixelWorksTalkLive=async (slug,id)=>logs.push(['TALK',slug,id]);
    window.pixelWorksOpenDecisionContext=opts=>logs.push(['INBOX',opts]);
  }''')
  await page.add_script_tag(path=str(JS))
  await page.locator('#pw13Dialog').evaluate('(el)=>el.showModal()')
  await page.wait_for_selector('#pw13Dialog .pw23-studio-links button')
  await page.locator('#pw13Dialog .pw23-studio-links button').click()
  await page.wait_for_selector('#pw23HelpDialog .pw23-card')
  assert await page.locator('#pw23HelpDialog .pw23-card').count()==2
  assert 'Pussel' in await page.locator('#pw23HelpDialog').inner_text()
  assert 'Hackertoolkit' in await page.locator('#pw23HelpDialog').inner_text()
  assert 'namn' in (await page.locator('#pw23HelpDialog').inner_text()).lower()
  # Only explicit player choice may act on a case, and originating project is retained.
  assert await page.evaluate('logs')==[]
  await page.locator('#pw23HelpDialog .pw23-card').filter(has_text='Pussel').get_by_role('button').click()
  assert (await page.evaluate('logs'))[-1]==['HELP','pussel','gunnar-pussel']
  # An exact local ID is a safe direct route.
  await page.locator('#agentLayer .agent').click()
  await page.wait_for_function('logs.some(x=>x[0]==="HELP"&&x[1]==="hack")')
  assert ['HELP','hack','gunnar-hack'] in await page.evaluate('logs')
  # Legacy report using a different ID must NEVER be silently tied by name.
  await page.evaluate('''() => { logs.length=0;byProject.hack=[{id:'cccccccccccc',agent_id:'legacy-gunnar',agent_name:'Gunnar',state:'failed'}];}''')
  await page.locator('#agentLayer .agent').click()
  await page.wait_for_selector('#pw23HelpDialog[open] .pw23-card')
  assert await page.evaluate('logs')==[]
  assert await page.locator('#pw23HelpDialog .pw23-card').count()==2
  # Old report must still be reachable by explicit choice.
  await page.locator('#pw23HelpDialog .pw23-card').filter(has_text='Hackertoolkit').get_by_role('button').click()
  assert (await page.evaluate('logs'))[-1]==['HELP','hack','legacy-gunnar']
  # No help and current real ID: normal talk without losing the person.
  await page.evaluate('''() => { logs.length=0;byProject.hack=[];byProject.pussel=[]; }''')
  await page.locator('#agentLayer .agent').click()
  await page.wait_for_function('logs.some(x=>x[0]==="TALK")')
  assert (await page.evaluate('logs'))[-1]==['TALK','hack','gunnar-hack']
  # A missing project-local ID with same name is NOT enough to reroute.
  await page.evaluate('''() => {logs.length=0;rosterHack=[{id:'new-other',name:'Gunnar'}];}''')
  await page.locator('#agentLayer .agent').click()
  await page.wait_for_selector('#pw23HelpDialog[open]')
  assert 'Personalposten' in await page.locator('#pw23HelpDialog h2').inner_text()
  assert not await page.evaluate('logs')
  # Partial retrieval failure is never reported as "no cases" without warning.
  await page.evaluate('''() => {window.pixelWorksApi=async url=>{
    if(url==='/api/pw-v013/studio')return studio;
    if(url==='/api/projects/pussel/help')throw Error('offline');
    if(url==='/api/projects/hack/help')return {cases:byProject.hack};
    if(url==='/api/projects/hack/staff')return {staff:rosterHack};
    throw Error('unexpected')};}''')
  await page.evaluate('pixelWorksStudioHelpAll()')
  await page.wait_for_function('document.querySelector("#pw23HelpDialog")?.textContent.includes("projekt kunde inte läsas")')
  assert 'ofullständig' in await page.locator('#pw23HelpDialog').inner_text()
  assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
  await browser.close()
  print('7 cross-project identity/help scenarios passed, including mobile, no name guessing and partial errors.')

asyncio.run(main())
