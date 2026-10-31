"""Offline UI tests for legacy help IDs and unique-name migration fallback."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

MODULE=Path(__file__).resolve().parents[1]/'src'/'pw-agent-help-bridge.js'

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path="/usr/bin/chromium",headless=True,args=['--no-sandbox'])
    page=await browser.new_page(viewport={'width':390,'height':700})
    await page.goto('about:blank')
    await page.set_content('<div id="agentLayer"><div class="agent" data-id="merged-gunnar"><span class="agent-name">Gunnar</span></div></div>')
    await page.evaluate('''() => {
      window.log=[];
      window.rows={cases:[],staff:[]};
      window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'hacker-toolkit',project:{live:true,agents:[{id:'merged-gunnar',name:'Gunnar'}]},getAgent:id=>({id,name:'Gunnar'})},ui:{selectAgent:id=>log.push(['DRAWER',id])}};
      window.pixelWorksApi=async path=>{
        log.push(['GET',path]);
        if(path.includes('/help'))return {cases:rows.cases};
        if(path.includes('/staff'))return {staff:rows.staff};
        throw new Error('unexpected route');
      };
      window.pixelWorksHelpLive=async (slug,id)=>log.push(['HELP',slug,id]);
      window.pixelWorksTalkLive=async (slug,id)=>log.push(['TALK',slug,id]);
      window.pixelWorksOpenDecisionContext=opts=>log.push(['INBOX',opts]);
    }''')
    await page.add_script_tag(path=str(MODULE))
    # Former department ID still attached to a valid help report.
    await page.evaluate('''async () => {
      rows.cases=[{id:'a123456789ab',agent_id:'old-qa-gunnar',agent_name:'Gunnar',state:'failed'}];
      await window.pixelWorksTalkOrHelpLive('hacker-toolkit','merged-gunnar',{name:'Gunnar'});
    }''')
    result=await page.evaluate('log')
    assert result[-1]==['HELP','hacker-toolkit','old-qa-gunnar'],result
    assert not any(x[0]=='TALK' for x in result),result
    # No help exists: reconcile current staff by unique name instead of unknown employee.
    await page.evaluate('''async () => {
      log.length=0;rows.cases=[];rows.staff=[{id:'current-gunnar',name:'Gunnar'}];
      await window.pixelWorksTalkOrHelpLive('hacker-toolkit','merged-gunnar',{name:'Gunnar'});
    }''')
    result=await page.evaluate('log')
    assert result[-1]==['TALK','hacker-toolkit','current-gunnar'],result
    # Duplicate report names must not silently send the user to a random case.
    await page.evaluate('''async () => {
      log.length=0;rows.cases=[{id:'report-1',agent_id:'older-g',agent_name:'Gunnar'},
                         {id:'report-2',agent_id:'old-g',agent_name:'Gunnar'}];
      await window.pixelWorksTalkOrHelpLive('hacker-toolkit','merged-gunnar',{name:'Gunnar'});
    }''')
    assert await page.locator('#pwAgentIdentityNotice').is_visible()
    result=await page.evaluate('log')
    assert not any(x[0] in ('HELP','TALK') for x in result),result
    await page.locator('#pwAgentIdentityNotice button').first.click()
    result=await page.evaluate('log')
    assert result[-1][0]=='INBOX',result
    # Clicking a migrated employee resolves their real old help report.
    await page.evaluate('''() => {
      log.length=0;rows.cases=[{id:'a123456789ab',agent_id:'old-qa-gunnar',agent_name:'Gunnar',state:'failed'}];
    }''')
    await page.locator('#agentLayer .agent').click()
    await page.wait_for_function('log.some(x=>x[0]==="HELP")')
    result=await page.evaluate('log')
    assert ['HELP','hacker-toolkit','old-qa-gunnar'] in result,result
    assert not any(x[0]=='DRAWER' for x in result),result
    # Clicking an agent without a help case still opens their normal agent drawer.
    await page.evaluate('''() => {log.length=0;rows.cases=[];}''')
    await page.locator('#agentLayer .agent').click()
    await page.wait_for_function('log.some(x=>x[0]==="DRAWER")')
    assert (await page.evaluate('log'))[-1]==['DRAWER','merged-gunnar']
    # Cross-project calls may not reach the old project's report.
    await page.evaluate('''async () => {
      log.length=0;
      await window.pixelWorksTalkOrHelpLive('another-project','merged-gunnar',{name:'Gunnar'});
    }''')
    assert await page.evaluate('log')==[]
    # No matches: clear non-destructive diagnostics instead of fake identity.
    await page.evaluate('''async () => {
      log.length=0;rows.cases=[];rows.staff=[];
      await window.pixelWorksTalkOrHelpLive('hacker-toolkit','merged-gunnar',{name:'Gunnar'});
    }''')
    assert 'Personalkopplingen' in (await page.locator('#pwAgentIdentityNotice h2').inner_text())
    assert await page.evaluate('log.at(-1)?.[0]')=='GET'
    await browser.close()
    print('7 identity scenarios passed: legacy help, roster, duplicate, sprite help/normal, isolation, diagnostic.')

asyncio.run(main())
