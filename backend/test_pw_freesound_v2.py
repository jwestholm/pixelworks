"""Offline regression tests: real dispatch contract mocked; no external calls."""
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
import pw_freesound as f

class Server:
    def __init__(self,root):
        self.ROOT=Path(root)
        self.LOCK=threading.RLock()
        self.JOBS={}
        self.writes=[]
        for name in ('alpha','beta'):
            (self.ROOT/'projects'/name/'management').mkdir(parents=True)
    def validate_slug(self,s):
        if s not in ('alpha','beta'):raise ValueError('project')
        return s
    def verify_project(self,s):self.validate_slug(s)
    def path_for(self,s):return self.ROOT/'projects'/s
    def staff_read(self,s):return [{'id':'a','name':'Alexandra','station':'music','provider':'codex','work_mode':'specialist'}]
    def orders_write(self,slug,orders):self.writes.append((slug,[dict(x) for x in orders]));return 'saved'

class TestToolDispatcher(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.srv=Server(self.tmp.name)
        self.orig_reply=f.real_reply;self.orig_search=f.search_freesound
        f.ACTIVE.clear()
    def tearDown(self):
        f.real_reply=self.orig_reply;f.search_freesound=self.orig_search
        f.ACTIVE.clear();self.tmp.cleanup()
    def verify(self):
        f.set_key(self.srv,'A_VALID_KEY_123456789')
        f.search_freesound=lambda token,query: []
        self.assertTrue(f.test_connection(self.srv)['verified'])
    def test_credential_never_exposed_and_test_replaced(self):
        self.verify()
        self.assertNotIn('A_VALID_KEY_123456789',json.dumps(f.status(self.srv)))
        f.set_key(self.srv,'NEW_VALID_KEY_123456789')
        self.assertFalse(f.status(self.srv)['verified'])
        self.assertTrue(f.status(self.srv)['connected'])
    def test_waiting_has_zero_calls_and_running_is_idempotent(self):
        self.verify()
        count=[]
        def ai(srv,slug,agent,prompt):
            count.append('ai')
            if len(count)==1:return json.dumps({'use_tool':True,'query':'cat meow'})
            return json.dumps({'picks':[{'id':1,'reason':'Ett kort jamande passar katten.'}]})
        f.real_reply=ai
        f.search_freesound=lambda token,query: [{
            'id':1,'name':'Cat meow','license':'CC0','url':'https://freesound.org/people/aa/sounds/1/',
            'username':'aa','preview':'https://cdn.freesound.org/a.mp3','duration':1.2,
            'tags':['cat'],'description':'cat','license_url':'https://creativecommons.org/publicdomain/zero/1.0/'}]
        order={'id':'ord1','station':'music','status':'waiting','instruction':'Hitta ett kort kattljud för pusselspelet', 'job_id':None}
        self.srv.JOBS['core1']={'agent_id':'a','project':'alpha','station':'music','state':'running'}
        self.assertEqual(self.srv.orders_write('alpha',[order]),'saved')
        self.assertEqual(len(count),0)
        f.activate_from_running_orders(self.srv,'alpha',[order])
        self.assertFalse(f.overview(self.srv,'alpha')['jobs'])
        order.update(status='running',job_id='core1')
        f.activate_from_running_orders(self.srv,'alpha',[order])
        f.activate_from_running_orders(self.srv,'alpha',[order])
        for _ in range(80):
            jobs=f.overview(self.srv,'alpha')['jobs']
            if jobs and jobs[0]['status'] != 'running':break
            time.sleep(.02)
        self.assertEqual(len(jobs),1)
        self.assertEqual(jobs[0]['status'],'done',jobs[0].get('error'))
        self.assertEqual(len(jobs[0]['suggestions']),1)
        self.assertEqual(len(count),2)
        self.assertIn('core1',self.srv.JOBS,'Do not delete or complete the real job')
        self.assertFalse(f.overview(self.srv,'beta')['jobs'])
    def test_agent_can_decline_freesound(self):
        self.verify()
        f.real_reply=lambda *args:json.dumps({'use_tool':False})
        f.search_freesound=lambda *args:self.fail('No API request for original composition')
        self.srv.JOBS['core2']={'agent_id':'a','project':'alpha','station':'music','state':'running'}
        f.activate_from_running_orders(self.srv,'alpha',[{'id':'ord2','station':'music','status':'running','job_id':'core2','instruction':'Komponera helt ny unik melodi till spelet'}])
        for _ in range(80):
            jobs=f.overview(self.srv,'alpha')['jobs']
            if jobs and jobs[0]['status']!='running':break
            time.sleep(.02)
        self.assertEqual(jobs[0]['status'],'skipped')
        self.assertIn('core2',self.srv.JOBS)
    def test_install_hook_detects_real_job_once(self):
        self.verify()
        class Handler:
            def do_GET(self): pass
            def do_POST(self): pass
        self.srv.Handler=Handler
        f.real_reply=lambda *args:json.dumps({'use_tool':False})
        f.search_freesound=lambda *args:self.fail('No Freesound search on decline')
        f.install(self.srv)
        self.srv.JOBS['core3']={'agent_id':'a','project':'alpha','station':'music','state':'running'}
        record={'id':'order3','station':'music','status':'waiting','instruction':'Skapa mjukt kattljud för spelet','job_id':None}
        self.srv.orders_write('alpha',[record])
        self.assertEqual(len(f.overview(self.srv,'alpha')['jobs']),0)
        record.update(status='running',job_id='core3')
        self.srv.orders_write('alpha',[record])
        self.srv.orders_write('alpha',[record])
        for _ in range(80):
            jobs=f.overview(self.srv,'alpha')['jobs']
            if jobs and jobs[0]['status']!='running':break
            time.sleep(.02)
        self.assertEqual(len(jobs),1)
        self.assertEqual(jobs[0]['status'],'skipped')
        self.assertIn('core3',self.srv.JOBS)

    def test_install_hooks_original_writer(self):
        self.verify()
        class Handler:
            def do_GET(self):pass
            def do_POST(self):pass
        self.srv.Handler=Handler
        f.install(self.srv)
        self.srv.orders_write('alpha',[{'id':'test','station':'music','status':'waiting'}])
        self.assertEqual(len(self.srv.writes),1)
        self.assertFalse(f.overview(self.srv,'alpha')['jobs'])

if __name__=='__main__':unittest.main(verbosity=2)
