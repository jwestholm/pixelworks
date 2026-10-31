"""No real provider, Freesound or browser calls; all effects use in-memory fakes."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import pw_tool_registry as reg
import pw_qa_handoff as qa
import pw_freesound as sound

class Fake:
    def __init__(self,root):
        self.ROOT=Path(root)
        self.LOCK=threading.RLock();self.JOBS={};self.order_map={'alpha':[],'beta':[]};self.calls=[]
        (self.ROOT/'projects'/'alpha'/'management').mkdir(parents=True)
        (self.ROOT/'projects'/'beta'/'management').mkdir(parents=True)
        class Handler:
            def do_GET(self):return ('old',)
        self.Handler=Handler
    def validate_slug(self,s):
        if s not in ('alpha','beta'):raise ValueError('Okänt projekt')
        return s
    def verify_project(self,s):self.validate_slug(s)
    def path_for(self,s):return self.ROOT/'projects'/s
    def staff_read(self,s):return [{'id':'gunnar','station':'music','provider':'codex','work_mode':'specialist'}]
    def orders_read(self,s):return [dict(x) for x in self.order_map[s]]
    def orders_write(self,s,rows):self.order_map[s]=[dict(x) for x in rows];return None
    def finalize_worker_job(self,j):
        self.calls.append(j['id']);return True

class ToolBridgeTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.s=Fake(self.temp.name);sound.set_key(self.s,'TestSecretKey123456789');sound.ACTIVE.clear()
    def tearDown(self):self.temp.cleanup();sound.ACTIVE.clear()
    def test_unverified_key_not_a_tool(self):
        broker=reg.install(self.s)
        self.assertEqual(broker.list('alpha')[0]['available'],False)
        with self.assertRaises(ValueError):broker.call('alpha',{'id':'gunnar','station':'music'},'freesound','audio.search',{'query':'cat meow'})
    def test_verified_tool_and_project_scope(self):
        broker=reg.install(self.s)
        with patch.object(sound,'search_freesound',return_value=[{'id':3}]) as mock:
            sound.test_connection(self.s)
            self.assertTrue(broker.list('alpha')[0]['available'])
            result=broker.call('alpha',{'id':'gunnar','station':'music'},'freesound','audio.search',{'query':'cat meow'})
            self.assertEqual(result,[{'id':3}]);self.assertEqual(mock.call_count,2)
        for agent,tool,operation,slug in [({'id':'gunnar','station':'code'},'freesound','audio.search','alpha'),({'id':'gunnar','station':'music'},'freesound','delete','alpha'),({'id':'gunnar','station':'music'},'freesound','audio.search','invalid')]:
            with self.assertRaises(ValueError):broker.call(slug,agent,tool,operation,{'query':'cat meow'})
        self.assertNotIn('TestSecretKey123456789',json.dumps(broker.list('alpha')))
    def test_qa_only_integrated_job_not_tested(self):
        self.s.order_map['alpha']=[{'id':'orig','job_id':'a'*12,'status':'done','instruction':'Lägg till musikfunktion i spelet'}]
        qa.install(self.s)
        job={'id':'a'*12,'order_id':'orig','station':'music','project':'alpha','state':'done','integrated':True}
        self.assertTrue(self.s.finalize_worker_job(job))
        self.assertEqual(len(self.s.order_map['alpha']),2)
        row=self.s.order_map['alpha'][1]
        self.assertEqual(row['status'],'waiting');self.assertFalse(row['independently_verified'])
        self.assertEqual(row['qa_for_job'],job['id'])
        self.assertIn('EJ TESTAT',row['instruction'])
        self.s.finalize_worker_job(job)
        self.assertEqual(len(self.s.order_map['alpha']),2,'Idempotent QA handoff')
        self.assertEqual(len(qa.status(self.s,'alpha',job['id'])['handoffs']),1)
        self.assertEqual(len(qa.status(self.s,'beta',job['id'])['handoffs']),0)
    def test_qa_never_self_triggers_or_for_failed_or_unrelated(self):
        self.s.order_map['alpha']=[{'id':'orig','job_id':'a'*12,'status':'done','instruction':'Instruktion'}]
        for station in ('qa','docs','research'):
            self.assertIsNone(qa.handoff(self.s,{'id':'a'*12,'order_id':'orig','station':station,'project':'alpha','state':'done','integrated':True}))
        self.assertIsNone(qa.handoff(self.s,{'id':'a'*12,'order_id':'orig','station':'code','project':'alpha','state':'failed','integrated':False}))
        self.assertIsNone(qa.handoff(self.s,{'id':'b'*12,'order_id':'orig','station':'code','project':'alpha','state':'done','integrated':True}))
        self.assertEqual(len(self.s.order_map['alpha']),1)
    def test_report_is_not_marked_verified_even_after_qa_done(self):
        self.s.order_map['alpha']=[{'id':'q1','qa_for_job':'a'*12,'status':'done','independently_verified':False}]
        x=qa.status(self.s,'alpha','a'*12)
        self.assertFalse(x['handoffs'][0]['independently_verified'])
        self.assertIn('inte oberoende verifierat', x['warning'])

if __name__=='__main__':unittest.main(verbosity=2)
