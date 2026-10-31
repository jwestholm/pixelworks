"""Real browser fetch of the packaged CSS and character PNG over v3.5.2 HTTP allowlist.
No AI provider requests; no game data is modified.
"""
import sys, json, tempfile, shutil, types, threading, unittest
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
import pw_v352_static

class BrowserAssetRoute(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();root=Path(cls.temp.name)
  for rel in ('src/pw-v35-world.css','src/pw-v351-dialogs.css','src/pw-v352-personnel.css',
              'assets/characters/mira/mira-idle.png','assets/characters/joppe/joppe-walk.png'):
   source=ROOT/rel;target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
  class Handler(SimpleHTTPRequestHandler):
   def __init__(self,*args,**kw):super().__init__(*args,directory=str(root),**kw)
   def allowed(self):return self.headers.get('Host','').startswith('127.0.0.1:')
   def reply(self,status,data):
    raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
   def do_GET(self):return self.reply(404,{'error':'restricted'})
   def end_headers(self):self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
   def log_message(self,*args):pass
  pw_v352_static.install(types.SimpleNamespace(Handler=Handler,SimpleHTTPRequestHandler=SimpleHTTPRequestHandler,APP=root))
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.url=f'http://127.0.0.1:{cls.server.server_port}/'
  cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.server.shutdown();cls.server.server_close();cls.temp.cleanup()
 def test_browser_loads_real_sprite_and_css(self):
  context=self.browser.new_context(viewport={'width':390,'height':844});page=context.new_page()
  page.set_content(f'''<!doctype html><html><head><base href="{self.url}"><link rel="stylesheet" href="src/pw-v352-personnel.css?v=3.5.2"></head><body><img id="sprite" src="assets/characters/mira/mira-idle.png"></body></html>''')
  page.wait_for_function('document.querySelector("#sprite").complete')
  values=page.evaluate('''()=>({image:[document.querySelector('#sprite').naturalWidth,document.querySelector('#sprite').naturalHeight],
     sheets:[...document.styleSheets].some(s=>s.href?.includes('pw-v352-personnel.css'))})''')
  self.assertEqual(values['image'],[192,68]);self.assertTrue(values['sheets']);
  response=page.request.get(self.url+'src/pw-v352-personnel.css?v=3.5.2');self.assertEqual(response.status,200);self.assertIn('text/css',response.headers['content-type']);self.assertIn('.pw352-team-grid',response.text());context.close()

if __name__=='__main__':unittest.main()
