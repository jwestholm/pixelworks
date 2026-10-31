#!/usr/bin/env python3
"""Browser regression for the real add-on against v0.13 dialog DOM structure.
Mocks are explicit: never claim this is a user's live staff roster."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
from functools import partial
from urllib.parse import quote
from playwright.sync_api import sync_playwright
import json
BASE=Path(__file__).resolve().parents[1]
HTML=BASE/'tests'/'fixture-v24.html'
PEOPLE=[]
PROJECTS=[{'id':n,'name':label} for n,label in [('hackertoolkit','Hackertoolkit'),('pussel','Pussel'),('cyberpunk','Fantasivärld i Cyberpunk'),('minesweeper','Minesweeper marathon'),('skjutbanan','Skjutbanan')]]
for i in range(15):
    proj=PROJECTS[i%5]
    name=['Gunnar','Greta','Chefen','Alexandra','Programmeraren'][i%5] if i<10 else ['Gunnar','Greta','Chefen','Artist','Gunnar'][i-10]
    PEOPLE.append({'studio_id':f'pw-{i:020x}', 'agent_id':f'agent{i}', 'name':name,'role':'Programmerare' if i%2 else 'Arbetsledare','role_type':'programmer' if i%2 else 'lead','project_id':proj['id'], 'project_name':proj['name'],'busy':i==1})

def generate():
    cards=''.join(f'''<article class="pw13-card" id="pw13-card-{p['studio_id']}">
<strong>☕ {p['name']}</strong><small>{p['role']} · Tillgänglig · {p['project_name']}</small>
<div class="pw13-assignment"><button>🎮 Visa spelet</button><select><option>{p['project_name']}</option></select><button>↗ Tilldela</button></div></article>''' for p in PEOPLE)
    projects=''.join('<button>'+p['name']+'</button>' for p in PROJECTS)
    api_js='''<script>
const people=__PEOPLE__;const projects=__PROJECTS__;
window.called=[];window.pixelWorksRefreshLive=async()=>{window.called.push('refresh')};
window.pixelWorksApi=async(path,payload)=>{
  window.called.push({path,payload});
  if(path==='/api/pw-v013/studio')return {staff:people.slice(),projects,shared:true};
  if(path.endsWith('/staff/dismiss')){
    const idx=people.findIndex(p=>p.agent_id===payload.agent_id&&path.includes(p.project_id));
    if(idx<0)throw Error('wrong identity');const [item]=people.splice(idx,1);return {dismissed:item.agent_id,history_preserved:true};
  }
  throw Error('Unexpected request: '+path);
};</script>'''.replace('__PEOPLE__',json.dumps(PEOPLE,ensure_ascii=False)).replace('__PROJECTS__',json.dumps(PROJECTS,ensure_ascii=False))
    template='''<!doctype html><html lang="sv"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{background:#153048;font:14px system-ui}#pw13Dialog{width:min(860px,96vw);max-height:88dvh;overflow:auto;box-sizing:border-box;padding:0;border:8px ridge #ac7a52;background:#f7f2e8;color:#1e3549;font:14px/1.5 system-ui,sans-serif}#pw13Dialog .pw13-shell{padding:18px 20px;background:linear-gradient(130deg,#fff9e9,#e6f1f3)}#pw13Dialog .pw13-staff{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}#pw13Dialog .pw13-card{background:#fff;border:2px solid #b1c0c5;padding:11px;box-shadow:2px 3px 0 #d2d2c7}#pw13Dialog .pw13-card strong{font-size:15px}#pw13Dialog .pw13-card small{display:block;color:#526c7e}#pw13Dialog button{background:#f3cc7e;color:#1b3249;border:2px solid #99713a;padding:8px 12px;margin:3px;cursor:pointer;font-weight:700;min-height:40px;border-radius:3px}#pw13Dialog .pw13-card select{max-width:100%;min-width:160px;min-height:39px;color:#1e3447;background:white;border:2px solid #9db0bf;padding:5px}
</style></head><body><dialog id="pw13Dialog"><div class="pw13-shell"><header class="pw13-head"><h2>🏢 Välkommen till Pixel Works</h2><button class="pw13-close">✕ Stäng</button></header><p>Här ser du hela teamet. Välj ett spel att fokusera på eller flytta en ledig medarbetare.</p><h3>🎮 Projekt</h3><div class="pw13-projects">__PROJECT_BUTTONS__</div><div class="pw23-studio-links"><button>💌 Alla hjälpärenden i studion</button><small>Hjälp i alla projekt.</small></div><h3>👥 Personalen – ett gemensamt kontor</h3><div class="pw13-staff">__CARDS__</div><p class="pw13-muted">Spelkod och historik ligger kvar i respektive projekt.</p></div></dialog>
__API_JS__<script src="../src/pw-studio-roster-v24.js"></script><script>document.querySelector('#pw13Dialog').showModal();</script></body></html>'''
    HTML.write_text(template.replace('__CARDS__',cards).replace('__PROJECT_BUTTONS__',projects).replace('__API_JS__',api_js),encoding='utf-8')

def run():
    generate()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1200,'height':850})
        errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
        html=HTML.read_text(encoding='utf-8').replace('<script src="../src/pw-studio-roster-v24.js"></script>', '')
        page.set_content(html)
        page.add_script_tag(path=str(BASE/'src'/'pw-studio-roster-v24.js'))
        page.locator('#pw24-search').wait_for(timeout=8000)
        assert page.locator('.pw13-card').count()==15
        assert page.locator('.pw24-identity').count()==15
        before=page.evaluate('window.called.map(x=>x.path||x)')
        assert before==['/api/pw-v013/studio'],before
        sizes=page.locator('.pw13-staff').evaluate('(el)=>({scroll:el.scrollHeight,client:el.clientHeight,overflow:getComputedStyle(el).overflowY})')
        assert sizes['scroll']>sizes['client']+90 and sizes['overflow']=='auto',sizes
        page.locator('.pw13-staff').evaluate('(el)=>{el.scrollTop=el.scrollHeight;}')
        assert page.locator('.pw13-staff').evaluate('(el)=>el.scrollTop')>100
        assert page.locator('#pw24-search').is_visible()
        page.locator('#pw24-search').fill('Gunnar')
        assert page.locator('.pw13-card:visible').count()>=2
        ids=page.locator('.pw13-card:visible').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.pw24Id)')
        assert len(ids)==len(set(ids))
        # Project filter combines with name: wrong project must never be targeted.
        page.locator('#pw24-project').select_option('hackertoolkit')
        assert all(x=='hackertoolkit' for x in page.locator('.pw13-card:visible').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.pw24Project)'))
        page.locator('#pw24-search').fill('omöjlig')
        assert page.locator('.pw13-card:visible').count()==0
        assert page.locator('.pw24-empty').is_visible()
        page.locator('#pw24-search').fill('');page.locator('#pw24-project').select_option('all')
        # Busy person cannot be dismissed.
        assert page.locator('.pw13-card').nth(1).locator('.pw24-dismiss').is_disabled()
        # Disambiguated dismissal is not executed on first click or invalid input.
        person=PEOPLE[0]
        card=page.locator('#pw13-card-'+person['studio_id'])
        card.locator('.pw24-dismiss').click()
        assert len(page.evaluate('window.called.filter(x=>x.payload)'))==0
        card.locator('.pw24-confirm input').fill('FEL')
        card.locator('.pw24-confirm .pw24-dismiss').click()
        assert len(page.evaluate('window.called.filter(x=>x.payload)'))==0
        card.locator('.pw24-confirm input').fill(person['name'])
        card.locator('.pw24-confirm .pw24-dismiss').click()
        page.wait_for_function('window.called.some(x=>x.payload&&x.path.includes("/staff/dismiss"))')
        assert not page.locator('#pw13-card-'+person['studio_id']).count()
        paths=page.evaluate('window.called.filter(x=>x.payload).map(x=>x.path)')
        assert paths==['/api/projects/hackertoolkit/staff/dismiss'],paths
        assert not errs,errs
        # Legacy v0.13 may rebuild the whole roster after a project transfer.
        # This must not strand the search bar or create duplicate controls.
        page.evaluate("""() => {
          const old=document.querySelector('.pw13-staff');
          const fresh=old.cloneNode(true);
          old.replaceWith(fresh);
        }""")
        page.locator('#pw24-search').wait_for()
        page.wait_for_function("document.querySelectorAll('#pw24-search').length===1")
        assert page.locator('.pw24-roster-tools').count()==1
        assert not errs,errs
        page.screenshot(path=str(BASE/'desktop.png'))
        page=browser.new_page(viewport={'width':390,'height':760})
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content(html);page.add_script_tag(path=str(BASE/'src'/'pw-studio-roster-v24.js'));page.locator('#pw24-search').wait_for()
        metrics=page.locator('.pw13-staff').evaluate('(el)=>({height:el.clientHeight,scroll:el.scrollHeight,width:el.clientWidth,overflow:getComputedStyle(el).overflowY})')
        assert metrics['height']>90 and metrics['scroll']>metrics['height']
        page.locator('.pw13-staff').evaluate('(el)=>el.scrollTop=el.scrollHeight')
        assert page.locator('.pw13-staff').evaluate('(el)=>el.scrollTop')>100
        overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
        assert not overflow, 'horizontal page scroll on 390px viewport'
        page.screenshot(path=str(BASE/'mobile.png'))
        assert not errs,errs
        browser.close()

    print('OK: 15 unique staff identities, scroll desktop/mobile, filters, busy guard, confirmed dismissal, no implicit POST')

if __name__=='__main__':run()
