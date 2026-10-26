"""Headless proof that new playable starter files actually run in a browser."""
import json,sys,tempfile,subprocess,threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).parent/'backend'))
import pw_v0134

with tempfile.TemporaryDirectory() as root:
 base=Path(root)/'test-game';work=base/'work';work.mkdir(parents=True)
 (base/'studio-bible').mkdir();(base/'studio-bible'/'GAME_BIBLE.md').write_text('# Game Bible\n',encoding='utf-8')
 (base/'project.json').write_text(json.dumps({'id':'test-game','name':'Minesweeper marathon','genre':'Pussel'}),encoding='utf-8')
 for n in ('README.md','AGENTS.md'):(work/n).write_text('Start',encoding='utf-8')
 subprocess.run(['git','init','-q',str(work)],check=True)
 server=SimpleNamespace(path_for=lambda slug:base)
 pw_v0134.bootstrap(server,'test-game',{'name':'Minesweeper marathon','genre':'Spel'})
 class Quiet(SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
 server_http=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=root))
 t=threading.Thread(target=server_http.serve_forever,daemon=True);t.start()
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1100,'height':760})
  errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
  page.set_content((work/'index.html').read_text(encoding='utf-8'))
  page.add_style_tag(content=(work/'style.css').read_text(encoding='utf-8'))
  page.add_script_tag(content=(work/'game.js').read_text(encoding='utf-8'))
  assert page.locator('#board button').count()==64
  assert page.locator('#message').inner_text().startswith('Öppna')
  page.locator('#board button').first.click()
  assert page.locator('#clock').inner_text().isdigit()
  assert page.locator('#board button.open').count()>0
  page.locator('#restart').click()
  assert page.locator('#board button.open').count()==0
  assert not errors,errors
  # A generic non-minesweeper prototype is independently interactive.
  base2=Path(root)/'other';work2=base2/'work';work2.mkdir(parents=True)
  (base2/'studio-bible').mkdir();(base2/'studio-bible'/'GAME_BIBLE.md').write_text('# Vision\n')
  (base2/'project.json').write_text(json.dumps({'id':'other','name':'Space Adventure'}))
  for n in ('README.md','AGENTS.md'):(work2/n).write_text('Start')
  subprocess.run(['git','init','-q',str(work2)],check=True)
  pw_v0134.bootstrap(SimpleNamespace(path_for=lambda s:base2),'other',{'name':'Space Adventure','genre':'Action'})
  page.close()
  page=browser.new_page(viewport={'width':1100,'height':760})
  errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
  page.set_content((work2/'index.html').read_text(encoding='utf-8'))
  page.add_style_tag(content=(work2/'style.css').read_text(encoding='utf-8'))
  page.add_script_tag(content=(work2/'game.js').read_text(encoding='utf-8'))
  assert page.locator('#board button').count()==16
  page.locator('#board button.active').click()
  assert page.locator('#count').inner_text()=='1'
  assert not errors,errors
  browser.close()
 server_http.shutdown()
print('Chromium: Minesweeper och generisk HTML5-startprototyp spelar utan JavaScriptfel')
