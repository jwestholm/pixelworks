import importlib.util,tempfile,unittest,subprocess
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_git',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class AutoGitTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'gittest','name':'Git Test','idea':'Ett spel med två arbetare','genre':'Äventyr','platform':'Webbläsare'})
  self.work=s.path_for('gittest')/'work'
 def tearDown(self):
  s.JOBS.clear();s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def test_initial_commit_is_automatic(self):
  self.assertFalse(s.isolated_ready('gittest')[0]);r=s.prepare_parallel_git('gittest')
  self.assertTrue(r['committed']);self.assertTrue(s.isolated_ready('gittest')[0])
  self.assertEqual(s.prepare_parallel_git('gittest')['committed'],False)
  self.assertTrue((self.work/'README.md').exists())
 def test_dirty_files_get_local_snapshot_and_worktrees(self):
  s.prepare_parallel_git('gittest');(self.work/'index.html').write_text('<h1>Spel</h1>')
  self.assertFalse(s.isolated_ready('gittest')[0]);self.assertTrue(s.prepare_parallel_git('gittest')['committed'])
  tree,branch=s.create_worker_tree('gittest','job123')
  self.assertEqual((tree/'index.html').read_text(),'<h1>Spel</h1>')
  self.assertTrue(branch.startswith('pixelworks/job-'))
 def test_sensitive_files_are_refused_not_committed(self):
  (self.work/'service.key').write_text('SENSITIVE_TEST_DATA')
  with self.assertRaisesRegex(ValueError,'hemlighet'):s.prepare_parallel_git('gittest')
  self.assertFalse(s.isolated_ready('gittest')[0])
 def test_running_direct_job_prevents_snapshot(self):
  s.JOBS['busy']={'project':'gittest','state':'running'}
  with self.assertRaisesRegex(ValueError,'direktjobb'):s.prepare_parallel_git('gittest')
if __name__=='__main__':unittest.main()
