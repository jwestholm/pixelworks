import unittest,tempfile,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('staff_dismiss_test',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class StaffDismissTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'testprojekt','name':'Test','idea':'Test','genre':'Pussel','platform':'Webbläsare'})
  self.a=s.hire_codex('testprojekt',{'name':'Extra','approval':'HIRE_CODEX_FOR_PROJECT'})
 def tearDown(self):
  s.JOBS.clear();s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def test_confirm_required(self):
  with self.assertRaisesRegex(ValueError,'Bekräftelse'):s.dismiss_staff('testprojekt',{'agent_id':self.a['id']})
 def test_dismiss_and_keep_project(self):
  out=s.dismiss_staff('testprojekt',{'agent_id':self.a['id'],'approval':'DISMISS_STAFF'})
  self.assertTrue(out['history_preserved']);self.assertEqual([],s.staff_read('testprojekt'))
  self.assertTrue((s.path_for('testprojekt')/'work').is_dir())
 def test_running_job_blocked(self):
  s.JOBS['x']={'agent_id':self.a['id'],'project':'testprojekt','state':'running'}
  with self.assertRaisesRegex(ValueError,'pågående'):s.dismiss_staff('testprojekt',{'agent_id':self.a['id'],'approval':'DISMISS_STAFF'})
 def test_cleanup_ownership(self):
  s.assignment_save('testprojekt',{'station':'qa','mode':'exclusive','agent_ids':[self.a['id']]})
  s.dismiss_staff('testprojekt',{'agent_id':self.a['id'],'approval':'DISMISS_STAFF'})
  self.assertEqual([],s.assignments_read('testprojekt')['qa']['agent_ids'])
  self.assertEqual('open',s.assignments_read('testprojekt')['qa']['mode'])
if __name__=='__main__':unittest.main()
