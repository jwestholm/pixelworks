import unittest, tempfile
from pathlib import Path
from unittest.mock import patch
import server as s

class ChiefReports(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=s.ROOT;self.projects=s.PROJECTS
  s.ROOT=Path(self.t.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'game','name':'Game','idea':'Testspel','genre':'Pussel','platform':'Webbläsare'})
  self.lead=s.hire_codex('game',{'name':'Chef','approval':'HIRE_CODEX_FOR_PROJECT'})
  a=s.staff_read('game');a[0]['role_type']='lead';a[0]['allowed_stations']=['lead'];a[0]['station']='lead';s.staff_write('game',a)
  s.order_action('game',{'station':'qa','instruction':'Undersök fiskebuggen nu','priority':1})
 def tearDown(self):
  s.JOBS.clear();s.DISPATCH_ERRORS.clear();s.ROOT=self.root;s.PROJECTS=self.projects;self.t.cleanup()
 def test_blocked_creates_one_desk_report(self):
  health={'leader_active':True,'waiting':1,'active_jobs':[],'state':'blocked','reason':'Ingen behörig personal', 'blocked':[{'order_id':'ord1','station':'qa','reason':'Saknar QA'}]}
  self.assertIsNotNone(s.chief_block_report('game',health))
  self.assertIsNone(s.chief_block_report('game',health))
  reports=s.list_reports('game');self.assertEqual(len(reports),1)
  self.assertEqual(reports[0]['source'],'studio-dispatch')
  self.assertFalse(reports[0]['read'])
  s.update_report('game',reports[0]['id'],'read');self.assertTrue(s.list_reports('game')[0]['read'])
 def test_different_reason_creates_new_report(self):
  h={'leader_active':True,'waiting':1,'active_jobs':[],'state':'blocked','reason':'A','blocked':[]}
  s.chief_block_report('game',h);h['reason']='B';s.chief_block_report('game',h)
  self.assertEqual(len(s.list_reports('game')),2)
 def test_does_not_report_without_chief_or_while_working(self):
  h={'leader_active':False,'waiting':1,'active_jobs':[],'state':'blocked','reason':'A'}
  self.assertIsNone(s.chief_block_report('game',h));h['leader_active']=True;h['active_jobs']=[{'id':'x'}]
  self.assertIsNone(s.chief_block_report('game',h))
 def test_chief_delegates_worker_when_available(self):
  worker=s.hire_codex('game',{'name':'QA','approval':'HIRE_CODEX_FOR_PROJECT'})
  staff=s.staff_read('game');staff[-1]['allowed_stations']=['qa'];staff[-1]['skills']['testing']=5;s.staff_write('game',staff)
  self.assertEqual(s.dispatch_plan('game')['next']['agent_id'],worker['id'])
 def test_chief_reports_mandate_problem(self):
  with patch.object(s,'status',return_value={'execution_enabled':True}):
   health=s.dispatch_health('game')
  self.assertEqual(health['state'],'mandate_required')
  self.assertIsNotNone(s.chief_block_report('game',health))

if __name__=='__main__':unittest.main()
