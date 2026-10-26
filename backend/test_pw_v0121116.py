"""Regression checks: chief retry never duplicates or bypasses busy workers."""
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent))
import pw_v0121116 as mod
import pw_v0121112 as dispatcher
import pw_v0121111 as staffplan


class Studio:
    def __init__(self,root):
        self.root=Path(root)
        self.LOCK=threading.RLock()
        self.JOBS={}
        self.orders=[{'id':'b'*12,'station':'docs','status':'waiting','instruction':'Write documentation','priority':2,'created_at':'2026-10-23'}]
        self.people=[{'id':'gunnar','name':'Gunnar','station':'cafe','provider':'codex'}]
        self.moves=[]
        self.report={'id':'a'*12,'source':'studio-dispatch','project':'my-game','archived':False,'summary':'Berörda uppdrag: docs ('+'b'*12+'): projektmapp upptagen'}
        (self.root/'reports').mkdir()
        self.path=self.root/'reports'/('a'*12+'.json')
        self.store()
    def store(self):self.path.write_text(json.dumps(self.report),encoding='utf8')
    def validate_slug(self,x):
        if x!='my-game':raise ValueError('Ogiltigt projekt')
        return x
    def report_path(self,slug,rid):return self.root/'reports'/(rid+'.json')
    def orders_read(self,slug):return self.orders
    def staff_read(self,slug):return self.people
    def move_staff(self,slug,payload):
        self.moves.append((payload['agent_id'],payload['station']))
        self.people[0]['station']=payload['station']


class ChiefRetry(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.s=Studio(self.temp.name)
        self.body={'project':'my-game','report_id':'a'*12}
        self.selector=patch.object(staffplan,'selection',return_value=self.s.people[0]);self.selector.start();self.addCleanup(self.selector.stop)
    def test_can_find_original_waiting_order(self):
        self.assertEqual(mod.report_orders(self.s,'my-game','a'*12)[0]['id'],'b'*12)
    def test_archived_report_cannot_retry(self):
        self.s.report['archived']=True;self.s.store()
        with self.assertRaisesRegex(ValueError,'arkiverad'):mod.report_orders(self.s,'my-game','a'*12)
    def test_non_chief_report_cannot_retry(self):
        self.s.report['source']='gemini-api';self.s.store()
        with self.assertRaisesRegex(ValueError,'endast arbetsledarens'):mod.report_orders(self.s,'my-game','a'*12)
    def test_unrelated_order_cannot_be_dispatched(self):
        self.s.orders.append({'id':'c'*12,'station':'docs','status':'waiting'})
        with self.assertRaisesRegex(ValueError,'inte längre'):mod.retry(self.s,{**self.body,'order_id':'c'*12})
    def test_completed_order_no_duplicate(self):
        self.s.orders[0]['status']='done'
        with patch.object(dispatcher,'dispatch_person',side_effect=AssertionError('should not dispatch')):
            self.assertEqual(mod.retry(self.s,self.body)['state'],'idle')
    def test_busy_direct_writer_does_not_touch_worker_or_dispatch(self):
        self.s.JOBS['other']={'project':'my-game','state':'running','agent_id':'somebody','provider':'codex','isolated':False}
        with patch.object(dispatcher,'dispatch_person',side_effect=AssertionError('should not dispatch')):
            result=mod.retry(self.s,self.body)
        self.assertEqual(result['state'],'blocked');self.assertIn('spelmappen',result['message']);self.assertFalse(self.s.moves)
        self.assertEqual(self.s.orders[0]['status'],'waiting')
    def test_retry_when_free_uses_exact_order_and_restores_position_on_block(self):
        with patch.object(dispatcher,'dispatch_person',return_value={'state':'blocked','message':'Kvotfel'}) as send:
            result=mod.retry(self.s,self.body)
        self.assertEqual(result['state'],'blocked')
        self.assertEqual(send.call_args.kwargs['order_id'],'b'*12)
        self.assertEqual(self.s.moves,[('gunnar','docs'),('gunnar','cafe')])
    def test_successful_job_stays_at_station(self):
        def start(*args,**kwargs):
            self.s.JOBS['job']={'project':'my-game','state':'queued','agent_id':'gunnar','provider':'codex','isolated':True}
            self.s.orders[0]['status']='running'
            return {'state':'started','job_id':'job','message':'Gunnar arbetar.'}
        with patch.object(dispatcher,'dispatch_person',side_effect=start):
            result=mod.retry(self.s,self.body)
        self.assertEqual(result['state'],'started')
        self.assertEqual(self.s.moves,[('gunnar','docs')])
        self.assertEqual(self.s.orders[0]['status'],'running')
    def test_busy_selected_worker_does_not_move(self):
        self.s.JOBS['job']={'project':'my-game','state':'queued','agent_id':'gunnar','provider':'codex','isolated':True}
        with patch.object(dispatcher,'dispatch_person',side_effect=AssertionError('should not dispatch')):
            result=mod.retry(self.s,self.body)
        self.assertEqual(result['state'],'blocked');self.assertEqual(self.s.moves,[])
    def test_many_orders_require_explicit_selection(self):
        self.s.report['summary']+='; docs ('+'c'*12+'): blocked';self.s.store()
        self.s.orders.append({'id':'c'*12,'station':'docs','status':'waiting','priority':3})
        with patch.object(dispatcher,'dispatch_person',side_effect=AssertionError('no dispatch yet')):
            result=mod.retry(self.s,self.body)
        self.assertEqual(result['state'],'choose');self.assertEqual(len(result['orders']),2)
    def test_invalid_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Ogiltigt rapport-ID'):
            mod.report_orders(self.s,'my-game','../passwd')

if __name__=='__main__':unittest.main()
