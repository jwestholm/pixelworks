#!/usr/bin/env python3
"""UI fixture: renders v2.7 beside existing global roster, no AI, no real files."""
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path('/mnt/data/pw_studio_v24')
V25=Path('/mnt/data/pw_global_v25')
ROOT=Path(__file__).resolve().parents[1]
HTML=(BASE/'tests/fixture-v24.html').read_text(encoding='utf-8')
HTML=HTML.replace('<script src="../src/pw-studio-roster-v24.js"></script>','')
HTML=HTML.replace("<script>document.querySelector('#pw13Dialog').showModal();</script>",'')
HTML=HTML.replace('</body>', '''<script>
window.wfActive=false;
const baseline=window.pixelWorksApi;
window.pixelWorksApi=async(path,payload)=>{
 if(path==='/api/pw-v025/global-staff')return {registered:true,people_count:15,
   staff:people.slice(),projects,needs_reconciliation:false,registry_created_at:'2026-10-30'};
 if(path==='/api/pw-v027/workforce')return {registered:true,active:window.wfActive,
   count:15,people:people.slice(),projects,revision:window.wfActive?1:null};
 if(path==='/api/pw-v027/workforce/activate'){
   window.called.push({path,payload});if(payload.expected_ids.length!==15)throw Error('stale');
   window.wfActive=true;return {active:true};}
 return baseline(path,payload);
};
</script></body>''')
SCRIPTS=[BASE/'src/pw-studio-roster-v24.js',V25/'src/pw-global-staff-v25.js',
         ROOT/'src/pw-global-office-v26.js',ROOT/'src/pw-global-workforce-v27.js']

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for vp in ({'width':1260,'height':840},{'width':390,'height':780}):
        page=browser.new_page(viewport=vp)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(HTML)
        for script in SCRIPTS:page.add_script_tag(path=str(script))
        page.locator('#pw13Dialog').evaluate('(d)=>d.showModal()')
        page.locator('.pw27-workforce button').wait_for(timeout=6500)
        assert 'Nästa steg' in page.locator('.pw27-workforce').inner_text()
        assert page.evaluate('window.called.filter(x=>x&&x.payload).length')==0
        page.locator('.pw27-workforce button').click()
        page.locator('#pw27Confirm').wait_for(state='visible')
        assert 'Gunnar' in page.locator('#pw27Confirm .pw27-people').inner_text()
        assert page.evaluate('window.called.filter(x=>x&&x.payload).length')==0
        page.locator('#pw27Confirm button').first.click()
        page.wait_for_function('window.wfActive===true',timeout=3000)
        page.wait_for_function('document.body.classList.contains("pw27-workforce-active")',timeout=3000)
        assert page.evaluate('window.called.filter(x=>x&&x.payload).length')==1
        calls=page.evaluate('window.called.filter(x=>x&&x.payload)')
        assert calls[0]['path']=='/api/pw-v027/workforce/activate'
        assert calls[0]['payload']['approval']=='ACTIVATE_GLOBAL_WORKFORCE_V27'
        panel=page.locator('.pw27-workforce')
        assert 'GLOBAL ARBETSSTYRKA AKTIV' in panel.inner_text()
        assert '5' in panel.inner_text()
        assert page.locator('.pw13-card').count()==15
        assert page.locator('.pw25-box').evaluate('(n)=>getComputedStyle(n).display')=='none'
        assert page.locator('#pw13Dialog').evaluate('(d)=>getComputedStyle(d).overflowY')=='auto'
        page.locator('#pw13Dialog').evaluate('(d)=>d.scrollTop=d.scrollHeight')
        assert page.locator('#pw13Dialog').evaluate('(d)=>d.scrollTop')>50
        assert not errors,errors
        path=ROOT/('workforce-mobile.png' if vp['width']<600 else 'workforce-desktop.png')
        page.screenshot(path=str(path),full_page=True)
        page.close()
    browser.close()
print('OK global workforce opt-in desktop/mobile, no unintended POST, current roster preserved')
