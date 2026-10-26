"""Chromium smoke test for Pixel Works station-first UI, using fake API data."""
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT=Path(__file__).parent/'src/pw-v0121118.js'

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1180,'height':860})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/assets/office-v2/graphics-studio-pastel.png', lambda route: route.fulfill(body=(Path(__file__).parent/'assets/office-v2/graphics-studio-pastel.png').read_bytes(), content_type='image/png'))
        page.set_content('''<html><head><base href="http://127.0.0.1:8765/"></head><body class="live-project"><select id="projectSelect"><option value="testprojekt">Testprojekt</option><option value="annat">Annat</option></select><div id="stationLayer"><div class="station" data-id="art" role="button" tabindex="0">Grafikstudio</div><div class="station" data-id="qa" role="button" tabindex="0">Testning</div><div class="station" data-id="meeting" role="button" tabindex="0">Mötesrum</div><div class="station" data-id="lead">Chef</div></div><script>
          window.__savedOrders=[];window.__oldQueue=[];
          window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'testprojekt'}};
          window.pixelWorksApi=async(path,payload)=>{
           if(!payload && path.includes('/assets'))return {assets:[{id:'ref-1',name:'Kattbild.png',station:'art',status:'approved'}]};
           if(payload && path.includes('/orders')){window.__savedOrders.push({path,payload});return {order:{id:'abc'}};}
           if(payload && path.includes('/assets'))return {asset:{id:'new'}};
           return {};
          };
          window.pixelWorksStationOrders=(...args)=>{window.__oldQueue.push(args)};
          window.pixelWorksRefreshOrders=()=>{};
        </script></body></html>''')
        page.add_script_tag(path=str(SCRIPT))
        page.locator('#stationLayer .station[data-id="art"]').click()
        assert page.locator('#pw18Desk').is_visible()
        assert page.locator('#pw18Desk button[data-cat="0"]').inner_text().find('Eget uppdrag')>=0
        assert page.locator('#pw18Desk button').filter(has_text='Föremål').count()==1
        page.locator('#pw18Desk button').filter(has_text='Föremål').click()
        assert page.locator('#pw18Desk').get_by_text('Lägg till nya objekt i spelet').is_visible()
        page.locator('#pw18Desk').get_by_text('Lägg till nya objekt i spelet').click()
        assert 'Föremål › Lägg till nya objekt' in page.locator('.pw18-crumb').inner_text()
        assert page.locator('input[name=pw18Priority]:checked').get_attribute('value')=='2'
        page.locator('#pw18Description').fill('Skapa en magisk nyckel som passar i spelets pixelstil.')
        page.locator('input[name=pw18Priority][value="1"]').check()
        page.locator('details').first.evaluate('(d)=>d.open=true')
        page.locator('input[data-ref="ref-1"]').check()
        page.locator('[data-go="submit"]').click()
        page.get_by_text('Arbetsordern är sparad').wait_for()
        orders=page.evaluate('window.__savedOrders')
        assert len(orders)==1,orders
        assert orders[0]['payload']['station']=='art'
        assert orders[0]['payload']['priority']==1
        assert orders[0]['payload']['attachment_ids']==['ref-1']
        assert 'magisk nyckel' in orders[0]['payload']['instruction']
        page.locator('#pw18Desk .pw18-x').click()
        # QA: custom and bug workflows, with no native prompt.
        page.locator('[data-id="qa"]').click()
        page.get_by_role('button',name='Rapportera bugg').click()
        page.get_by_role('button',name='AI och NPC').click()
        assert 'AI och NPC' in page.locator('.pw18-crumb').inner_text()
        assert page.locator('input[name=pw18Priority]:checked').get_attribute('value')=='2'
        page.locator('#pw18Desk .pw18-x').click()
        # Meeting: plan is preview only. It must not enqueue 5 premature orders.
        page.locator('[data-id="meeting"]').click()
        page.get_by_role('button',name='Ny karaktär / NPC').click()
        page.get_by_role('button',name='Djur eller varelse').click()
        page.locator('#pw18Description').fill('Jag vill ha en NPC-katt som följer spelaren, spinner och hjälper till.')
        page.locator('[data-go="plan"]').click()
        for s in ['Grafikstudio','Musikstudio','Programmering','Testning','Dokumentation']:
            assert page.locator('.pw18-preview').get_by_text(s).count()==1
        assert len(page.evaluate('window.__savedOrders'))==1
        page.locator('[data-go="submit"]').click()
        page.get_by_text('Arbetsordern är sparad').wait_for()
        assert len(page.evaluate('window.__savedOrders'))==2
        assert 'prioriterad arbetsplan' in page.evaluate('window.__savedOrders[1].payload.instruction')
        # Project swap must abort, even with an already-open dialog.
        page.locator('#pw18Desk .pw18-x').click()
        page.locator('[data-id="art"]').click()
        page.locator('[data-cat="0"]').click()
        page.locator('#pw18Description').fill('Skapa en ny miljö för skogen och gör den färgrik.')
        page.evaluate("window.__PIXEL_WORKS_DEMO__.model.activeProjectId='annat'")
        page.locator('[data-go="submit"]').click()
        assert len(page.evaluate('window.__savedOrders'))==2
        assert 'bytt spel' in page.locator('#pw18Status').inner_text()
        page.locator('#pw18Desk .pw18-x').click()
        assert not errors,errors
        print('PASS: Grafik kategori/underkategori, referens, prio, QA, möte, projektgräns, inga JS-fel')
        # Visual screenshot of graphics studio background.
        page.evaluate("window.__PIXEL_WORKS_DEMO__.model.activeProjectId='testprojekt'")
        page.locator('[data-id="art"]').click()
        page.screenshot(path=str(Path(__file__).parent/'test_browser_0121118_art.png'))
        browser.close()

if __name__=='__main__':run()
