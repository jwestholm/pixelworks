import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_multistaff',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class MultiStaffTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'sample','name':'Sample','idea':'A fun game','genre':'Pussel','platform':'Webbläsare'})
  self.a=s.hire_codex('sample',{'approval':'HIRE_CODEX_FOR_PROJECT','name':'Kim'})
  self.b=s.hire_codex('sample',{'approval':'HIRE_CODEX_FOR_PROJECT','name':'Robin'})
 def tearDown(self):s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def test_unique_and_persisted(self):
  self.assertNotEqual(self.a['id'],self.b['id'])
  self.assertEqual([x['name'] for x in s.staff_read('sample')],['Kim','Robin'])
  self.assertEqual(self.a['id'],'codex-1')
 def test_profiles_and_station_permissions(self):
  s.update_staff_profile('sample',{'agent_id':self.b['id'],'role':'QA','personality':'Nyfiken','work_mode':'specialist','allowed_stations':['qa']})
  with self.assertRaisesRegex(ValueError,'behörighet'):s.move_staff('sample',{'agent_id':self.b['id'],'station':'music'})
  self.assertEqual(s.move_staff('sample',{'agent_id':self.b['id'],'station':'qa'})['station'],'qa')
  self.assertEqual(s.staff_read('sample')[1]['role'],'QA')
 def test_exclusive_station(self):
  s.assignment_save('sample',{'station':'qa','mode':'exclusive','agent_ids':[self.b['id']]})
  with self.assertRaisesRegex(ValueError,'behörighet'):s.move_staff('sample',{'agent_id':self.a['id'],'station':'qa'})
  self.assertEqual(s.move_staff('sample',{'agent_id':self.b['id'],'station':'qa'})['station'],'qa')
  self.assertEqual(s.assignments_read('sample')['qa']['mode'],'exclusive')
 def test_invalid_assignment_fails(self):
  with self.assertRaises(ValueError):s.assignment_save('sample',{'station':'qa','mode':'exclusive','agent_ids':['unknown']})
  self.assertEqual(s.assignments_read('sample'),{})
 def test_custom_skill_per_agent(self):
  s.save_skill_setting('sample',{'agent_id':self.b['id'],'skill':'custom-phaser-3','name':'Phaser 3','level':4,'instruction':'Skapa och testa Phaser-scener.'})
  self.assertEqual(s.get_skill_settings('sample')[self.b['id']]['custom-phaser-3']['level'],4)
  self.assertNotIn('custom-phaser-3',s.get_skill_settings('sample')[self.a['id']])
 def test_no_skill_inflates_provider_capability(self):
  with self.assertRaises(ValueError):s.save_skill_setting('sample',{'agent_id':self.a['id'],'skill':'custom-image','name':'Bild','level':6,'instruction':'Generera bilder direkt.'})
if __name__=='__main__':unittest.main()
