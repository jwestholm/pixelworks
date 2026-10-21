import unittest,tempfile,sys,subprocess,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import server as s

class LeadOfficeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'game','name':'Game','idea':'Testspel','genre':'Pussel','platform':'Webbläsare'})
  self.lead=s.hire_codex('game',{'name':'Chef','approval':'HIRE_CODEX_FOR_PROJECT'})
  self.coder=s.hire_codex('game',{'name':'Coder','approval':'HIRE_CODEX_FOR_PROJECT'})
  self.qa=s.hire_codex('game',{'name':'QA','approval':'HIRE_CODEX_FOR_PROJECT'})
  team=s.staff_read('game')
  for a in team:
   a['allowed_stations']=['lead','code','qa']
   a['role_type']='lead' if a['id']==self.lead['id'] else 'programmer'
  s.staff_write('game',team)
  self.order=s.order_action('game',{'station':'qa','instruction':'Testa det färdiga spelet','priority':1})['item']
 def tearDown(self):
  s.JOBS.clear();s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def test_without_chief_no_auto_assignment(self):
  self.assertIsNone(s.dispatch_plan('game')['next'])
 def test_chief_at_desk_delegates(self):
  s.move_staff('game',{'agent_id':self.lead['id'],'station':'lead'})
  plan=s.dispatch_plan('game')
  self.assertIsNotNone(plan['next'])
  self.assertNotEqual(plan['next']['agent_id'],self.lead['id'])
 def test_chief_coffee_pauses(self):
  s.move_staff('game',{'agent_id':self.lead['id'],'station':'lead'})
  s.move_staff('game',{'agent_id':self.lead['id'],'station':'cafe'})
  self.assertIsNone(s.dispatch_plan('game')['next'])
 def test_skill_priority_beats_home_station(self):
  s.move_staff('game',{'agent_id':self.lead['id'],'station':'lead'})
  team=s.staff_read('game')
  for a in team:
   if a['id']==self.coder['id']:a['skills']['testing']=5;a['home_station']='code'
   if a['id']==self.qa['id']:a['skills']['testing']=1;a['home_station']='qa'
  s.staff_write('game',team)
  self.assertEqual(s.dispatch_plan('game')['next']['agent_id'],self.coder['id'])
 def test_fallback_when_no_other_worker(self):
  s.move_staff('game',{'agent_id':self.lead['id'],'station':'lead'})
  people=s.staff_read('game')
  for a in people:
   if a['id']!=self.lead['id']:a['allowed_stations']=['code']
  s.staff_write('game',people)
  self.assertEqual(s.dispatch_plan('game')['next']['agent_id'],self.lead['id'])
 def test_separate_git_worktrees_can_write_concurrently(self):
  if not shutil.which('git'):self.skipTest('git saknas')
  work=s.path_for('game')/'work'
  (work/'file.txt').write_text('base')
  s.prepare_parallel_git('game')
  a,ba=s.create_worker_tree('game','abcdef123401')
  b,bb=s.create_worker_tree('game','abcdef123402')
  # Real simultaneous local processes writing to same Git repository through distinct worktrees.
  p1=subprocess.Popen([sys.executable,'-c',"from pathlib import Path;Path('one.txt').write_text('one')"],cwd=a)
  p2=subprocess.Popen([sys.executable,'-c',"from pathlib import Path;Path('two.txt').write_text('two')"],cwd=b)
  self.assertEqual(p1.wait(timeout=10),0);self.assertEqual(p2.wait(timeout=10),0)
  self.assertTrue((a/'one.txt').exists());self.assertTrue((b/'two.txt').exists())
  self.assertFalse((work/'one.txt').exists());self.assertFalse((work/'two.txt').exists())
  self.assertNotEqual(ba,bb)

if __name__=='__main__':unittest.main()
