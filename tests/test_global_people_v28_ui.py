import pathlib, asyncio, json
from playwright.async_api import async_playwright
root=pathlib.Path(__file__).resolve().parents[1]
people=[]
for i in range(15):
 project=['hackertoolkit','sjutbanan','pussel','mine'][i%4]
 people.append({'studio_id':f'pw-{i:020x}','agent_id':f'codex-{i}','name':'Gunnar' if i in (0,6,9) else f'Kund {i}', 'role':'Programmerare','role_type':'programmer','provider':'codex','project_id':project,'project_name':project,'station':'code','busy':False})
projects=[{'id':x,'name':x} for x in ['hackertoolkit','sjutbanan','pussel','mine']]
html='''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>
<button data-dock="agents" id="agentsNav">Agenter</button><button id="hireBtn">Personal</button><button id="officeHire">Personal-skylt</button><button id="localStudioBtn">Lokal studio</button><button id="pw13StudioNav">Min studio</button>
<button id="focusGame">Byt spel</button><p id="gameName">Hackertoolkit</p>
<dialog id="localStudioDialog"><button class="hireLocal" data-id="sjutbanan">Personal i Skjutbanan</button></dialog>
<dialog id="pw13Dialog"></dialog>
<script>
window.oldOpens=0; window.apiWrites=0; window.workforceActive=false;
window.__PIXEL_WORKS_DEMO__={model:{project:{live:true},activeProjectId:'hackertoolkit'},ui:{toast:msg=>{window.lastToast=msg}}};
window.persons='''+json.dumps(people)+'''; window.projs='''+json.dumps(projects)+''';
window.pixelWorksHireLive=()=>{window.oldOpens++};
window.pixelWorksRefreshLive=async()=>{};
window.pixelWorksApi=async(p,data)=>{
 if(data)window.apiWrites++;
 if(p==='/api/pw-v013/studio')return {staff:window.persons,projects:window.projs,shared:true};
 if(p==='/api/pw-v027/workforce')return {registered:true,active:window.workforceActive,people:window.persons,projects:window.projs,count:15};
 if(p==='/api/pw-v025/global-staff')return {registered:true,people_count:15,projects:window.projs,staff:window.persons,needs_reconciliation:false};
 if(p.endsWith('/activate')){window.workforceActive=true;return {active:true,count:15,people:window.persons,projects:window.projs}};
 if(p.includes('/hire'))return {agent:{id:'test'}};
 throw Error('API unknown '+p);
};
function openOld(){
 const d=document.querySelector('#pw13Dialog'); const roster=window.persons.map(p=>
 `<article class="pw13-card" id="pw13-card-${p.studio_id}"><strong>${p.name}</strong><small>${p.role} · Ledig · ${p.project_name}</small><div class="pw13-assignment"><button class="gameJump">🎮 Visa spelet</button><select><option>${p.project_name}</option></select><button class="assign">↗ Tilldela</button></div></article>`).join('');
 d.innerHTML=`<div class="pw13-shell"><header class="pw13-head"><h2>Välkommen till Pixel Works</h2></header><p>Gamla projektbundna kontor</p><h3>🎮 Projekt</h3><div class="pw13-projects"><button>Byt till Skjutbanan</button></div><h3>Personalen</h3><div class="pw13-staff">${roster}</div></div>`;
 if(!d.open)d.showModal();
}
document.querySelector('#pw13StudioNav').addEventListener('click',openOld);
document.querySelector('#agentsNav').addEventListener('click',()=>window.oldOpens++);
document.querySelector('#hireBtn').addEventListener('click',()=>window.oldOpens++);
document.querySelector('#officeHire').addEventListener('click',()=>window.oldOpens++);
document.querySelector('.hireLocal').addEventListener('click',()=>window.oldOpens++);
document.querySelector('#focusGame').addEventListener('click',()=>{document.querySelector('#gameName').textContent='Skjutbanan';window.__PIXEL_WORKS_DEMO__.model.activeProjectId='sjutbanan'});
</script>
<script src="pw-studio-roster-v24.js"></script>
<script src="pw-global-workforce-v27.js"></script>
<script src="pw-global-people-v28.js"></script>
</body></html>'''
html=html.split('<script src=')[0]+'</body></html>'
# The fixture remains in memory; project data is never written
async def run():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for size in [{'width':1366,'height':768},{'width':390,'height':844}]:
   page=await browser.new_page(viewport=size)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(html)
   for f in ['pw-studio-roster-v24.js','pw-global-workforce-v27.js','pw-global-people-v28.js']:
    await page.add_script_tag(content=(root/'src'/f).read_text())
   await page.click('[data-dock="agents"]')
   await page.wait_for_selector('#pw13Dialog[open] #pw28PeopleHeader')
   await page.wait_for_function("document.querySelector('#pw13Dialog .pw28-global-banner').textContent.includes('AKTIVERING ÅTERSTÅR')")
   assert await page.evaluate('window.oldOpens')==0
   assert await page.locator('#pw13Dialog .pw13-card').count()==15
   assert await page.locator('#pw13Dialog .pw13-card:visible').count()==15
   assert await page.locator('#pw13Dialog .pw13-projects').evaluate('(el)=>getComputedStyle(el).display')=='none'
   assert not await page.locator('#pw13Dialog .pw28-recruit').is_enabled()
   assert not await page.locator('#pw13Dialog .assign').first.is_enabled()
   assert await page.evaluate('window.apiWrites')==0
   assert await page.locator('#pw24-project').input_value()=='all'
   assert await page.locator('#gameName').inner_text()=='Hackertoolkit'
   await page.click('#pw28PeopleHeader .pw28-activate')
   await page.wait_for_selector('#pw27Confirm[open]')
   await page.click('#pw27Confirm button:first-of-type')
   await page.wait_for_function('window.workforceActive')
   # On v27 source UI, activation refresh should update the panel asynchronously.
   await page.locator('#pw13Dialog').evaluate('(el)=>el.close()')
   await page.click('#hireBtn')
   await page.wait_for_function("document.querySelector('#pw13Dialog .pw28-global-banner')?.textContent.includes('AKTIV')")
   assert await page.locator('#pw13Dialog .pw13-card:visible').count()==15
   assert await page.locator('#gameName').inner_text()=='Hackertoolkit'
   await page.locator('#pw24-project').select_option('sjutbanan')
   assert await page.locator('#pw13Dialog .pw13-card:visible').count() < 15
   await page.locator('#pw13Dialog').evaluate('(el)=>el.close()')
   await page.click('#focusGame')
   await page.click('#officeHire')
   await page.wait_for_function("document.querySelector('#pw24-project')?.value==='all'")
   assert await page.locator('#pw13Dialog .pw13-card:visible').count()==15
   assert await page.locator('#gameName').inner_text()=='Skjutbanan'
   assert await page.evaluate('window.oldOpens')==0
   assert await page.locator('#pw13Dialog .pw28-recruit').is_enabled()
   assert await page.locator('#pw13Dialog .assign').first.is_enabled()
   assert await page.evaluate('window.apiWrites')==1
   await page.locator('#pw13Dialog .pw28-recruit').click()
   await page.wait_for_selector('#pw28Recruit[open]')
   await page.wait_for_function("document.querySelectorAll('#pw28HireProject option').length===4")
   await page.locator('#pw28Recruit input').fill('Karin')
   await page.locator('#pw28Recruit button').first.click()
   assert await page.evaluate('window.apiWrites')==2
   assert not errors, errors
   print('PASS',size, 'api writes',await page.evaluate('window.apiWrites'))
   await page.close()
  await browser.close()
if __name__=='__main__':asyncio.run(run())
