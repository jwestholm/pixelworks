"""Non-network, non-writing integration contract tests for the UX-stabilization layer."""
import io
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import pw_v0121117 as patch


class FakeHandler:
    def __init__(self):
        self.path='/'
        self.headers={}
        self.wfile=io.BytesIO()
        self.headers_out={}
    def allowed(self):return True
    def reply(self,status,body):return status,body
    def do_GET(self):return 419
    def send_response(self,status):self.status=status
    def send_header(self,key,value):self.headers_out[key]=value
    def end_headers(self):pass


class Tests(unittest.TestCase):
    def test_home_includes_new_script_once_and_preserves_existing_scripts(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'index.html').write_text('<body><p>Original</p></body>')
            srv=types.SimpleNamespace(APP=root,APP_VERSION='old',Handler=type('Handler',(FakeHandler,),{}))
            patch.install(srv)
            h=srv.Handler();h.do_GET()
            content=h.wfile.getvalue().decode()
            self.assertIn('<p>Original</p>',content)
            self.assertEqual(1,content.count('src="./src/pw-v0121117.js"'))
            self.assertEqual(1,content.count('src="./src/pw-v01211.js"'))
            self.assertEqual('0.12.11.17',srv.APP_VERSION)
            self.assertEqual('no-store',h.headers_out['Cache-Control'])
            self.assertEqual(str(len(h.wfile.getvalue())),h.headers_out['Content-Length'])
            patch.install(srv)
            h=srv.Handler();h.do_GET()
            self.assertEqual(1,h.wfile.getvalue().decode().count('pw-v0121117.js'))
    def test_no_new_permissions_or_routes_granted(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'index.html').write_text('<body></body>')
            class Unauthorized(FakeHandler):
                def allowed(self):return False
            srv=types.SimpleNamespace(APP=root,APP_VERSION='old',Handler=type('Handler',(Unauthorized,),{}))
            patch.install(srv)
            h=srv.Handler(); self.assertEqual((403,{'error':'Ogiltig host'}),h.do_GET())
            h=srv.Handler();h.path='/api/projects';self.assertEqual(419,h.do_GET())
    def test_starter_names_are_people_not_provider(self):
        import pw_v01210
        class Roster:
            def __init__(self):self.people=None
            def staff_read(self,slug):return self.people or []
            def staff_write(self,slug,people):self.people=people
        srv=Roster()
        original=pw_v01210.gemini_status
        try:
            pw_v01210.gemini_status=lambda _:{'configured':True}
            pw_v01210.seed_project_staff(srv,'example')
            self.assertEqual(['Chefen','Gunnar','Greta'],[p['name'] for p in srv.people])
            self.assertEqual(['codex','codex','gemini'],[p['provider'] for p in srv.people])
            pw_v01210.seed_project_staff(srv,'example')
            self.assertEqual(3,len(srv.people))
        finally:
            pw_v01210.gemini_status=original

if __name__=='__main__':unittest.main()
