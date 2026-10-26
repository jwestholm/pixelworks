"""Offline contract tests for v0.12.11.18's safe HTML injection."""
import io
import pathlib
import tempfile
import types
import unittest
from pw_v0121118 import install, VERSION


class Handler:
    def __init__(self):
        self.path='/'
        self.wfile=io.BytesIO()
        self.code=0
        self.headers={}
        self.denied=False
    def allowed(self):return not self.denied
    def reply(self,code,body):self.code=code;return body
    def send_response(self,code):self.code=code
    def send_header(self,key,value):self.headers[key]=value
    def end_headers(self):pass
    def do_GET(self):return 'previous'


class InjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=pathlib.Path(self.tmp.name)
        (self.folder/'index.html').write_text('<html><body><script defer src="./src/pw-v0121117.js"></script></body></html>',encoding='utf-8')
        self.srv=types.SimpleNamespace(Handler=type('IsolatedHandler',(Handler,),{}),APP=self.folder,APP_VERSION='old')
        install(self.srv)
    def test_html_injects_new_script_once_and_last(self):
        h=self.srv.Handler();h.do_GET();self.assertEqual(h.code,200)
        html=h.wfile.getvalue().decode('utf-8')
        self.assertEqual(html.count('src="./src/pw-v0121118.js"'),1)
        self.assertEqual(html.count('src="./src/pw-v0121117.js"'),1)
        self.assertLess(html.index('pw-v0121117.js'),html.index('pw-v0121118.js'))
        self.assertEqual(self.srv.APP_VERSION,VERSION)
        h2=self.srv.Handler();h2.do_GET();self.assertEqual(h2.wfile.getvalue(),h.wfile.getvalue())
    def test_non_root_uses_preexisting_safe_static_handler(self):
        h=self.srv.Handler();h.path='/assets/office-v2/graphics-studio-pastel.png'
        self.assertEqual(h.do_GET(),'previous')
    def test_forbidden_host_cannot_read_html(self):
        h=self.srv.Handler();h.denied=True
        self.assertEqual(h.do_GET()['error'],'Ogiltig host')
        self.assertEqual(h.code,403)
    def test_install_idempotent(self):
        previous=self.srv.Handler.do_GET
        install(self.srv)
        self.assertIs(self.srv.Handler.do_GET,previous)

if __name__=='__main__':unittest.main()
