"""Offline decision policy and bounded retry tests, no AI, Freesound or network calls."""
import sys, tempfile, unittest, threading, types
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_decision_center as d

class FakeSrv:
    def __init__(self,root):
        self.ROOT=Path(root)
        self.LOCK=threading.RLock()
        self.orders={'cat':[],'dog':[]}
        self.cases={'cat':[],'dog':[]}
        self.SKILL_STATIONS={'code':'programmering','music':'musik','qa':'test','art':'grafik'}
        for slug in self.orders:(self.ROOT/'projects'/slug/'management').mkdir(parents=True)
    def validate_slug(self,s):
        if s not in self.orders:raise ValueError('Ogiltigt projekt')
        return s
    def verify_project(self,s):self.validate_slug(s)
    def path_for(self,s):return self.ROOT/'projects'/s
    def list_help_cases(self,s):return self.cases[s]
    def orders_read(self,s):return [o.copy() for o in self.orders[s]]
    def orders_write(self,s,arr):self.orders[s]=arr
    def project_mandate(self,s):return {'enabled':True}

class DecisionsTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.s=FakeSrv(self.t.name)
        self.id='a'*12
        self.s.cases['cat']=[{'id':self.id,'agent_name':'Gunnar','state':'failed',
             'station':'code','friendly_reason':'Arbetet kunde inte slutföras','reason':'Test',
             'summary':'Någon skrev samtidigt', 'instruction':'Fixa sprites','created_at':'2026-10-29'}]
        self.access=patch.dict(sys.modules,{'pw_v01210':types.SimpleNamespace(studio_access=lambda server:{'enabled':True})})
        self.access.start()
    def tearDown(self):self.access.stop();self.t.cleanup()
    def test_default_policy_safe_and_revocable(self):
        self.assertEqual(d.settings(self.s),d.DEFAULT)
        out=d.configure(self.s,{'approval':'SET_OWNER_DECISION_POLICY', 'retry_git_conflict_once':False,
                 'auto_retry_transient_once':True})
        self.assertFalse(out['retry_git_conflict_once']);self.assertTrue(out['auto_retry_transient_once'])
        self.assertEqual(out,d.settings(self.s))
        d.configure(self.s,{'approval':'SET_OWNER_DECISION_POLICY','retry_git_conflict_once':False,
                 'auto_retry_transient_once':False})
        self.assertFalse(d.settings(self.s)['auto_retry_transient_once'])
    def test_reject_unauthorized_settings(self):
        with self.assertRaises(ValueError):d.configure(self.s,{'retry_git_conflict_once':True,'auto_retry_transient_once':True})
        with self.assertRaises(ValueError):d.configure(self.s,{'approval':'SET_OWNER_DECISION_POLICY',
             'retry_git_conflict_once':1,'auto_retry_transient_once':False})
    def test_help_only_own_project_and_delay(self):
        self.assertEqual(len(d.cases(self.s,'cat')['cases']),1)
        self.assertEqual(len(d.cases(self.s,'dog')['cases']),0)
        self.assertFalse(d.cases(self.s,'cat')['cases'][0]['deferred'])
        with self.assertRaises(ValueError):d.later(self.s,{'project':'dog','case_id':'help:'+self.id})
        d.later(self.s,{'project':'cat','case_id':'help:'+self.id})
        self.assertTrue(d.cases(self.s,'cat')['cases'][0]['deferred'])
        self.assertEqual(d.cases(self.s,'dog')['cases'],[])
        self.assertTrue((self.s.ROOT/'projects/cat/management/decision-later.json').is_file())
        with patch.object(d.time, 'time', return_value=d.time.time()+d.DELAY+1):
            self.assertFalse(d.cases(self.s,'cat')['cases'][0]['deferred'],
                             'After the delay, the owner must see the help card again')
    def _origin(self,station='code'):
        self.s.orders['cat']=[{'id':'f'*12,'job_id':'e'*12,'station':station,'status':'review',
                 'instruction':'Ändra ett menyflöde i pusselspelet','priority':2,'attachment_ids':[]}]
    def test_git_conflict_retry_once(self):
        self._origin()
        job={'id':'e'*12,'project':'cat','order_id':'f'*12,'state':'review',
             'integration_note':'Arbetet krockar med andra ändringar. Arbetsledaren kunde inte lösa konflikten säkert.'}
        follow=d.retry_once(self.s,job)
        self.assertEqual(follow['status'],'waiting')
        self.assertEqual(follow['parent_report_id'],job['id'])
        self.assertEqual(follow['auto_retry_attempt'],1)
        self.assertIn('senaste',follow['instruction'].lower())
        self.assertEqual(len(self.s.orders['cat']),2)
        self.assertIsNone(d.retry_once(self.s,job))
        again={'id':'b'*12,'project':'cat','order_id':follow['id'],'state':'review',
               'integration_note':'Ändringarna krockar med andra ändringar'}
        self.s.orders['cat'][1].update(status='review',job_id='b'*12)
        self.assertIsNone(d.retry_once(self.s,again),'Never recurse after one automatic attempt')
        self.assertEqual(len(self.s.orders['cat']),2)
    def test_no_retry_without_mandate(self):
        self._origin()
        self.s.project_mandate=lambda _s:{'enabled':False}
        job={'id':'e'*12,'project':'cat','order_id':'f'*12,'state':'review',
             'integration_note':'krockar med andra ändringar'}
        self.assertIsNone(d.retry_once(self.s,job))
    def test_dirty_work_is_not_safe_conflict_retry(self):
        self._origin()
        job={'id':'e'*12,'project':'cat','order_id':'f'*12,'state':'review',
             'integration_note':'Spelets huvudmapp innehåller ändringar.'}
        self.assertIsNone(d.retry_once(self.s,job))
    def test_transient_requires_explicit_opt_in(self):
        self._origin();self.s.orders['cat'][0]['status']='failed'
        job={'id':'e'*12,'project':'cat','order_id':'f'*12,'state':'failed','error':'Jobbet nådde timeout'}
        self.assertIsNone(d.retry_once(self.s,job))
        d.configure(self.s,{'approval':'SET_OWNER_DECISION_POLICY','retry_git_conflict_once':False,
              'auto_retry_transient_once':True})
        self.assertEqual(d.retry_once(self.s,job)['auto_retry_reason'],'transient_failure')
    def test_auto_retry_disabled(self):
        self._origin()
        d.configure(self.s,{'approval':'SET_OWNER_DECISION_POLICY','retry_git_conflict_once':False,
              'auto_retry_transient_once':False})
        job={'id':'e'*12,'project':'cat','order_id':'f'*12,'state':'review','integration_note':'krockar med andra ändringar'}
        self.assertIsNone(d.retry_once(self.s,job))
    def test_reject_symlink_secrets(self):
        (self.s.ROOT/'secrets').symlink_to(self.s.ROOT/'projects',target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'hemlighetskatalog'):
            d.settings(self.s)

if __name__=='__main__':unittest.main()
