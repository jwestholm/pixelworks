"""Isolated Chromium regression for V3.2 UI and fixed sprites. No AI or live game server."""
import json,sys,tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'backend'))
import pw_recruitment_v3 as v3
class Core:
 def __init__(self,r):self.ROOT=Path(r);self.LOCK=threading.RLock();self.JOBS={}
with tempfile.TemporaryDirectory() as d:
 s=Core(d);v3.activate(s,{'approval':v3.APPROVAL})
 initial=v3.state(s)
# HTML file at project root means sprite URLs are real images not about:blank data.
html=here.parent/'_test_recruitment_v32.html'
html.write_text('''<!doctype html><html lang="sv"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#143248;font:14px system-ui}#officeStage{position:relative;height:750px;background:linear-gradient(#aad2cd 35%,#dfb68d 35%);overflow:hidden}.agent{position:absolute;display:block;width:48px;height:68px;transform:translate(-50%,-70%)}.agent-name{position:absolute;top:-12px;color:white;background:#143248;font-size:11px}</style>
<button data-dock="office" id="officeControl">Kontor</button><button data-dock="agents">Agenter</button>
<dialog id="localStudioDialog">Gamla personaldialogen</dialog><div id="officeStage"><div id="agentLayer"></div><div id="pw13OfficeRoster"></div></div>
<script src="src/pw-v3-recruit.js"></script></html>''')
pre='''
window.__officeClicked=0;
document.addEventListener('click', e => {if(e.target?.matches('#officeControl'))window.__officeClicked++});
window.__mockData=JSON.parse(%s);
window.pixelWorksApi=async function(url,payload){let d=window.__mockData;if(!payload)return structuredClone(d);
 if(payload.revision!==d.revision)throw Error('revision mismatch');d.revision++;
 if(url.endsWith('/hire')){let c=d.candidates.find(x=>x.id===payload.candidate_id);d.people.push({person_id:'pw3-'+c.id,character_id:c.id,role:payload.role,role_name:d.roles[payload.role],name:c.name,character:c,work_description:'',prompt_preview:c.prompt_preview,worker:{id:'pw3-'+c.id,role:payload.role}})}
 else if(url.endsWith('/profile')){let p=d.people.find(x=>x.person_id===payload.person_id);p.role=payload.role;p.role_name=d.roles[p.role];p.work_description=payload.work_description}
 return structuredClone(d)};window.confirm=()=>true;
'''%json.dumps(json.dumps(initial))
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--allow-file-access-from-files'])
 try:
  for width,height in [(1350,900),(390,844)]:
   context=browser.new_context(viewport={'width':width,'height':height})
   page=context.new_page()
   errs=[]
   page.on('pageerror',lambda e:errs.append(str(e)))
   page.set_content(html.read_text().replace('<script src="src/pw-v3-recruit.js"></script>',''))
   page.evaluate(pre)
   page.add_script_tag(content=(here.parent/'src/pw-v3-recruit.js').read_text())
   page.locator('#pw3Open').click()
   page.locator('#pw3Candidates').click()
   for k in range(6):
    if 'Mira Byte' in page.locator('#pw3Dialog .pw31-name').inner_text():break
    page.locator('#pw3NextTop').click()
   assert 'Mira Byte' in page.locator('.pw31-name').inner_text()
   assert 'Bäst lämpad för:' in page.locator('#pw3Dialog').inner_text()
   assert 'Pixelgrafiker' in page.locator('.pw32-best').inner_text()
   page.locator('.pw32-story summary').click()
   assert '64 versioner' in page.locator('.pw32-story').inner_text()
   page.locator('#pw3Role').select_option('programmer')
   assert 'Pixelgrafiker' in page.locator('.pw32-best').inner_text()
   page.locator('#pw3Hire').click()
   page.locator('.pw3-person[data-person-id="pw3-mira"]').wait_for()
   sprite=page.locator('.pw3-person[data-person-id="pw3-mira"]')
   assert sprite.get_attribute('data-character-id')=='mira'
   imgurl=sprite.evaluate('(e)=>getComputedStyle(e).backgroundImage')
   assert 'mira-idle.png' in imgurl,imgurl
   # Browser decode of exact packaged PNG bytes; URL itself is tested in computed CSS.
   import base64
   uri='data:image/png;base64,'+base64.b64encode((here.parent/'assets/characters/mira/mira-idle.png').read_bytes()).decode()
   image_loaded=page.evaluate("async uri=>{let im=new Image();im.src=uri;await im.decode();return [im.naturalWidth,im.naturalHeight]}",uri)
   assert image_loaded==[192,68],image_loaded
   page.locator('#pw3Team').click()
   page.locator('[data-staff="pw3-mira"]').click()
   assert 'Mira' in page.locator('#pw3Dialog').inner_text()
   assert 'AI-instruktion' in page.locator('#pw3Dialog').inner_text()
   page.locator('#pw3StaffRole').select_option('artist')
   page.locator('#pw3SaveStaff').click()
   assert sprite.get_attribute('data-character-id')=='mira'
   assert 'mira-idle.png' in sprite.evaluate('(e)=>getComputedStyle(e).backgroundImage')
   # Exit goes back to office; legacy modal behind recruiter is closed.
   page.locator('#pw3Close').click()
   assert page.locator('#pw3Dialog').evaluate('(e)=>!e.open')
   assert page.evaluate('window.__officeClicked')>=1
   page.locator('#localStudioDialog').evaluate('(e)=>e.showModal()')
   page.evaluate("window.pixelWorksRecruitV3.open('crew')")
   assert page.locator('#localStudioDialog').evaluate('(e)=>!e.open')
   page.locator('#pw3Close').click()
   assert page.locator('#pw3Dialog').evaluate('(e)=>!e.open')
   assert not errs,errs
   print('PASS Chromium V3.2',width,height,'sprites and close/back navigation')
   context.close()
 finally:browser.close()
html.unlink(missing_ok=True)
