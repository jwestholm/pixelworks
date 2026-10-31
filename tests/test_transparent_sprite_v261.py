#!/usr/bin/env python3
"""Playwright contract test: local fixture, faked API, no real user projects."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

HERE=Path(__file__).resolve().parents[1]
OLD=Path('/mnt/data/pw_studio_v24')
V25=Path('/mnt/data/pw_global_v25')
SCRIPTS=[OLD/'src/pw-studio-roster-v24.js',V25/'src/pw-global-staff-v25.js',HERE/'src/pw-global-office-v26.js']
HTML=(OLD/'tests/fixture-v24.html').read_text(encoding='utf-8').replace('<script src="../src/pw-studio-roster-v24.js"></script>','')
HTML=HTML.replace('</body>', '''<style>
#officeStage{position:relative;width:980px;height:680px;background:#bdc6b9;overflow:hidden;margin:16px auto}
#agentLayer,#pw13OfficeRoster{position:absolute;inset:0}
#pw13OfficeRoster{z-index:24}
#agentLayer .agent{display:block}
#officeStage .agent{position:absolute;width:46px;height:65px;transform:translate(-50%,-70%);background-color:#fff;border:2px solid #37516d;}
#officeStage .agent.sprite-role-lead{background-image:linear-gradient(to right, #123456 0 25%, transparent 25% 100%);background-repeat:no-repeat}
#officeStage .agent-name{position:absolute;top:-18px;white-space:nowrap;background:#102e3a;color:white;font-size:11px;padding:2px}
#officeStage .agent-status{position:absolute;bottom:0;right:0;border:3px solid #fff;width:10px;height:10px;background:green}
@media(max-width:630px){#officeStage{width:920px;height:680px}}
</style>
<button id="pw13StudioNav">Min studio</button><div id="officeStage"><div id="agentLayer"><div class="agent" id="oldProjectOnly"></div></div><div id="pw13OfficeRoster"><button class="pw13-group">+12 kollegor</button></div></div>
<script>
document.body.classList.add('live-project');
window.__PIXEL_WORKS_DEMO__={model:{project:{live:true},activeProjectId:'hackertoolkit'}};
document.querySelector('#pw13StudioNav').onclick=()=>{const d=document.querySelector('#pw13Dialog');if(!d.open)d.showModal();};
let baseApi=window.pixelWorksApi;
const fakeStaff=people.map((p,i)=>({...p,station:['cafe','code','lead','qa','docs'][i%5],busy:i===1}));
window.pixelWorksApi=async(path,payload)=>{
  if(path==='/api/pw-v013/studio')return {staff:fakeStaff,projects,shared:true};
  if(path==='/api/pw-v025/global-staff')return {registered:true,people_count:15,staff:fakeStaff,projects,needs_reconciliation:false};
  return baseApi(path,payload);
};
</script></body>''')

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for viewport in [{'width':1260,'height':820},{'width':390,'height':780}]:
            page=browser.new_page(viewport=viewport)
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.set_content(HTML)
            for script in SCRIPTS:page.add_script_tag(path=str(script))
            page.locator('#pw26GlobalAgents .pw26-person').first.wait_for(timeout=6500)
            page.wait_for_timeout(250)
            assert page.locator('#pw26GlobalAgents .pw26-person').count()==15
            assert page.locator('.pw13-group').count()==1
            assert page.locator('#pw13OfficeRoster').evaluate('(el)=>getComputedStyle(el).display')=='none'
            assert page.locator('#agentLayer').evaluate('(el)=>getComputedStyle(el).visibility')=='hidden'
            assert page.locator('#pw26GlobalAgents .pw26-person[title*=Gunnar]').count()>=2
            assert page.locator('#pw26GlobalAgents .pw26-person.working').count()==1
            # A standard button has an opaque user-agent background. The
            # game sprites need a transparent button surface so their image
            # alpha renders the actual floor, not a white rectangle.
            sprites=page.locator('#pw26GlobalAgents .pw26-person')
            colors=sprites.evaluate_all('(nodes)=>nodes.map(n=>getComputedStyle(n).backgroundColor)')
            assert set(colors)=={'rgba(0, 0, 0, 0)'},colors
            count=page.locator('#pw26-global-count').inner_text()
            assert '15 anställda' in count and '1 studio' in count, count
            assert '5 spel' in count and 'projekt' not in count, count
            lead=page.locator('.pw26-person.sprite-role-lead').first
            assert lead.count()==1
            bg=lead.evaluate('(n)=>getComputedStyle(n).backgroundImage')
            assert 'linear-gradient(' in bg,bg
            assert len(set(page.locator('.pw26-person').evaluate_all('(ns)=>ns.map(n=>n.dataset.studioId)')))==15
            # Pre-migration business route must remain unmodified by visual overlay.
            assert not page.evaluate('window.called.some(x=>x.payload)')
            # Top of dialog contains migration notice; bottom cards remain reachable.
            page.locator('#pw24-search').wait_for(timeout=6500)
            page.locator('.pw25-box').wait_for(timeout=6500)
            metrics=page.locator('#pw13Dialog').evaluate('(el)=>({client:el.clientHeight,scroll:el.scrollHeight,overflow:getComputedStyle(el).overflowY})')
            assert metrics['scroll']>metrics['client']+80 and metrics['overflow']=='auto',metrics
            page.locator('#pw13Dialog').evaluate('(el)=>el.scrollTop=el.scrollHeight')
            assert page.locator('#pw13Dialog').evaluate('(el)=>el.scrollTop')>120
            last=page.locator('.pw13-card').last
            last.scroll_into_view_if_needed()
            assert last.is_visible()
            # The filters still work after removing the nested list scroller.
            page.locator('#pw24-search').fill('Greta')
            assert page.locator('.pw13-card:visible').count()>0
            page.locator('#pw24-search').fill('')
            # Sprites from *other* projects open the same global staff dialog.
            page.locator('#pw13Dialog').evaluate('(d)=>d.close()')
            outsider=page.locator('.pw26-person').filter(has=page.locator('.agent-name',has_text='Gunnar')).first
            clicked_id=outsider.get_attribute('data-studio-id')
            outsider.evaluate('(n)=>n.click()')
            page.wait_for_function('(id)=>document.querySelector(`#pw13-card-${id}`)?.classList.contains("pw26-highlight")',arg=clicked_id,timeout=4000)
            assert page.locator('#pw13Dialog').evaluate('(d)=>d.open')
            assert page.locator('.pw13-card.pw26-highlight').count()==1
            # Drag a unique person to a desk. Dispatch exactly one request with
            # the PERSON'S own project and agent id, not the displayed project.
            page.locator('#pw13Dialog').evaluate('(d)=>d.close()')
            if viewport['width']>=800:
                page.evaluate("""() => {
                  window.moved=null;
                  window.__PIXEL_WORKS_DEMO__.ui={stationAt:()=>({dataset:{id:'code'}}),toast:()=>{}};
                  window.pixelWorksMoveLive=async(project,id,station)=>{window.moved={project,id,station};};
                }""")
                target=page.locator('.pw26-person:not(.working)').nth(3)
                expected={'project':target.get_attribute('data-project-id'),
                          'id':target.get_attribute('data-agent-id'),'station':'code'}
                b=target.bounding_box()
                assert b,b
                x=b['x']+b['width']/2;y=b['y']+b['height']/2
                page.mouse.move(x,y);page.mouse.down()
                page.mouse.move(x+90,y+30,steps=9);page.mouse.up()
                page.wait_for_function('window.moved !== null',timeout=3000)
                assert page.evaluate('window.moved')==expected
            # Office must remain independent from the browser's current project.
            page.evaluate("window.__PIXEL_WORKS_DEMO__.model.activeProjectId='pussel';window.dispatchEvent(new Event('pixelworks:project-changed'))")
            page.wait_for_timeout(600)
            assert page.locator('.pw26-person').count()==15
            assert not errors,errors
            path=HERE/('office-mobile.png' if viewport['width']<500 else 'office-desktop.png')
            page.screenshot(path=str(path),full_page=True)
            page.close()
        browser.close()
    print('OK: 15 individual clickable staff sprites, cross-project identity, dialog scroll desktop/mobile, old group hidden, no AI/POST')

if __name__=='__main__':run()
