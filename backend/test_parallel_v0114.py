import importlib.util, tempfile, unittest, subprocess, shutil
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_parallel',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class ParallelTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'parallel','name':'Parallel','idea':'Ett spel för tester','genre':'Pussel','platform':'Webbläsare'})
  self.work=s.path_for('parallel')/'work'
  self.a=s.hire_codex('parallel',{'name':'Kodaren','approval':'HIRE_CODEX_FOR_PROJECT'})
  self.b=s.hire_codex('parallel',{'name':'Testaren','approval':'HIRE_CODEX_FOR_PROJECT'})
  workers=s.staff_read('parallel')
  for w in workers:
   w.update(work_mode='autonomous',allowed_stations=['code','qa'],home_station='code' if w['id']==self.a['id'] else 'qa')
  s.staff_write('parallel',workers)
  s.order_action('parallel',{'station':'code','instruction':'Implementera ett litet spel','priority':1})
  s.order_action('parallel',{'station':'qa','instruction':'Testa spelets huvudmeny','priority':1})
 def tearDown(self):
  s.JOBS.clear();s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def test_no_commit_forces_one_at_a_time(self):
  plan=s.dispatch_plan('parallel')
  self.assertFalse(plan['parallel_ready'])
  self.assertEqual(len(plan['assignments']),1)
 def test_two_workers_different_worktrees(self):
  if not shutil.which('git'):self.skipTest('git saknas')
  subprocess.run(['git','-C',str(self.work),'add','.'],check=True,capture_output=True)
  subprocess.run(['git','-C',str(self.work),'-c','user.name=Pixel Works Test','-c','user.email=test@localhost','commit','-m','Baseline'],check=True,capture_output=True)
  plan=s.dispatch_plan('parallel')
  self.assertTrue(plan['parallel_ready'],plan['parallel_reason'])
  self.assertEqual(len(plan['assignments']),2)
  self.assertNotEqual(plan['assignments'][0]['agent_id'],plan['assignments'][1]['agent_id'])
  t1,b1=s.create_worker_tree('parallel','a123')
  t2,b2=s.create_worker_tree('parallel','b123')
  self.assertTrue((t1/'.git').exists());self.assertTrue((t2/'.git').exists())
  self.assertNotEqual(t1,t2);self.assertEqual((self.work/'.git').is_dir(),True)
  self.assertEqual(s.isolated_ready('parallel')[0],True)
 def test_leader_delegates_then_fallback(self):
  staff=s.staff_read('parallel')
  staff[0]['role_type']='lead';staff[0]['allowed_stations']=['code','qa']
  staff[1]['allowed_stations']=['qa']
  s.staff_write('parallel',staff)
  plan=s.dispatch_plan('parallel')
  self.assertTrue(plan['next']['fallback_lead'])
 def test_key_saved_outside_project_and_never_echoed(self):
  key='AIza'+'a'*34
  result=s.store_gemini_key({'key':key})
  self.assertTrue(result['configured']);self.assertFalse(result['execution_enabled'])
  self.assertEqual(s.gemini_key_file().stat().st_mode&0o777,0o600)
  self.assertNotIn(key,str(s.provider_status()))
 def test_key_does_not_enable_gemini(self):
  s.store_gemini_key({'key':'AIza'+'b'*34})
  self.assertFalse(s.provider_status()['gemini']['execution_enabled'])
if __name__=='__main__':unittest.main()
