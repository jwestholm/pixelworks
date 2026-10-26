"""Headless Chromium, fake API, verifies shared-office GUI + safe explicit move."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).parent

def run():
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1430,'height':920},device_scale_factor=1)
        failures=[];native=[]
        page.on('pageerror',lambda e:failures.append(str(e)))
        page.on('dialog',lambda d:(native.append(d.message),d.dismiss()))
        page.set_content('''<!doctype html><html lang="sv"><head><base href="http://127.0.0.1:8765/"><style>
          body{margin:0;background:#142333;color:#fff;font-family:system-ui}
          #gameDock{display:flex;gap:7px;padding:8px;background:#0e2133}
          #gameDock button{background:#254c68;color:white;padding:7px 12px;border:1px solid #4c8091}
          #officeStage{position:relative;width:1120px;height:750px;border:2px solid #966e42;
            background:linear-gradient(#80afb9 0 32%,#d4ab7c 32%)}
          .right-rail{position:absolute;top:100px;left:1130px;width:288px}
          #stationLayer{position:absolute;inset:0}
          .station{position:absolute;width:80px;height:35px;background:#5b493f;border:2px solid #ce9f62}
          </style></head><body class="live-project">
          <header><b class="brand-title">Pixel Works <span class="version">old</span></b>
          <nav id="gameDock"><button class="dock-item">Kontor</button></nav>
          <select id="projectSelect"><option value="alpha">Alfa</option><option value="beta">Beta</option></select></header>
          <div id="officeStage"><div id="stationLayer"><div class="station" style="top:40%;left:18%">Chef</div></div></div>
          <aside class="right-rail"></aside><script>
          window.__calls=[];window.__ops=[];
          window.__db={shared:false,projects:[{id:'alpha',name:'Alfa'},{id:'beta',name:'Beta'}],staff:[
             {studio_id:'pw-aaaaaaaaaaaaaaaaaaaa',agent_id:'chief-1',name:'Gunnar',role:'Programmerare',project_id:'alpha',project_name:'Alfa',station:'code',busy:false},
             {studio_id:'pw-bbbbbbbbbbbbbbbbbbbb',agent_id:'chief-1',name:'Greta',role:'Creative Director',project_id:'beta',project_name:'Beta',station:'meeting',busy:false},
             {studio_id:'pw-cccccccccccccccccccc',agent_id:'worker-1',name:'Anna',role:'Testare',project_id:'beta',project_name:'Beta',station:'qa',busy:true}
          ]};
          window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'alpha',project:{live:true},projects:[{id:'alpha'},{id:'beta'}],switchProject(id){this.activeProjectId=id}},ui:{renderAll(){},toast(t){window.__ops.push(t)}}};
          document.getElementById('projectSelect').addEventListener('change',e=>{window.__PIXEL_WORKS_DEMO__.model.switchProject(e.target.value)});
          window.pixelWorksApi=async(path,payload)=>{
            window.__calls.push({path,payload});
            if(path==='/api/pw-v013/studio')return {...window.__db,version:'0.13.0',staff_count:window.__db.staff.length,project_count:2};
            if(path.endsWith('/enable')){window.__db.shared=true;return {shared:true}};
            if(path.endsWith('/transfer')){const who=window.__db.staff.find(x=>x.studio_id===payload.studio_id);if(who.busy)throw Error('Personen arbetar');who.project_id=payload.target_project;who.project_name=window.__db.projects.find(x=>x.id===who.project_id).name;return {moved:true}};
            throw Error('Unexpected URL '+path);
          };
          window.pixelWorksRefreshLive=async()=>{};
          </script></body></html>''')
        page.add_script_tag(path=str(ROOT/'src'/'pw-v013.js'))
        page.get_by_text('Gemensam studio',exact=False).first.wait_for(timeout=8000)
        assert 'v0.13.0' in page.locator('.brand-title').inner_text()
        assert page.locator('#pw13-summary').get_by_text('3 anställda').count()==1
        # Staff from another project is drawn in the same office.
        assert page.locator('#pw13OfficeRoster .pw13-avatar').count()==2
        assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='alpha'
        print('CLICK STUDIO',flush=True);page.locator('#pw13StudioNav').click();print('OPENED',page.locator('#pw13Dialog').is_visible(),flush=True)
        assert page.locator('#pw13Dialog').is_visible()
        assert page.get_by_role('button',name='Aktivera gemensam studio').is_visible()
        # GET/initial view does not write anything or start provider operations.
        calls=page.evaluate('window.__calls')
        assert all(not c['payload'] for c in calls),calls
        print('ENABLING',flush=True);page.get_by_role('button',name='Aktivera gemensam studio').click();print('ENABLED',flush=True)
        print('WAITING',flush=True);page.get_by_text('Personalen – ett gemensamt kontor').wait_for(timeout=3500);print('DISPLAY',flush=True)
        assert page.get_by_role('button',name='Tilldela').count()==3
        gunnar=page.locator('#pw13-card-pw-aaaaaaaaaaaaaaaaaaaa')
        gunnar.locator('select').select_option('beta')
        print('FIRST MOVE',flush=True);gunnar.get_by_role('button',name='Tilldela').click();print('FIRST DONE',flush=True)
        # Two-step in-game confirmation; no native browser modal.
        assert not any(x['path'].endswith('/transfer') for x in page.evaluate('window.__calls'))
        print('SECOND MOVE',flush=True);gunnar.get_by_role('button',name='Bekräfta:').click(timeout=3500);print('SECOND DONE',flush=True)
        page.get_by_text('Gunnar',exact=False).first.wait_for()
        data=page.evaluate('window.__db')
        assert data['staff'][0]['project_id']=='beta'
        assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='alpha'
        assert page.locator('#pw13OfficeRoster .pw13-avatar').count()==3
        anna=page.locator('#pw13-card-pw-cccccccccccccccccccc')
        assert anna.get_by_role('button',name='Tilldela').is_disabled()
        assert not native,native
        # Manual project focus may change explicitly.
        print('FOCUS SWITCH',flush=True);page.locator('.pw13-projects button').filter(has_text='Beta').click(timeout=3500)
        assert page.evaluate('window.__PIXEL_WORKS_DEMO__.model.activeProjectId')=='beta'
        assert not failures,failures
        # Visual artifact for inspection.
        page.screenshot(path=str(ROOT/'PIXEL_WORKS_013_STUDIO_PREVIEW.png'))
        print('PASS: gemensam studio, personal från flera projekt, explicit tilldelning, ingen automatisk projektväxling eller browser-confirm')
        b.close()
if __name__=='__main__':run()
