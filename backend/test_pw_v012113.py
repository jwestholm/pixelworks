"""0.12.11.3: Model 404 regression and real-generation verification. All HTTP is mocked."""
import hashlib
import importlib.util
import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError

BASE=Path(__file__).with_name('pw_v01210.py')
spec=importlib.util.spec_from_file_location('pw113',BASE)
pw=importlib.util.module_from_spec(spec);spec.loader.exec_module(pw)

class FakeResponse:
    def __init__(self,text='OK'):
        self.data=json.dumps({'candidates':[{'content':{'parts':[{'text':text}]}}]}).encode()
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):return self.data[:n]

class Gemini404Regression(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
        base=Path(temp.name);secret=base/'secrets';secret.mkdir()
        (secret/'gemini.key').write_text('OnlyFakeKeyForTestNoRemoteCalls_2026')
        self.srv=SimpleNamespace(ROOT=base,PROJECTS=base/'projects',JOBS={},LOCK=threading.RLock(),
                                 gemini_key_file=lambda:secret/'gemini.key')
    def test_token_or_legacy_metadata_success_never_starts_workers(self):
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
        keyhash=hashlib.sha256(self.srv.gemini_key_file().read_bytes()).hexdigest()
        pw._write_json(pw._cfg_file(self.srv),{'tested_key_sha256':keyhash,
                         'test_result':'ansluten','tested_model':'gemini-2.5-flash'})
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
    def test_generate_content_request_is_required_and_quota_counted(self):
        with patch.object(pw,'urlopen',return_value=FakeResponse('OK')) as call:
            value=pw.test_gemini_connection(self.srv)
        self.assertTrue(value['verified'])
        self.assertEqual(pw.gemini_status(self.srv)['model'],'gemini-3.5-flash-lite')
        self.assertEqual(pw.gemini_status(self.srv)['used_today'],1)
        self.assertTrue(pw.gemini_status(self.srv)['can_send'])
        req=call.call_args[0][0]
        self.assertEqual(req.get_method(),'POST')
        self.assertEqual(req.full_url,pw.GEMINI_URL)
        self.assertLessEqual(len(req.data),1024)
        self.assertNotIn('2.5-flash',req.full_url)
    def test_http404_is_not_a_valid_connection_even_with_correct_key(self):
        def not_found(req,timeout):raise HTTPError(req.full_url,404,'model not accessible',{},None)
        with patch.object(pw,'urlopen',side_effect=not_found) as mock:
            value=pw.test_gemini_connection(self.srv)
        self.assertEqual(mock.call_count,1)
        self.assertEqual(value['status'],'modellen nekas (404)')
        self.assertFalse(value['verified'])
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
        self.assertEqual(pw.gemini_status(self.srv)['used_today'],1)
        self.assertNotIn('OnlyFakeKey',value['detail'])
    def test_successful_new_test_clears_previous_model_pause_without_resetting_quota(self):
        pw._write_json(pw._cfg_file(self.srv),{'paused_until_day':pw.google_day(),
                       'pause_reason':'Gemini 2.5 svarade HTTP 404'})
        with patch.object(pw,'urlopen',return_value=FakeResponse('OK')):
            v=pw.test_gemini_connection(self.srv)
        self.assertTrue(v['verified'])
        self.assertIsNone(pw.gemini_status(self.srv)['paused_until_day'])
        self.assertTrue(pw.gemini_status(self.srv)['can_send'])
    def test_previously_failed_no_text_test_never_dispatches(self):
        with patch.object(pw,'urlopen',return_value=FakeResponse('  ')):
            v=pw.test_gemini_connection(self.srv)
        self.assertFalse(v['verified'])
        self.assertEqual(v['status'],'inget textsvar')
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
    def test_daily_limit_blocks_test_without_http(self):
        pw._write_json(pw._counter_file(self.srv),{'date':pw.google_day(),'count':12})
        with patch.object(pw,'urlopen',side_effect=AssertionError('NO CALL')):
            v=pw.test_gemini_connection(self.srv)
        self.assertEqual(v['status'],'kvotgräns nådd')
    def test_health_overrides_misleading_codex_only_message(self):
        jobs=[]
        staff=[{'id':'boss','provider':'codex','role_type':'lead','station':'lead'},
               {'id':'gemini','provider':'gemini','role_type':'writer','station':'docs',
                'allowed_stations':['docs']}]
        orders=[{'id':'order','status':'waiting','station':'docs'}]
        self.srv.staff_read=lambda slug:staff
        self.srv.orders_read=lambda slug:orders
        self.srv.provider_status=lambda:{'codex':{}}
        self.srv.run_codex=lambda *x:None
        self.srv.integrate_worker_result=lambda job:(True,'ok')
        self.srv.status=lambda:{'execution_enabled':True}
        self.srv.agent_authorized=lambda *args:True
        self.srv.dispatch_health=lambda slug:{'leader_active':True,'state':'blocked','reason':'Ingen Codex-anställd'}
        self.srv.Handler=type('Handler',(),{'do_GET':lambda self:None,'do_POST':lambda self:None})
        pw.install(self.srv)
        state=self.srv.dispatch_health('demo')
        self.assertEqual(state['state'],'gemini_test_required')
        self.assertIn('Testa/verifiera',state['reason'])

if __name__=='__main__':unittest.main()
