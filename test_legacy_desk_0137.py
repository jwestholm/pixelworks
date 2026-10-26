"""Ensures legacy chief builder remains actionable after visual overlay."""
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).parent
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1200,'height':860})
 page.on('pageerror',lambda exc: (_ for _ in ()).throw(RuntimeError(str(exc))))
 page.route('**/assets/office-v2/**',lambda route:route.fulfill(path=str(BASE/'assets'/'office-v2'/route.request.url.rsplit('/',1)[-1]),content_type='image/png'))
 page.set_content('''<!doctype html><html><head><base href="http://127.0.0.1:8765/"></head><body><dialog id="localStudioDialog" class="local-dialog" open style="display:flex;flex-direction:column;gap:8px;padding:18px">
 <div class="local-shell-header" style="display:flex;justify-content:space-between"><h2>⚙ LOKAL STUDIO</h2><button id="localClose">Stäng</button></div>
 <div class="local-shell-info">Teknisk versionsinformation</div>
 <div class="local-shell-body"><div class="station-builder"><div class="station-builder-top"><h3>👔 Chefsbord – välj uppdrag</h3></div>
 <div class="station-task-grid"><button class="station-task-tile">Planera produktion</button><button class="station-task-tile">Fördela arbete</button><button class="station-task-tile">Granska resultat</button></div>
 <div class="local-actions"><button id="queue">Arbetskö</button></div></div></div></dialog>
 <select id="projectSelect"><option value="demospelet">Demo</option></select>
 <script>window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'demospelet'}};window.pixelWorksApi=async()=>({assets:[]});</script></body></html>''')
 page.add_script_tag(path=str(BASE/'src/pw-v0121118.js'))
 assert page.locator('#localStudioDialog').is_visible()
 assert page.locator('#localStudioDialog').evaluate("e=>getComputedStyle(e).backgroundImage.includes('leadership-studio-pastel.png')")
 assert page.locator('#localStudioDialog .local-shell-header h2').evaluate('e=>getComputedStyle(e,"::after").content.includes("Arbetsledning")')
 page.locator('.station-task-tile').first.click()
 page.locator('#localStudioDialog').screenshot(path=str(BASE/'ui_0137_lead.png'))
 assert page.locator('#queue').is_visible()
 b.close()
 print('PASS: chief legacy menu illustrated, buttons accessible, no backend invoked')
