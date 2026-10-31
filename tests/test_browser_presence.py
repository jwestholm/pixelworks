"""Standalone browser regression for real provider presence UI. No network/API cost."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

MODULE = Path(__file__).resolve().parents[1]/'src'/'pw-provider-presence.js'


def smoke():
    state = {'configured': True, 'execution_enabled': False, 'can_send': False, 'test_result': 'anslutningsfel (HTTP 503)', 'pause_reason': 'Gemini svarade HTTP 503'}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1200, 'height': 760})
        page.set_default_timeout(3500)
        page.on('console', lambda m: print('BROWSER:',m.text))
        page.on('pageerror', lambda e: print('ERROR:',str(e)))
        def route(req):
            req.fulfill(status=200, content_type='application/json', body=json.dumps({'providers':{'gemini':state}}))
        page.set_content('<body class="live-project"><aside class="right-rail"><section class="event-panel"><div id="eventFeed"></div></section></aside><div id="agentLayer"></div><div id="agentDrawerContent"><div class="agent-detail-head">Greta</div></div></body>')
        page.evaluate('''() => {
          window.fixtureStatus={configured:true, execution_enabled:false,can_send:false,test_result:'anslutningsfel (HTTP 503)',pause_reason:'Gemini svarade HTTP 503'};
          window.fetch=async ()=>({ok:true,json:async()=>({providers:{gemini:window.fixtureStatus}})});
          const greta = {id:'greta',name:'Greta',provider:'gemini',status:'idle',role:'Creative Director',engineAvailable:true};
          const gunnar = {id:'gunnar',name:'Gunnar',provider:'codex',status:'idle',role:'Developer'};
          const project = {id:'skjutbanan',live:true,agents:[greta,gunnar],providers:{gemini:{quota:'okänt'}}};
          const model = {activeProjectId:'skjutbanan',project,projects:[project],getAgent:id=>project.agents.find(a=>a.id===id),getStation:name=>name==='cafe'?{x:63,y:71}:null};
          const ui = {selectedAgentId:'greta',walks:new Map(),toasts:[],toast(t){this.toasts.push(t)},renderAgents(){
            const root=document.getElementById('agentLayer');root.replaceChildren();
            for(const a of project.agents) {const n=document.createElement('button');n.className='agent '+a.status;n.dataset.id=a.id;n.textContent=a.name;
              n.style.position='absolute';n.style.left='5%';n.style.top='5%';root.append(n)}},
            renderDrawer(){document.getElementById('agentDrawerContent').innerHTML='<div class="agent-detail-head">Greta</div>';}};
          window.__PIXEL_WORKS_DEMO__={model,ui};ui.renderAgents();
          window.pixelWorksAISettingsV01210=()=>{window.settingsOpened=true};
        }''')
        print('add_script_tag');page.add_script_tag(path=str(MODULE));print('script injected');print(page.evaluate('({rt:!!window.__PIXEL_WORKS_DEMO__,flag:!!window.__PW_PROVIDER_PRESENCE__,panel:!!document.querySelector("#pwProviderPresence")})'))
        page.wait_for_function('() => document.querySelector("#pwProviderPresence") && !document.querySelector("#pwProviderPresence").hidden')
        assert 'API' in page.locator('#pwProviderPresence').inner_text()
        assert 'kvoten är slut' in page.locator('#pwProviderPresence .pwpp-message').inner_text().lower()
        assert 'Gick hem' not in page.locator('#pwProviderPresence').inner_text()
        assert page.locator('#agentLayer [data-id="greta"]').evaluate('(e)=> e.classList.contains("pwpp-cafe")')
        assert page.locator('#agentLayer [data-id="greta"]').evaluate('(e)=>e.style.left')=='63%'
        assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.project.agents[0].status')=='blocked'
        assert not page.locator('#agentLayer [data-id="gunnar"]').evaluate('(e)=>e.classList.contains("pwpp-cafe")')
        assert 'kan inte' in page.locator('.pwpp-drawer-note').inner_text().lower()
        page.locator('#pwppGeminiSettings').click()
        assert page.evaluate('window.settingsOpened')
        page.evaluate('window.fixtureStatus={configured:true,execution_enabled:false,can_send:false,test_result:"kvotgräns nådd",pause_reason:"Gemini svarade 429"}')
        page.evaluate('window.pixelWorksRefreshProviderPresence()')
        page.wait_for_function('()=>document.querySelector("#agentLayer [data-id=greta]").classList.contains("pwpp-home")')
        assert page.locator('#agentLayer [data-id="greta"]').evaluate('(e)=>getComputedStyle(e).visibility')=='hidden'
        assert 'Gick hem' in page.locator('#pwProviderPresence').inner_text()
        page.evaluate('window.fixtureStatus={configured:true,execution_enabled:true,can_send:true,test_result:"ansluten",pause_reason:null}')
        page.evaluate('window.pixelWorksRefreshProviderPresence()')
        page.wait_for_function('()=>document.querySelector("#pwProviderPresence").hidden')
        assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.project.agents[0].status')=='idle'
        assert not page.locator('#agentLayer [data-id="greta"]').evaluate('(e)=>e.classList.contains("pwpp-home")')
        assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.project.agents[0].engineAvailable')
        browser.close()
    print('PASS: API 503 -> fika, 429 -> hem, restored -> back, Codex unaffected, settings and drawer')

if __name__=='__main__':
    smoke()
