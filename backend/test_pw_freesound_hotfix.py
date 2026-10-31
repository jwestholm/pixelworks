"""Regression: Freesound server access injected into actual authorized Codex job; offline only."""
from __future__ import annotations
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import pw_freesound as f
import pw_tool_registry as reg

KEY='privateFreesoundKey123456789'
class Fake:
    def __init__(self, root):
        self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={};self.orders={};self.calls=[]
        for slug in ('alpha','beta'):(self.ROOT/'projects'/slug/'management').mkdir(parents=True)
        class Handler:
            def do_GET(self):return 'old-get'
            def do_POST(self):return 'old-post'
        self.Handler=Handler
    def validate_slug(self,slug):
        if slug not in ('alpha','beta'):raise ValueError('Ogiltigt projekt')
        return slug
    def verify_project(self,slug):self.validate_slug(slug)
    def path_for(self,slug):return self.ROOT/'projects'/slug
    def staff_read(self,slug):return [{'id':'agent1','name':'Chefen','station':'music','provider':'codex','work_mode':'specialist'}]
    def orders_read(self,slug):return [dict(o) for o in self.orders.get(slug,[])]
    def orders_write(self,slug,orders):self.orders[slug]=[dict(o) for o in orders]
    def run_codex(self,jid,slug,instruction):
        self.calls.append((jid,slug,instruction))
        return {'passed':True}
    def approved(self,slug='alpha',id='c'*12):
        self.JOBS[id]={'id':id,'project':slug,'station':'music','agent_id':'agent1','state':'queued','order_id':'ord1'}
        self.orders[slug]=[{'id':'ord1','job_id':id,'station':'music','status':'running','instruction':'Hitta mjukt kattljud till pusselspelet'}]
        return id

class HotfixTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.s=Fake(self.temp.name)
        f.ACTIVE.clear()
        f.set_key(self.s,KEY)
        with patch.object(f,'search_freesound',return_value=[]):f.test_connection(self.s)
        reg.install(self.s)
        self.orig_search=f.search_freesound
        self.orig_ai=f.real_reply
    def tearDown(self):
        f.search_freesound=self.orig_search
        f.real_reply=self.orig_ai
        f.ACTIVE.clear()
        self.temp.cleanup()
    def install(self):f.install(self.s)
    def candidates(self):
        return [{'id':1,'name':'Cat meow','username':'artist','license':'CC0',
                 'license_url':'https://creativecommons.org/publicdomain/zero/1.0/',
                 'url':'https://freesound.org/people/artist/sounds/1/',
                 'preview':'https://cdn.freesound.org/a.mp3', 'description':'small cat sound',
                 'duration':1.2,'tags':['cat']}]
    def test_real_worker_receives_server_owned_results_before_running(self):
        self.s.approved();asked=[]
        def reply(*args):
            asked.append(args[-1])
            return json.dumps({'tool':'freesound','query':'soft kitten meow'}) if len(asked)==1 else json.dumps({'picks':[{'id':1,'reason':'Kattmjau passar det sökta ljudet'}]})
        f.real_reply=reply
        def search(token,query):
            self.assertEqual(token,KEY)
            self.assertEqual(query,'soft kitten meow')
            self.assertFalse(self.s.calls,'Freesound must finish before ordinary code worker')
            return self.candidates()
        f.search_freesound=search
        self.install()
        self.assertEqual(self.s.run_codex('c'*12,'alpha','Gör ljudeffekter'),{'passed':True})
        self.assertEqual(len(asked),2)
        self.assertEqual(len(self.s.calls),1)
        injected=self.s.calls[0][2]
        self.assertIn('soft kitten meow',injected)
        self.assertIn('Cat meow',injected)
        self.assertIn('Försök INTE söka Freesound',injected)
        self.assertNotIn(KEY,injected)
        rec=f.overview(self.s,'alpha')['jobs'][0]
        self.assertEqual(rec['status'],'done')
        self.assertEqual(rec['core_job_id'],'c'*12)
        self.assertTrue(any(e['kind']=='request' for e in rec['tool_events']))
    def test_no_job_or_waiting_order_cannot_trigger_api(self):
        self.install();self.s.JOBS['c'*12]={'id':'c'*12,'project':'alpha','station':'music','state':'queued','order_id':'ord1','agent_id':'agent1'}
        self.s.orders['alpha']=[{'id':'ord1','job_id':'c'*12,'status':'waiting','station':'music'}]
        f.search_freesound=lambda *args:self.fail('Waiting order must not search')
        self.s.run_codex('c'*12,'alpha','Väntande')
        self.assertEqual(self.s.calls[-1][-1],'Väntande')
        self.assertEqual(f.overview(self.s,'alpha')['jobs'],[])
    def test_missing_key_does_not_launch_tool(self):
        self.s.approved();self.install()
        f.key_path(self.s).unlink();f.remove_connection_test(self.s)
        f.search_freesound=lambda *args:self.fail('No key')
        self.s.run_codex('c'*12,'alpha','Ljud')
        self.assertIn('API-nyckel saknas',self.s.calls[-1][-1])
    def test_unverified_key_does_not_launch_tool(self):
        self.s.approved();self.install()
        f.remove_connection_test(self.s)
        f.search_freesound=lambda *args:self.fail('Unverified key')
        self.s.run_codex('c'*12,'alpha','Ljud')
        self.assertIn('inte anslutningstestat',self.s.calls[-1][-1])
    def test_agent_can_decline_tool_without_search(self):
        self.s.approved();self.install()
        f.real_reply=lambda *args:json.dumps({'tool':None})
        f.search_freesound=lambda *args:self.fail('Agent declined tool')
        self.s.run_codex('c'*12,'alpha','Komponera originalmelodi')
        self.assertEqual(f.overview(self.s,'alpha')['jobs'][0]['status'],'skipped')
    def test_tool_failure_does_not_fake_success_or_stop_core(self):
        self.s.approved();self.install()
        f.real_reply=lambda *args:json.dumps({'tool':'freesound','query':'cat meow'})
        f.search_freesound=lambda *args:(_ for _ in ()).throw(RuntimeError('API svarade 429'))
        self.s.run_codex('c'*12,'alpha','Ljud')
        self.assertIn('API svarade 429',self.s.calls[-1][-1])
        self.assertEqual(f.overview(self.s,'alpha')['jobs'][0]['status'],'failed')
    def test_same_core_job_idempotent(self):
        self.s.approved();self.install()
        f.real_reply=lambda *args:json.dumps({'tool':None})
        self.s.run_codex('c'*12,'alpha','Ljud')
        self.s.run_codex('c'*12,'alpha','Ljud')
        self.assertEqual(len(f.overview(self.s,'alpha')['jobs']),1)
    def test_unrelated_station_and_project_isolation(self):
        self.s.approved();self.install()
        self.s.JOBS['c'*12]['station']='code'
        f.real_reply=lambda *args:self.fail('Not audio')
        self.s.run_codex('c'*12,'alpha','Skriv kod')
        self.assertEqual(self.s.calls[-1][-1],'Skriv kod')
        self.assertEqual(f.overview(self.s,'beta')['jobs'],[])
    def test_api_v2_authenticated_search_contract(self):
        from unittest.mock import patch
        from urllib.parse import urlparse, parse_qs
        class Response:
            status=200
            def read(self, limit):
                return json.dumps({'results':[{'id':14,'name':'Cat meow','username':'artist',
                    'license':'https://creativecommons.org/publicdomain/zero/1.0/',
                    'previews':{'preview-hq-mp3':'https://cdn.freesound.org/preview.mp3'},
                    'duration':1.5,'description':'A cat meowing','tags':['cat']}]}).encode()
            def __enter__(self):return self
            def __exit__(self,*args):return False
        class Opener:
            def open(self,req,timeout):
                address=urlparse(req.full_url)
                self_inner=self
                assert address.scheme=='https' and address.netloc=='freesound.org'
                assert address.path=='/apiv2/search/'
                query=parse_qs(address.query)
                assert query['query']==['cat meow']
                assert 'previews' in query['fields'][0]
                assert req.get_header('Authorization')=='Token '+KEY
                assert timeout>0
                return Response()
        with patch.object(f,'build_opener',return_value=Opener()):
            found=f.search_freesound(KEY,'cat meow')
        self.assertEqual(found[0]['license'],'CC0')
        self.assertEqual(found[0]['name'],'Cat meow')
        self.assertTrue(found[0]['preview'].startswith('https://'))
    def test_dns_error_is_server_specific(self):
        import socket
        from urllib.error import URLError
        from unittest.mock import patch
        class Opener:
            def open(self,req,timeout):raise URLError(socket.gaierror(-2,'Name not known'))
        with patch.object(f,'build_opener',return_value=Opener()):
            with self.assertRaisesRegex(RuntimeError,'Pixel Works-servern.*DNS'):
                f.search_freesound(KEY,'cat meow')
    def test_http_authentication_failure_remains_distinct(self):
        from urllib.error import HTTPError
        from unittest.mock import patch
        class Opener:
            def open(self,req,timeout):raise HTTPError(req.full_url,401,'Unauthorized',{},None)
        with patch.object(f,'build_opener',return_value=Opener()):
            with self.assertRaisesRegex(RuntimeError,'avvisade API-nyckeln'):
                f.search_freesound(KEY,'cat meow')
    def test_status_never_contains_api_key(self):
        self.assertNotIn(KEY,json.dumps(f.status(self.s)))
    def test_verification_is_key_bound(self):
        self.assertTrue(f.verified_key(self.s))
        f.set_key(self.s,'NewPrivateToken123456789')
        self.assertFalse(f.verified_key(self.s))
if __name__=='__main__':unittest.main(verbosity=2)
