"""Simulated browser contracts – no real AI requests or project filesystem changes."""
from playwright.sync_api import sync_playwright
from pathlib import Path
ROOT=Path(__file__).resolve().parent

PAGE='''<!doctype html><html lang="sv"><head><meta charset="utf-8"></head><body class="live-project">
<select id="projectSelect"><option value="gta-klonen">GTA Klonen</option><option value="fantasi">Fantasivarelser i Cyberpunk</option></select>
<button id="newProjectBtn">Nytt projekt</button>
<div id="dockDialogContent"></div><dialog id="dockDialog"></dialog>
<dialog id="gameDialog"><div id="gameDialogContent"></div></dialog>
<dialog id="localStudioDialog"><div class="local-shell-info">Lokal studio</div><div class="local-shell-body"></div></dialog>
<div class="right-rail"><div>Studioåtkomst behövs</div></div>
<div id="stationLayer"><div class="station" data-id="docs" tabindex="0" role="button"><div class="station-label">DOK</div></div><div class="station" data-id="code" tabindex="0" role="button"><div class="station-label">KOD</div></div></div>
<script>
 Object.defineProperty(window,'localStorage',{value:(()=>{const map=new Map();return {getItem:k=>map.get(k)||null,setItem:(k,v)=>map.set(k,String(v)),removeItem:k=>map.delete(k)};})(),configurable:true});
 window.calls=[];
 window.projectId='gta-klonen';
 window.mockAccess=false;
 window.mockProjects=[{id:'gta-klonen',title:'GTA Klonen',live:true},{id:'fantasi',title:'Fantasivarelser i Cyberpunk',live:true}];
 const model={projects:window.mockProjects,activeProjectId:'gta-klonen',
   switchProject(id){this.activeProjectId=id;document.querySelector('#projectSelect').value=id},
   setLiveStaff(){}};
 const ui={renderAll(){document.querySelector('#projectSelect').value=model.activeProjectId},toast(s){window.calls.push(['toast',s])}};
 window.__PIXEL_WORKS_DEMO__={model,ui};
 window.pixelWorksApplyLive=function(){const previous=model.activeProjectId;
    model.projects=window.mockProjects;model.activeProjectId=model.projects[0].id;
    if(model.projects.some(p=>p.id===previous))model.activeProjectId=previous;
    ui.renderAll();};
 window.pixelWorksApi=async(path,payload)=>{
    window.calls.push(['api',path,payload||null]);
    if(path==='/api/pw-v01210/studio-access'){
      if(payload){window.mockAccess=!!payload.enabled;return {enabled:window.mockAccess}};
      return {enabled:window.mockAccess};
    }
    if(path.startsWith('/api/projects/')&&path.endsWith('/orders'))return {orders:[{id:'aaaaaaaabbbb',station:'docs',status:'waiting'}]};
    if(path.startsWith('/api/projects/')&&path.endsWith('/reports'))return {reports:[{id:'eeeeeeeeffff',agent_name:'Greta',station:'docs',state:'review',source:'gemini-api',order_id:'bbbbbbbbcccc'}]};
    if(path.startsWith('/api/projects/')&&path.endsWith('/staff'))return {staff:[{id:'greta',name:'Greta',station:'docs'}]};
    if(path.startsWith('/api/projects/')&&path.endsWith('/jobs'))return {jobs:[]};
    if(path==='/api/projects'&&payload)return {verified:true,path:'/myroot/projects/'+payload.slug};
    if(path.startsWith('/api/projects/')&&!payload)return {verified:true,path:'/myroot/projects/'+path.split('/')[3],project:{id:path.split('/')[3]}};
    return {};
 };
 window.pixelWorksCreateLive=async()=>({});
 window.pixelWorksHireLive=async slug=>{window.calls.push(['hire',slug]);};
 window.pixelWorksGeminiReview=(slug,rid)=>window.calls.push(['review',slug,rid]);
 window.fetch=async (url,options)=>({ok:true,json:async()=>{
   if(url==='/api/pw-v01210/studio-access'){
     if(options?.method==='POST')window.mockAccess=!!JSON.parse(options.body).enabled;
     return {decided:true,enabled:window.mockAccess};
   }
   return {token:'fake',providers:{gemini:{configured:true,execution_enabled:true}}};
 }});
</script></body></html>'''

