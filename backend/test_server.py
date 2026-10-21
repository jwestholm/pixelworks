import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('pixelworks_server',Path(__file__).with_name('server.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class LocalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();mod.ROOT=Path(self.tmp.name).resolve();mod.PROJECTS=mod.ROOT/'projects'
 def tearDown(self):self.tmp.cleanup()
 def payload(self,slug='rosa-grisen'):
  return dict(name='Rosa Grisens Äventyr',slug=slug,idea='Bygg ett spel med en rosa gris',genre='Plattformsspel',platform='Webbläsare',priority='Spelkänsla')
 def test_project_and_bible(self):
  result=mod.create_project(self.payload());self.assertTrue(Path(result['work']).exists());self.assertTrue((mod.PROJECTS/'rosa-grisen/studio-bible/GAME_BIBLE.md').exists());self.assertTrue((mod.PROJECTS/'rosa-grisen/management/DECISIONS.md').exists());self.assertTrue((mod.PROJECTS/'rosa-grisen/work/AGENTS.md').exists())
  if result['git_initialized']:self.assertTrue((mod.PROJECTS/'rosa-grisen/work/.git').exists())
 def test_duplicate_rejected(self):
  mod.create_project(self.payload())
  with self.assertRaises(FileExistsError):mod.create_project(self.payload())
 def test_traversal_rejected(self):
  for slug in ['../x','x/../../etc','abc_xyz','a','', 'a'*80]:
   with self.subTest(slug=slug):
    with self.assertRaises(ValueError):mod.create_project(self.payload(slug))
 def test_staff_hire_persist_and_move(self):
  mod.create_project(self.payload())
  self.assertEqual(mod.staff_read('rosa-grisen'),[])
  person=mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT','name':'Byte'})
  self.assertEqual(person['name'],'Byte')
  second=mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT','name':'Andra'})
  self.assertNotEqual(person['id'],second['id'])
  changed=mod.move_staff('rosa-grisen',{'agent_id':'codex-1','station':'art'})
  self.assertEqual(changed['station'],'art')
  self.assertEqual(mod.staff_read('rosa-grisen')[0]['station'],'art')
  self.assertEqual((mod.PROJECTS/'rosa-grisen/management/STAFF.json').exists(),True)
 def test_work_docs_can_be_changed_without_losing_staff(self):
  mod.create_project(self.payload())
  mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  work=mod.PROJECTS/'rosa-grisen'/'work'
  (work/'AGENTS.md').unlink()
  (work/'README.md').unlink()
  result=mod.verify_project('rosa-grisen')
  self.assertTrue(result['verified'])
  self.assertTrue(result['warnings'])
  self.assertEqual(len(mod.staff_read('rosa-grisen')),1)
  self.assertEqual(mod.move_staff('rosa-grisen',{'agent_id':'codex-1','station':'qa'})['station'],'qa')
 def test_can_hire_after_codex_removed_optional_docs(self):
  mod.create_project(self.payload())
  (mod.PROJECTS/'rosa-grisen/work/AGENTS.md').unlink()
  person=mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  self.assertEqual(person['id'],'codex-1')
  self.assertEqual(len(mod.staff_read('rosa-grisen')),1)
 def test_staff_cannot_move_outside(self):
  mod.create_project(self.payload())
  mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  with self.assertRaises(ValueError):mod.move_staff('rosa-grisen',{'agent_id':'codex-1','station':'../../other'})
 def test_symlink_rejected(self):
  mod.PROJECTS.mkdir(parents=True); (mod.PROJECTS/'evil').symlink_to(Path(self.tmp.name))
  with self.assertRaises(ValueError):mod.path_for('evil')

if __name__=='__main__':unittest.main()

class PreviewTests(LocalTests):
 def test_preview_only_web_files(self):
  mod.create_project(self.payload())
  work=mod.PROJECTS/'rosa-grisen'/'work'
  (work/'index.html').write_text('<h1>Hej</h1>',encoding='utf-8')
  (work/'game.js').write_text('alert(1)',encoding='utf-8')
  self.assertEqual(mod.preview_file('rosa-grisen','index.html'),work/'index.html')
  self.assertEqual(mod.preview_file('rosa-grisen','game.js'),work/'game.js')
  for bad in ['../project.json','../../etc/passwd','.git/config','AGENTS.md','notes/../../project.json']:
   with self.assertRaises((ValueError,FileNotFoundError),msg=bad):mod.preview_file('rosa-grisen',bad)
 def test_preview_symlinks_blocked(self):
  mod.create_project(self.payload())
  work=mod.PROJECTS/'rosa-grisen'/'work'
  (work/'index.html').symlink_to(mod.PROJECTS/'rosa-grisen'/'project.json')
  with self.assertRaises(ValueError):mod.preview_file('rosa-grisen','index.html')
