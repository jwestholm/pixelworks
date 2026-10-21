import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_edit_staff',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class StaffEditTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'testprojekt','name':'Test','idea':'A test game','genre':'Pussel','platform':'Webbläsare'})
  self.agent=s.hire_codex('testprojekt',{'approval':'HIRE_CODEX_FOR_PROJECT','name':'Kim'})
 def tearDown(self):
  s.ROOT,s.PROJECTS=self.old;s.JOBS.clear();self.tmp.cleanup()
 def test_edit_identity_profession_and_job_instructions_persist(self):
  a=s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'name':'Programmerarn','role':'Frontendutvecklare','role_type':'programmer','home_station':'code','allowed_stations':['code','qa'],'work_instructions':'Skriv alltid tester.'})
  self.assertEqual(a['name'],'Programmerarn')
  self.assertEqual(a['role_type'],'programmer')
  self.assertEqual(s.staff_read('testprojekt')[0]['work_instructions'],'Skriv alltid tester.')
 def test_new_stations_fall_back_to_valid_home_for_legacy_profiles(self):
  a=s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'allowed_stations':['qa']})
  self.assertEqual(a['home_station'],'qa')
 def test_home_must_be_allowed(self):
  with self.assertRaisesRegex(ValueError,'Hemmabord'):
   s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'allowed_stations':['qa'],'home_station':'music'})
 def test_active_agent_cannot_change_permission_or_identity(self):
  s.JOBS['busy-test']={'agent_id':self.agent['id'],'project':'testprojekt','state':'running'}
  with self.assertRaisesRegex(ValueError,'arbetar'):
   s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'name':'New'})
  self.assertEqual(s.staff_read('testprojekt')[0]['name'],'Kim')
 def test_invalid_instructions_and_role_type_rejected(self):
  with self.assertRaises(ValueError):s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'work_instructions':'x'*2001})
  with self.assertRaises(ValueError):s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'role_type':'godmode'})
if __name__=='__main__':unittest.main()
