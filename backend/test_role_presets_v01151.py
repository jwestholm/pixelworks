import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_role',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class RolePresetTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'testprojekt','name':'Test','idea':'Testspel','genre':'Pussel','platform':'Webbläsare'})
  self.agent=s.hire_codex('testprojekt',{'approval':'HIRE_CODEX_FOR_PROJECT','name':'Boss'})
 def tearDown(self):
  s.ROOT,s.PROJECTS=self.old;s.JOBS.clear();self.tmp.cleanup()
 def test_lead_role_enables_lead_station_and_persists(self):
  a=s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'role_type':'lead','apply_role_skills':True})
  self.assertEqual(a['role'],'Arbetsledare');self.assertEqual(a['home_station'],'lead')
  self.assertIn('lead',a['allowed_stations'])
  self.assertEqual(s.staff_read('testprojekt')[0]['role_type'],'lead')
  self.assertEqual(s.get_skill_settings('testprojekt')[a['id']]['planning']['level'],5)
 def test_qa_role_default_and_manual_allowed_override(self):
  a=s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'role_type':'qa','allowed_stations':['qa','code'],'apply_role_skills':True})
  self.assertEqual(a['role'],'QA-testare');self.assertEqual(a['allowed_stations'],['qa','code'])
  self.assertEqual(s.get_skill_settings('testprojekt')[a['id']]['testing']['level'],5)
 def test_role_change_does_not_block_individual_skill_tweaks(self):
  a=s.update_staff_profile('testprojekt',{'agent_id':self.agent['id'],'role_type':'artist','apply_role_skills':True})
  self.assertIn('art',a['allowed_stations'])
  self.assertEqual(s.get_skill_settings('testprojekt')[a['id']]['art']['level'],5)
if __name__=='__main__':unittest.main()
