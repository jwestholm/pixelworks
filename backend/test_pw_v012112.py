"""v0.12.11.2 regressions – simulated Google responses, NO actual network."""
import importlib.util
import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError

PATH=Path(__file__).with_name('pw_v01210.py')
spec=importlib.util.spec_from_file_location('pw12fix',PATH)
pw=importlib.util.module_from_spec(spec);spec.loader.exec_module(pw)

class TestGeminiSettings(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name)
        self.srv=SimpleNamespace(ROOT=root,APP=root,PROJECTS=root/'projects',
            JOBS={},LOCK=threading.RLock(),gemini_key_file=lambda:root/'secrets'/'gemini.key',
            provider_status=lambda:{'codex':{}},run_codex=lambda *x:None,
            integrate_worker_result=lambda job:(True,'ok'),status=lambda:{'execution_enabled':True},
            agent_authorized=lambda *a:False,assignments_read=lambda slug:{},
            Handler=type('Handler',(),{'do_GET':lambda self:None,'do_POST':lambda self:None}))
        pw.install(self.srv)
    def test_new_key_alphabet_is_not_rejected_as_invalid_before_google(self):
        with patch.object(pw,'urlopen',side_effect=AssertionError('No HTTP when saving')):
            response=self.srv.store_gemini_key({'key':'  auth.key_2026.0123456-ABC  '})
        self.assertTrue(response['configured'])
        self.assertEqual(self.srv.gemini_key_file().read_text().strip(),'auth.key_2026.0123456-ABC')
    def test_reject_control_and_copy_paste_errors_without_network(self):
        with patch.object(pw,'urlopen',side_effect=AssertionError('Do not call Google')):
            for key in ('', 'short', 'token with spaces 98765', 'abc\n1234567', '"token-abcdef-12345"'):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    self.srv.store_gemini_key({'key':key})
        self.assertFalse(self.srv.gemini_key_file().exists())
    def test_real_model_generation_check_works_for_new_style_key(self):
        self.srv.store_gemini_key({'key':'auth.key_2026.0123456-ABC'})
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return None
            def read(self,n):return json.dumps({'candidates':[{'content':{'parts':[{'text':'OK'}]}}]}).encode()
        def fake_google(req,timeout):
            self.assertEqual(req.get_method(),'POST')
            self.assertIn('/v1beta/models/'+pw.MODEL+':generateContent',req.full_url)
            self.assertIn('x-goog-api-key',dict((k.lower(),v) for k,v in req.header_items()))
            return Response()
        with patch.object(pw,'urlopen',side_effect=fake_google):
            result=pw.test_gemini_connection(self.srv)
        self.assertTrue(result['verified'])
        self.assertEqual(pw.gemini_status(self.srv)['test_result'],'ansluten')
        self.assertEqual(pw.gemini_status(self.srv)['used_today'],1)
    def test_google_rejects_key_with_meaningful_message(self):
        self.srv.store_gemini_key({'key':'auth.key_2026.0123456-ABC'})
        def fake_google(req,timeout):raise HTTPError(req.full_url,403,'forbidden',{},None)
        with patch.object(pw,'urlopen',side_effect=fake_google):
            result=pw.test_gemini_connection(self.srv)
        self.assertFalse(result['verified'])
        self.assertIn('403',result['detail'])
        self.assertNotIn('auth.key_',result['detail'])
    def test_model_with_no_answer_is_not_claimed_verified(self):
        self.srv.store_gemini_key({'key':'auth.key_2026.0123456-ABC'})
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return None
            def read(self,n):return b'{"models":[{"name":"models/another-model","supportedGenerationMethods":["generateContent"]}]}'
        with patch.object(pw,'urlopen',return_value=Response()):
            result=pw.test_gemini_connection(self.srv)
        self.assertFalse(result['verified'])
        self.assertEqual(result['status'],'inget textsvar')

if __name__=='__main__':unittest.main()
