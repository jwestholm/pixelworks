"""No-network regression tests for Pixel Works v0.12.11 onboarding and settings."""
import importlib.util
import io
import hashlib
import json
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pw',ROOT/'pw_v01210.py')
pw=importlib.util.module_from_spec(spec);spec.loader.exec_module(pw)

class Version11Tests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.project=self.root/'projects'/'example';self.project.mkdir(parents=True)
        for n in ('management','studio-bible','work'):(self.project/n).mkdir()
        self.staff=[];self.mandates=[];self.created=[]
        self.srv=SimpleNamespace(ROOT=self.root, APP=self.root, PROJECTS=self.root/'projects',
            JOBS={},LOCK=threading.Lock(),
            create_project=lambda payload:self.created.append(payload) or {'verified':True,'project':{'id':payload['slug']}},
            validate_slug=lambda x:x,verify_project=lambda x:True,
            path_for=lambda x:self.project,
            staff_read=lambda x:self.staff[:],staff_write=lambda x,people:self.staff.extend(people),
            set_project_mandate=lambda slug,payload:self.mandates.append((slug,payload)),
            gemini_key_file=lambda:self.root/'secrets'/'gemini.key')
    def set_key(self):
        (self.root/'secrets').mkdir(exist_ok=True)
        self.srv.gemini_key_file().write_text('AIzaTestFakeKeyForOfflineOnly',encoding='utf-8')
    def test_starter_team_always_has_chief_and_programmer(self):
        team=pw.seed_project_staff(self.srv,'example')
        self.assertEqual(len(team),2)
        self.assertEqual(self.staff[0]['station'],'lead')
        self.assertEqual(self.staff[1]['station'],'code')
        self.assertEqual(pw.seed_project_staff(self.srv,'example'),[])
        self.assertEqual(len(self.staff),2)
    def test_existing_staff_never_overwritten(self):
        self.staff.append({'name':'Existing','id':'legacy'})
        self.assertEqual(pw.seed_project_staff(self.srv,'example'),[])
        self.assertEqual(len(self.staff),1)
    def test_saved_token_adds_gemini_to_new_project(self):
        self.set_key()
        ids=pw.seed_project_staff(self.srv,'example')
        self.assertEqual(len(ids),3)
        self.assertEqual(self.staff[2]['provider'],'gemini')
        self.assertIn('docs',self.staff[2]['allowed_stations'])
    def test_config_token_can_be_displayed_without_external_network(self):
        self.set_key()
        with patch.object(pw,'urlopen',side_effect=AssertionError('unexpected HTTP')):
            status=pw.gemini_status(self.srv)
        self.assertTrue(status['configured'])
        self.assertEqual(status['test_result'],'ej testad')
    def test_connection_test_generates_real_short_text(self):
        self.set_key()
        class Response:
            def __enter__(self):return self
            def __exit__(self,*a):return None
            def read(self,n):return b'{"candidates":[{"content":{"parts":[{"text":"OK"}]}}]}'
        def fetch(req,timeout):
            self.assertEqual(req.get_method(),'POST')
            self.assertIn('models/'+pw.MODEL+':generateContent',req.full_url)
            return Response()
        with patch.object(pw,'urlopen',side_effect=fetch):
            out=pw.test_gemini_connection(self.srv)
        self.assertTrue(out['verified'])
        self.assertEqual(pw.gemini_status(self.srv)['test_result'],'ansluten')
        self.assertEqual(pw.gemini_status(self.srv)['used_today'],1)
        self.srv.gemini_key_file().write_text('AIzaSomeOtherFakeKeyForTests',encoding='utf-8')
        self.assertEqual(pw.gemini_status(self.srv)['test_result'],'ej testad')
    def test_429_validation_does_not_generate_content(self):
        self.set_key()
        from urllib.error import HTTPError
        def reject(req,timeout):raise HTTPError(req.full_url,429,'rate limit',{},None)
        with patch.object(pw,'urlopen',side_effect=reject):
            out=pw.test_gemini_connection(self.srv)
        self.assertEqual(out['status'],'kvotgräns nådd')
    def test_import_does_not_call_external_services(self):
        with patch.object(pw,'urlopen',side_effect=AssertionError('unexpected network')):
            self.assertEqual(pw.gemini_status(self.srv)['configured'],False)
    def test_server_launcher_fails_closed_without_git(self):
        spec=importlib.util.spec_from_file_location('pw_launcher',ROOT/'server.py')
        launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
        with patch.object(launcher,'ROOT',self.root):
            with self.assertRaisesRegex(RuntimeError,'Git-klonen'):
                launcher.load_base()
    def test_server_launcher_loads_exact_local_git_blob(self):
        spec=importlib.util.spec_from_file_location('pw_launcher2',ROOT/'server.py')
        launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        file=self.root/'original.py'
        file.write_text('ANSWER=42\n',encoding='utf-8')
        sha=subprocess.check_output(['git','-C',str(self.root),'hash-object','-w',str(file)],text=True).strip()
        with patch.object(launcher,'ROOT',self.root),patch.object(launcher,'ORIGINAL_SHA',sha):
            module=launcher.load_base()
        self.assertEqual(module.ANSWER,42)
        file.write_text('WRONG=99\n',encoding='utf-8')
        with patch.object(launcher,'ROOT',self.root),patch.object(launcher,'ORIGINAL_SHA',sha):
            module=launcher.load_base()
        self.assertEqual(module.ANSWER,42)
    def test_dispatch_prefers_gemini_for_documentation(self):
        self.set_key()
        self.staff.extend([{'id':'g','provider':'gemini','allowed_stations':['docs'],'role_type':'writer'},
                           {'id':'c','provider':'codex','allowed_stations':['docs'],'role_type':'programmer'}])
        self.srv.dispatch_plan=lambda slug:{'leader_active':True,'next':{'agent_id':'c'},'assignments':[{'agent_id':'c','station':'docs'}]}
        self.srv.Handler=type('FakeHandler',(),{'do_GET':lambda self:None,'do_POST':lambda self:None})
        self.srv.provider_status=lambda:{'codex':{}}
        self.srv.store_gemini_key=lambda p:{'configured':True}
        pw._write_json(pw._cfg_file(self.srv), {'tested_model':pw.MODEL,
            'tested_key_sha256':hashlib.sha256(self.srv.gemini_key_file().read_bytes()).hexdigest(),
            'test_result':'ansluten'})
        self.srv.run_codex=lambda *args:None
        self.srv.integrate_worker_result=lambda x:True
        self.srv.status=lambda:{'execution_enabled':True}
        pw.install(self.srv)
        planned=self.srv.dispatch_plan('example')
        self.assertEqual(planned['assignments'],[])
        self.assertIsNone(planned['next'])

if __name__=='__main__':unittest.main()