with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=browser.new_context()
 page=context.new_page();errors=[]
 page.on('pageerror',lambda exc: errors.append(str(exc)))
 page.set_content(PAGE)
 page.add_script_tag(path=str(ROOT/'src/pw-v01211.js'))
 page.wait_for_timeout(440)
 # Last-saved selection is startup-only. Never redirect on the next roster refresh.
 page.evaluate("window.__PIXEL_WORKS_DEMO__.model.switchProject('fantasi')")
 assert page.evaluate("localStorage.getItem('pixelworks.last-project.v01211')")=='fantasi'
 page.evaluate('window.pixelWorksApplyLive()')
 assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='fantasi'
 assert page.locator('#projectSelect').input_value()=='fantasi'
 page.add_script_tag(path=str(ROOT/'src/pw-v0121117.js'))
 page.wait_for_timeout(1300)
 assert page.locator('#stationLayer .station[data-id=docs] .station-label').inner_text()=='Dokumentation'
 assert 'Game Bible' in page.locator('#stationLayer .station[data-id=docs]').get_attribute('title')
 assert page.locator('#pw17-projectbar').inner_text().endswith('Fantasivarelser i Cyberpunk')
 assert page.locator('#pw17-decisions').get_by_text('1 att granska').count()>0
 assert page.locator('.pw17-stale-access').count()==1
 page.get_by_role('button',name='Granska Gretas förslag').click()
 assert page.evaluate('window.calls.filter(x=>x[0]==="review").slice(-1)[0]')==['review','fantasi','eeeeeeeeffff']
 # Grant consent exactly once, across projects.
 page.get_by_role('button',name='Aktivera studioarbete').click()
 assert page.locator('#pw11StudioConsent').evaluate('(e)=>e.open')
 page.locator('#pw11ConsentAllow').click()
 page.wait_for_timeout(200)
 assert page.evaluate('window.mockAccess')
 assert 'Studioarbete tillåtet' in page.locator('#pw17-access').inner_text()
 assert page.evaluate('window.mockAccess')
 # Stale project-specific POSTs must fail before reaching the backend.
 failed=page.evaluate("window.pixelWorksApi('/api/projects/gta-klonen/orders',{action:'write'}).then(()=>false,()=>true)")
 assert failed
 page.evaluate("window.__PIXEL_WORKS_DEMO__.model.switchProject('gta-klonen')")
 page.wait_for_timeout(200)
 assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='gta-klonen'
 page.evaluate('window.pixelWorksApplyLive()')
 assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='gta-klonen'
 # Creating a project with the old wizard path does not invoke a second browser confirm.
 page.evaluate('() => {window.confirm=()=>{throw Error("Unexpected recurring project confirmation")}}')
 saved=page.evaluate("window.pixelWorksCreateLive({name:'En Ny Värld',description:'Ett färdigt äventyr som vi utvecklar tillsammans.',creator:{gameGenre:['Äventyr']}})")
 assert saved['project']['id']=='en-ny-varld'
 # Wizard follows the actual production flow: refresh the roster, select the
 # newly created project, then present useful choices rather than raw hires.
 page.evaluate("""() => { window.mockProjects.unshift({id:'en-ny-varld',title:'En Ny Värld',live:true}); window.pixelWorksApplyLive(); window.__PIXEL_WORKS_DEMO__.model.switchProject('en-ny-varld'); window.__PIXEL_WORKS_DEMO__.ui.renderAll(); }""")
 page.evaluate("window.pixelWorksHireLive('en-ny-varld')")
 page.wait_for_timeout(230)
 assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='en-ny-varld'
 assert 'Ditt nya spel är skapat' in page.locator('#pw17-welcome').inner_text()
 assert not any(x[0]=='hire' and x[1]=='en-ny-varld' for x in page.evaluate('window.calls'))
 page.get_by_role('button',name='Gå till kontoret').click()
 page.evaluate('window.pixelWorksApplyLive()')
 assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='en-ny-varld'
 assert page.evaluate("localStorage.getItem('pixelworks.last-project.v01211')")=='en-ny-varld'
 # A stale decision dialog must close on an explicit project change.
 page.locator('#localStudioDialog').evaluate('(el) => el.showModal()')
 page.wait_for_timeout(80)
 assert 'En Ny Värld' in page.locator('#localStudioDialog .pw17-context').inner_text()
 page.evaluate("window.__PIXEL_WORKS_DEMO__.model.switchProject('fantasi')")
 page.wait_for_timeout(60)
 assert not page.locator('#localStudioDialog').evaluate('(el)=>el.open')
 assert errors==[],errors
 # Startup is the ONE allowed use of a saved project choice.
 second=context.new_page(); second.set_content(PAGE)
 second.evaluate("localStorage.setItem('pixelworks.last-project.v01211','fantasi')")
 second.add_script_tag(path=str(ROOT/'src/pw-v01211.js'))
 second.wait_for_timeout(450)
 assert second.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='fantasi'
 second.evaluate("window.__PIXEL_WORKS_DEMO__.model.switchProject('gta-klonen')")
 second.evaluate('window.pixelWorksApplyLive()')
 assert second.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='gta-klonen'
 second.close()
 print('Browser integration PASS: startup-only saved choice, sticky project, wizard create, decision link, consent once, station labels, context')
 browser.close()
