"""Chromium DOM smoke of the new right-rail production panel, no real network."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

JS=str(Path(__file__).with_name('pw-v013.js'))

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
  page=await browser.new_page()
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  await page.set_content('<html><body><header><div class="brand-title">Pixel Works <span class="version"></span></div><nav id="gameDock"></nav></header><div class="right-rail"><div id="pw17-decisions">Arbete och beslut</div></div><section id="officeStage"></section></body></html>')
  await page.evaluate('''() => {
    window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'minesweeper',project:{live:false},projects:[{id:'minesweeper',title:'Minesweeper'}]}};
    window.testPosts=[];
    window.pixelWorksApi=async(path,data)=>{
      if(path.startsWith('/api/pw-v0133/production'))return {project:'minesweeper',orders:[
        {id:'1',title:'Designa grafiken',station:'art',state:'ready',assignee:'Sofia',reason:''},
        {id:'2',title:'Programmera spelet',station:'code',state:'dependency',assignee:'Gunnar',reason:'Väntar på att grafiken blir klar'}]};
      if(path==='/api/pw-v013/studio')return {version:'0.13.3',projects:[{id:'minesweeper',name:'Minesweeper'}],staff:[],staff_count:0,project_count:1,shared:false};
      if(data){window.testPosts.push([path,data]);return {created:true,message:'Arbete i kö'};}
      return {};
    };
  }''')
  await page.add_script_tag(path=JS)
  await page.wait_for_timeout(1600)
  text=await page.locator('#pw13Production').inner_text()
  assert 'Designa grafiken' in text and 'Programmera spelet' in text and 'Väntar på' in text, text
  assert 'v0.13.3' in await page.locator('.version').inner_text()
  assert not errors,errors
  # Replace the mocked production GET; confirm that an old report is routed to
  # the authenticated creation endpoint only after an explicit second click.
  await page.evaluate('''() => {
    const old=window.pixelWorksApi;
    window.pixelWorksApi=async(path,data)=>{
      if(path.startsWith('/api/pw-v0133/production'))return {project:'minesweeper',orders:[],
        last_lead_report:{id:'abcdef123456',title:'Chefens plan'},
        lead_reports:[{id:'abcdef123456',title:'Chefens plan',date:'2026-10-26'}]};
      return old(path,data);
    };
  }''')
  await page.evaluate('''() => window.dispatchEvent(new Event('pixelworks:project-changed'))''')
  await page.wait_for_timeout(500)
  button=page.get_by_role('button',name='Skapa uppdrag från senaste chefsrapporten')
  await button.click()
  assert len(await page.evaluate('window.testPosts'))==0
  await page.get_by_role('button',name='Bekräfta: ge Chefen').click()
  await page.wait_for_timeout(350)
  sent=await page.evaluate('window.testPosts')
  assert sent[0][0]=='/api/pw-v0133/from-report' and sent[0][1]['report_id']=='abcdef123456',sent
  await browser.close()
  print('PASS: production panel, report picker, double confirmation, no JS errors')

if __name__=='__main__':asyncio.run(main())
