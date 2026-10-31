#!/usr/bin/env python3
"""Browser test with mock project records. Does NOT test real live browser or API."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
people=[{'studio_id':'pw-'+format(i,'020x'),'agent_id':'codex-'+str(i),
         'name':'Gunnar' if i<2 else 'Chefen','role':'Programmerare','role_type':'programmer',
         'project_id':'hackertoolkit' if i!=1 else 'sjutbanan',
         'project_name':'Hackertoolkit' if i!=1 else 'Sjutbanan',
         'busy':False} for i in range(3)]
projects=[{'id':'hackertoolkit','name':'Hackertoolkit'},{'id':'sjutbanan','name':'Sjutbanan'}]
styles='''body{background:#143548}#pw13Dialog{width:880px;max-height:90vh;background:#f9f6ed;color:#233b4b;border:7px ridge #ac7a52;padding:0}#pw13Dialog .pw13-shell{padding:14px;height:100%;}#pw13Dialog .pw13-staff{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}#pw13Dialog .pw13-card{background:white;border:2px solid #9db;padding:10px;}#pw13Dialog button{padding:7px;background:#e8c379}'''
script='''
window.calls=[];
window.registered=false;
window.pixelWorksApi=async (path,payload)=>{
 window.calls.push({path,payload});
 if(path==='/api/pw-v013/studio')return {shared:true,staff:__STAFF__,projects:__PROJECTS__};
 if(path==='/api/pw-v025/global-staff')return {registered:window.registered,people_count:window.registered?3:0,current_count:3,projects:__PROJECTS__,staff:__STAFF__,new_count:0,missing_count:0,changed_assignments:[],needs_reconciliation:false,backup_ref:window.registered?'studio-v013/staff-backups-v25/test':null};
 if(path==='/api/pw-v025/global-staff/activate'){
  if(payload.approval!=='CREATE_GLOBAL_STAFF_V25'||payload.expected_ids.length!==3)throw Error('Wrong ids');
  window.registered=true;return {registered:true,created:true,people_count:3,projects:__PROJECTS__,staff:__STAFF__,new_count:0,missing_count:0,changed_assignments:[],needs_reconciliation:false,backup_ref:'studio-v013/staff-backups-v25/test'};
 }
 throw Error('Unexpected API '+path);
};
'''.replace('__STAFF__',json.dumps(people,ensure_ascii=False)).replace('__PROJECTS__',json.dumps(projects,ensure_ascii=False))
html='''<!doctype html><html lang="sv"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>__CSS__</style></head><body>
<dialog id="pw13Dialog"><div class="pw13-shell"><header class="pw13-head"><h2>Min studio</h2></header>
<h3>🎮 Projekt</h3><div class="pw13-projects"><button>Hackertoolkit</button><button>Sjutbanan</button></div><h3>Personalen</h3>
<div class="pw13-staff">__PEOPLE__</div></div></dialog><script>__SCRIPT__</script></body></html>'''
cards=''.join(f'''<article class="pw13-card" id="pw13-card-{p['studio_id']}"><strong>{p['name']}</strong><small>{p['project_name']}</small><div class="pw13-assignment"><button>Visa</button></div></article>''' for p in people)
html=html.replace('__CSS__',styles).replace('__PEOPLE__',cards).replace('__SCRIPT__',script)

def check(viewport):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport=viewport)
        errs=[];page.on('pageerror',lambda ex:errs.append(str(ex)))
        page.set_content(html)
        # Test the shipped v2.4 module as well.
        page.add_script_tag(path=str(ROOT.parents[0]/'pw_studio_v24'/'src'/'pw-studio-roster-v24.js'))
        page.add_script_tag(path=str(ROOT/'src'/'pw-global-staff-v25.js'))
        page.locator('#pw13Dialog').evaluate('(d)=>d.showModal()')
        page.locator('.pw25-box').wait_for(timeout=9000)
        page.get_by_text('Konvertera till en global personalstyrka').wait_for()
        assert not page.evaluate('window.registered')
        assert not page.evaluate('window.calls.some(c=>c.payload)')
        page.get_by_role('button',name='Granska och skapa personregister').click()
        page.locator('#pw25-confirm').wait_for()
        assert page.get_by_text('Gunnar · Hackertoolkit').count()==1
        assert page.get_by_text('Gunnar · Sjutbanan').count()==1
        assert not page.evaluate('window.calls.some(c=>c.payload)')
        page.get_by_role('button',name='Avbryt').click()
        assert not page.evaluate('window.calls.some(c=>c.payload)')
        page.get_by_role('button',name='Granska och skapa personregister').click()
        page.get_by_role('button',name='Skapa register med säkerhetskopia').click()
        page.get_by_text('Global personalstyrka registrerad').wait_for()
        assert page.evaluate('window.registered')
        actions=page.evaluate('window.calls.filter(c=>c.payload)')
        assert len(actions)==1, actions
        assert actions[0]['payload']['expected_ids']==sorted(p['studio_id'] for p in people)
        assert len(page.locator('.pw13-card').all())==3
        assert not errs, errs
        browser.close()

if __name__=='__main__':
    check({'width':1220,'height':850})
    check({'width':390,'height':800,'isMobile':True,'hasTouch':True})
    print('OK: desktop+mobile, preview/cancel/migrate, identities kept')
