"""Projektborttagning måste vara tvåstegs, isolerad och återställbar."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('pw_del',Path(__file__).with_name('server.py'))
pw=importlib.util.module_from_spec(spec);spec.loader.exec_module(pw)

class RemovalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();pw.ROOT=Path(self.tmp.name).resolve();pw.PROJECTS=pw.ROOT/'projects'
  pw.JOBS.clear();pw.PROJECT_DELETE_TICKETS.clear()
  for slug in ('mitt-spel','annat-spel'):
   pw.create_project({'slug':slug,'name':slug,'idea':'Ett testspelexperiment','genre':'Äventyr'})
 def tearDown(self):
  pw.JOBS.clear();pw.PROJECT_DELETE_TICKETS.clear();self.tmp.cleanup()
 def test_two_step_recovery_and_other_project_unchanged(self):
  before=(pw.PROJECTS/'mitt-spel/studio-bible/GAME_BIBLE.md').read_bytes()
  ticket=pw.prepare_project_removal('mitt-spel')['ticket']
  with self.assertRaises(ValueError):pw.remove_project_safely('mitt-spel',{'ticket':ticket,'confirm_slug':'annat-spel','approval':'REMOVE_PROJECT_CONFIRMED_TWICE'})
  self.assertTrue((pw.PROJECTS/'mitt-spel').exists())
  ticket=pw.prepare_project_removal('mitt-spel')['ticket']
  result=pw.remove_project_safely('mitt-spel',{'ticket':ticket,'confirm_slug':'mitt-spel','approval':'REMOVE_PROJECT_CONFIRMED_TWICE'})
  self.assertFalse((pw.PROJECTS/'mitt-spel').exists())
  self.assertEqual((Path(result['recovery_path'])/'studio-bible/GAME_BIBLE.md').read_bytes(),before)
  self.assertTrue((pw.PROJECTS/'annat-spel').exists())
  with self.assertRaises(ValueError):pw.remove_project_safely('mitt-spel',{'ticket':ticket,'confirm_slug':'mitt-spel','approval':'REMOVE_PROJECT_CONFIRMED_TWICE'})
 def test_busy_project_blocked(self):
  pw.JOBS['test']={'project':'mitt-spel','state':'running'}
  with self.assertRaises(ValueError):pw.prepare_project_removal('mitt-spel')
  self.assertTrue((pw.PROJECTS/'mitt-spel').exists())
 def test_symlink_project_blocked(self):
  (pw.PROJECTS/'mitt-spel').rename(pw.ROOT/'safe')
  (pw.PROJECTS/'mitt-spel').symlink_to(pw.ROOT/'safe',target_is_directory=True)
  with self.assertRaises(ValueError):pw.prepare_project_removal('mitt-spel')
  self.assertTrue((pw.ROOT/'safe').exists())

if __name__=='__main__':unittest.main()
