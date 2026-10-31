"""v3.5.2 HTTP regression: the real static assets must not silently be JSON 404."""
import sys, tempfile, threading, types, unittest, json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen,Request
from urllib.error import HTTPError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import pw_v352_static

class StaticRoutes(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.folder=tempfile.TemporaryDirectory();root=Path(cls.folder.name);cls.root=root
  for f in ['src/pw-v35-world.css','src/pw-v351-dialogs.css','src/pw-v352-personnel.css','src/pw-v353-office.css',
            'assets/characters/mira/mira-idle.png','assets/characters/joppe/joppe-walk.png',
            'backend/server.py','secrets/private.key']:
   target=root/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'CSS-OK' if f.endswith('.css') else b'\x89PNG\r\n' if f.endswith('.png') else b'NEVER-LEAK')
  class Handler(SimpleHTTPRequestHandler):
   def __init__(self,*a,**kw):super().__init__(*a,directory=str(root),**kw)
   def allowed(self):return self.headers.get('Host','').startswith('127.0.0.1:')
   def reply(self,status,data):
    raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
   def end_headers(self):
    self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
   def do_GET(self):return self.reply(404,{'error':'not-allowlisted'})
   def log_message(self,*a):pass
  cls.srv=types.SimpleNamespace(Handler=Handler,SimpleHTTPRequestHandler=SimpleHTTPRequestHandler,APP=root)
  pw_v352_static.install(cls.srv)
  cls.http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
  cls.base=f'http://127.0.0.1:{cls.http.server_port}'
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.folder.cleanup()
 def get(self,path,host=None):
  req=Request(self.base+path,headers=({'Host':host} if host else {}))
  try:
   with urlopen(req,timeout=2) as response:return response.status,response.headers,response.read()
  except HTTPError as e:return e.code,e.headers,e.read()
 def test_css_mime_and_no_store(self):
  for path in ('/src/pw-v35-world.css','/src/pw-v351-dialogs.css','/src/pw-v352-personnel.css','/src/pw-v353-office.css'):
   with self.subTest(path=path):
    code,head,body=self.get(path+'?v=3.5.2');self.assertEqual(code,200);self.assertIn('text/css',head['Content-Type']);self.assertEqual(head['Cache-Control'],'no-store');self.assertEqual(body,b'CSS-OK')
 def test_character_png(self):
  for path in ('/assets/characters/mira/mira-idle.png','/assets/characters/joppe/joppe-walk.png'):
   code,head,body=self.get(path);self.assertEqual(code,200);self.assertIn('image/png',head['Content-Type']);self.assertTrue(body.startswith(b'\x89PNG'))
 def test_reject_non_allowlisted_files(self):
  for path in ('/backend/server.py','/secrets/private.key','/src/other.css','/assets/characters/mira/mira-notreal.png','/assets/characters/mira/mira-idle.png/../../../../backend/server.py','/assets/characters/chef/chef-evil.png'):
   with self.subTest(path=path):self.assertNotEqual(self.get(path)[0],200)
 def test_bad_host_denied(self):self.assertEqual(self.get('/src/pw-v35-world.css',host='untrusted.example')[0],403)
 def test_symlink_refused(self):
  path=self.root/'assets/characters/vera/vera-idle.png';path.parent.mkdir(parents=True,exist_ok=True);path.symlink_to(self.root/'backend/server.py')
  try:self.assertEqual(self.get('/assets/characters/vera/vera-idle.png')[0],404)
  finally:path.unlink()
 def test_idempotent_install(self):
  previous=self.srv.Handler.do_GET;pw_v352_static.install(self.srv);self.assertIs(self.srv.Handler.do_GET,previous)

if __name__=='__main__':unittest.main()
