"""Isolated Chromium UI test – simulated JSON API; does not contact Pixel Works or AI."""
import json, sys, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'backend'))
import pw_recruitment_v3 as m
class Core:
    def __init__(self,p):self.ROOT=Path(p);self.LOCK=threading.RLock();self.JOBS={}

html='''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#142e42;font:14px system-ui"><div id="officeStage" style="position:relative;height:760px;max-width:100%;background:linear-gradient(#a2cacc 0 36%,#e8bb8b 36%);overflow:hidden"><div id="agentLayer"></div><div id="pw13OfficeRoster"></div></div>
<button data-dock="agents">Agenter (gammal genväg)</button><script src="../src/pw-v3-recruit.js"></script></body></html>'''
(here/'recruitment-mock.html').write_text(html,encoding='utf-8')

def run():
    with tempfile.TemporaryDirectory() as tmp:
        initial=m.state(Core(tmp))
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for size in [{'width':1400,'height':940},{'width':390,'height':844}]:
                page=browser.new_page(viewport=size,device_scale_factor=1)
                page.on('console',lambda msg: print('BROWSER:',msg.type,msg.text[:130]) if msg.type=='error' else None)
                page.on('pageerror',lambda exc: print('PAGEERROR:',str(exc)))
                setup='''
                window.__mockData=JSON.parse(%s);
                window.pixelWorksApi=async function(url,payload){
                  let d=window.__mockData;
                  if(!payload)return structuredClone(d);
                  if(url.endsWith('/activate')){
                    d.enabled=true;d.revision=1;
                    let c={id:'chef',name:'Chefen',subtitle:'Din första kollega',quote:'Chefen',skills:{coding:3,art:2,qa:3,music:2,research:4,design:4,planning:5},traits:{},colors:['#eee','#335','#b86'],voice:'Lugn',quirk:'Kaffe',weakness:'Djup kod'};
                    d.people=[{person_id:'pw3-chef',character_id:'chef',role:'lead',role_name:'Arbetsledare',name:'Chefen',character:c,work_description:'Planera',worker:{id:'pw3-chef',role:'lead',status:'idle'}}];
                    return structuredClone(d);
                  }
                  if(payload.revision!==d.revision)throw Error('Fel revision');
                  d.revision++;
                  if(url.endsWith('/hire')){let c=d.candidates.find(x=>x.id===payload.candidate_id);
                    d.people.push({person_id:'pw3-'+c.id,character_id:c.id,role:payload.role,role_name:d.roles[payload.role],name:c.name,character:c,work_description:'',worker:{id:'pw3-'+c.id,role:payload.role,status:'idle'}});
                  }else if(url.endsWith('/profile')){let p=d.people.find(x=>x.person_id===payload.person_id);p.role=payload.role;p.work_description=payload.work_description;p.role_name=d.roles[p.role]||'Arbetsledare';
                  }else if(url.endsWith('/interview')){let c=d.candidates.find(x=>x.id===payload.candidate_id);
                    let result={candidate_id:c.id,role:payload.role,score:c.skills[d.role_skill[payload.role]],source:'DEMO',text:'Fiktivt exempel, ej AI'};
                    d.interviews[c.id]=result;return {revision:d.revision,interview:structuredClone(result)};
                  }else if(url.endsWith('/dismiss')){d.people=d.people.filter(x=>x.person_id!==payload.person_id)}
                  return structuredClone(d);
                };
                window.confirm=()=>true;
                '''%json.dumps(json.dumps(initial))
                page.set_content(html.replace('<script src="../src/pw-v3-recruit.js"></script>',''))
                page.evaluate(setup)
                page.add_script_tag(content=(here.parent/'src/pw-v3-recruit.js').read_text(encoding='utf8'))
                page.locator('#pw3Open').click()
                page.locator('#pw3Activate').click()
                page.locator('#pw3Team').wait_for()
                assert page.locator('#pw3OfficeAgents .pw3-person').count()==1
                page.locator('#pw3Candidates').click()
                page.locator('#pw3Role').select_option('programmer')
                assert 'programmerare' in page.locator('#pw3Dialog').inner_text().lower()
                # Find Mira and hire her as programmer, despite graphics skill being highest.
                for _ in range(6):
                    if 'Mira Byte' in page.locator('#pw3Dialog .pw3-portrait-card').inner_text():break
                    page.locator('#pw3Next').click()
                assert 'Mira Byte' in page.locator('#pw3Dialog').inner_text()
                assert 'Svag matchning' in page.locator('#pw3Dialog').inner_text()
                page.locator('#pw3Role').select_option('artist')
                page.locator('#pw3Interview').click()
                page.locator('#pw3-gorilla').count() if False else None
                assert page.locator('#pw3Dialog .pw3-gorilla svg').count()==1
                assert 'DEMO' in page.locator('#pw3Dialog .pw3-interview').inner_text()
                page.locator('#pw3Role').select_option('programmer')
                page.locator('#pw3Hire').click()
                assert page.locator('#pw3OfficeAgents .pw3-person').count()==2
                page.locator('#pw3Team').click()
                page.locator('[data-staff="pw3-mira"]').click()
                assert page.locator('#pw3WorkDescription').is_visible()
                page.locator('#pw3WorkDescription').fill('QA ska granska prototypen')
                page.locator('#pw3StaffRole').select_option('artist')
                page.locator('#pw3SaveStaff').click()
                assert page.locator('#pw3WorkDescription').input_value()=='QA ska granska prototypen'
                # One outer scroll, no inner scroll trap.
                assert page.locator('#pw3Dialog').evaluate('(e)=>getComputedStyle(e).overflowY')=='auto'
                assert page.locator('#pw3Dialog').evaluate('(e)=>e.scrollHeight>e.clientHeight') or size['width']>700
                outfile=here.parent.parent/('recruitment-mobile.png' if size['width']<500 else 'recruitment-desktop.png')
                # Show candidate UI in screenshots.
                page.locator('#pw3Candidates').click()
                page.locator('#pw3Role').select_option('artist')
                page.screenshot(path=str(outfile),full_page=False)
                print('PASS',size,'screenshot',outfile)
                page.close()
        finally:browser.close()
if __name__=='__main__':run()
