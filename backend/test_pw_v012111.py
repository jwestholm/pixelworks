"""Pixel Works 0.12.11.1 regression coverage; zero network and zero actual AI calls."""
import importlib.util
import json
import stat
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

MODULE=Path(__file__).with_name('pw_v01210.py')
spec=importlib.util.spec_from_file_location('pw11fix',MODULE)
pw=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

class TestGeminiPermissionsAndToken(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        project=root/'projects'/'sample';project.mkdir(parents=True)
        for d in ('management','work','studio-bible'): (project/d).mkdir()
        people=[{'id':'gemini','name':'Gemini','provider':'gemini','role_type':'writer',
                 'station':'cafe','allowed_stations':['docs','research','meeting']},
                {'id':'codex','name':'Codex','provider':'codex','role_type':'programmer',
                 'station':'code','allowed_stations':['code','docs']}]
        srv=SimpleNamespace(ROOT=root,APP=root,PROJECTS=root/'projects',JOBS={},LOCK=threading.RLock(),
            staff_read=lambda slug:people,
            gemini_key_file=lambda:root/'secrets'/'gemini.key',
            provider_status=lambda:{'codex':{}},
            run_codex=lambda *args:None,
            integrate_worker_result=lambda job:(True,'ok'),
            status=lambda:{'execution_enabled':True},
            store_gemini_key=lambda data: (_ for _ in ()).throw(AssertionError('legacy token validator called')),
            agent_authorized=lambda slug,agent,station: agent.get('provider')=='codex' and station in agent.get('allowed_stations',[]),
            assignments_read=lambda slug:{'docs':{'mode':'exclusive','agent_ids':['codex']}},
            dispatch_plan=lambda slug:{'leader_active':False,'assignments':[]},
            Handler=type('Handler',(),{'do_GET':lambda self:None,'do_POST':lambda self:None}),
        )
        pw.install(srv)
        self.srv=srv; self.people=people

    def test_docs_movement_ignores_codex_only_gate_and_hidden_ownership(self):
        g=self.people[0]
        self.assertTrue(self.srv.agent_authorized('sample',g,'docs'))
        self.assertTrue(self.srv.agent_authorized('sample',g,'research'))
        self.assertTrue(self.srv.agent_authorized('sample',g,'meeting'))
        self.assertFalse(self.srv.agent_authorized('sample',g,'code'))
        self.assertFalse(self.srv.agent_authorized('sample',g,'art'))

    def test_other_providers_still_follow_original_rules(self):
        c=self.people[1]
        self.assertTrue(self.srv.agent_authorized('sample',c,'code'))
        self.assertFalse(self.srv.agent_authorized('sample',c,'research'))

    def test_token_saved_without_unreliable_legacy_prefix_check(self):
        fake='TestNotActualGoogleKey0123456789_AA'
        with patch.object(pw,'urlopen',side_effect=AssertionError('no network should happen')):
            saved=self.srv.store_gemini_key({'key':'  '+fake+'  '})
        self.assertTrue(saved['configured'])
        path=self.srv.gemini_key_file()
        self.assertEqual(path.read_text().strip(),fake)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)
        self.assertTrue(pw.gemini_status(self.srv)['configured'])
        self.assertEqual(pw.gemini_status(self.srv)['test_result'],'ej testad')

    def test_obvious_invalid_token_rejected_without_storing_or_network(self):
        with patch.object(pw,'urlopen',side_effect=AssertionError('never request Google')):
            for fake in ('tiny', 'AIza key with spaces', '"quotedToken1234567890123456789"'):
                with self.subTest(fake=fake),self.assertRaises(ValueError):
                    self.srv.store_gemini_key({'key':fake})
        self.assertFalse(self.srv.gemini_key_file().exists())

if __name__=='__main__':unittest.main()
