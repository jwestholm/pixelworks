import unittest
from test_server import LocalTests, mod

class SkillTests(LocalTests):
 def test_defaults_persistence_isolation(self):
  mod.create_project(self.payload())
  mod.create_project(self.payload('andra-spelet'))
  mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  mod.hire_codex('andra-spelet',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  self.assertEqual(len(mod.get_skill_settings('rosa-grisen')['codex-1']),10)
  self.assertEqual(mod.get_skill_settings('rosa-grisen')['codex-1']['art']['level'],2)
  result=mod.save_skill_setting('rosa-grisen',{'agent_id':'codex-1','skill':'art','level':4,'instruction':'Gör grisen vackert rosa och behåll gameplay.'})
  self.assertEqual(result['level'],4)
  self.assertIn('rosa',mod.get_skill_settings('rosa-grisen')['codex-1']['art']['instruction'])
  self.assertNotIn('grisen',mod.get_skill_settings('andra-spelet')['codex-1']['art']['instruction'])
  self.assertTrue((mod.PROJECTS/'rosa-grisen/work/AGENTS.md').exists())
 def test_validation(self):
  mod.create_project(self.payload());mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  base={'agent_id':'codex-1','skill':'art','level':3,'instruction':'Förbättra grafiken i projektet'}
  for extra in ({'level':9},{'skill':'unknown'},{'instruction':'x'},{'agent_id':'nobody'}):
   with self.assertRaises(ValueError):mod.save_skill_setting('rosa-grisen',base|extra)
 def test_no_symlink_overwrite(self):
  mod.create_project(self.payload());mod.hire_codex('rosa-grisen',{'approval':'HIRE_CODEX_FOR_PROJECT'})
  import pathlib
  target=pathlib.Path(self.tmp.name)/'outside.json';target.write_text('{}')
  (mod.PROJECTS/'rosa-grisen/management/SKILL_SETTINGS.json').symlink_to(target)
  with self.assertRaises(ValueError):mod.save_skill_setting('rosa-grisen',{'agent_id':'codex-1','skill':'art','level':3,'instruction':'Testa något riktigt här'})
  self.assertEqual(target.read_text(),'{}')
if __name__=='__main__':unittest.main()
