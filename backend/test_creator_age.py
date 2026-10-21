import importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('creator_v102',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class AudiencePolicies(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name)/'.pixelworks';s.PROJECTS=s.ROOT/'projects'
 def tearDown(self):
  s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def payload(self,slug,creator):
  return {'slug':slug,'name':slug,'idea':'Speltest','creator':creator}
 def test_child_rejects_explicit_adult(self):
  with self.assertRaisesRegex(ValueError,'otillåtna egna val'):
   s.create_project(self.payload('barnspel',{'audience':['Barn (6–9)'],'content':['Vuxen / XXX 18+']}))
  self.assertFalse((s.PROJECTS/'barnspel').exists())
 def test_child_rejects_custom_theme(self):
  with self.assertRaisesRegex(ValueError,'otillåtna egna val'):
   s.create_project(self.payload('junior',{'audience':['Junior (10–12)'],'themes':['Eget XXX-tema']}))
 def test_adult_content_requires_adult_choice(self):
  with self.assertRaisesRegex(ValueError,'uttryckligt'):
   s.create_project(self.payload('missing',{'content':['Vuxen / XXX 18+']}))
 def test_child_project_writes_policy_to_bible_and_task(self):
  result=s.create_project(self.payload('kids',{'audience':['Barn (6–9)'],'gameGenre':['Plattform'],'themes':['Pirater']}))
  self.assertTrue(result['verified'])
  p=s.PROJECTS/'kids'
  self.assertIn('Förbjud nakenhet', (p/'studio-bible/GAME_BIBLE.md').read_text())
  self.assertIn('innehållspolicy',(p/'management/FIRST_BIBLE_TASK.md').read_text())
  self.assertIn('child_safe',(p/'project.json').read_text())
 def test_adult_content_explicit(self):
  result=s.create_project(self.payload('adult',{'audience':['Vuxen (18+)'],'content':['Vuxen / XXX 18+']}))
  self.assertTrue(result['verified'])
if __name__=='__main__':unittest.main()
