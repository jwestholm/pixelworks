import importlib.util, tempfile, unittest, subprocess
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pw_integration',Path(__file__).with_name('server.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def git(root,*args):
    p=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True)
    if p.returncode:raise AssertionError((args,p.stderr))
    return p.stdout

class IntegrationTests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();mod.ROOT=Path(self.tmp.name);mod.PROJECTS=mod.ROOT/'projects';mod.JOBS.clear()
    mod.create_project({'name':'Minesweeper','slug':'minesweeper','idea':'Spel','genre':'Spel','platform':'Webbläsare','priority':'Kvalitet'})
    self.project=mod.PROJECTS/'minesweeper';self.work=self.project/'work'
    if not (self.work/'.git').exists():git(self.work,'init')
    (self.work/'game.js').write_text('start\n')
    (self.work/'art.css').write_text('plain\n')
    git(self.work,'add','-A');git(self.work,'-c','user.name=Test','-c','user.email=test@local','commit','-m','base')
 def tearDown(self): self.tmp.cleanup()
 def worker(self,id):
    tree,branch=mod.create_worker_tree('minesweeper',id)
    return tree,{'id':id,'project':'minesweeper','worktree':str(tree),'branch':branch,'state':'review'}
 def test_clean_result_integrated_without_manager(self):
    tree,job=self.worker('a'*12)
    (tree/'game.js').write_text('new shovel\n')
    ok,msg=mod.integrate_worker_result(job)
    self.assertTrue(ok,msg);self.assertEqual((self.work/'game.js').read_text(),'new shovel\n')
 def test_parallel_nonconflicting_merges_without_manager(self):
    a,ja=self.worker('a'*12);b,jb=self.worker('b'*12)
    (a/'game.js').write_text('shovel\n');(b/'art.css').write_text('new art\n')
    self.assertTrue(mod.integrate_worker_result(ja)[0])
    ok,msg=mod.integrate_worker_result(jb)
    self.assertTrue(ok,msg);self.assertEqual((self.work/'art.css').read_text(),'new art\n')
 def test_same_content_is_not_duplicate_merge(self):
    a,ja=self.worker('a'*12);b,jb=self.worker('b'*12)
    (a/'game.js').write_text('shovel\n');(b/'game.js').write_text('shovel\n')
    self.assertTrue(mod.integrate_worker_result(ja)[0])
    ok,msg=mod.integrate_worker_result(jb)
    self.assertTrue(ok,msg);self.assertIn('redan',msg)
    self.assertEqual((self.work/'game.js').read_text(),'shovel\n')
 def test_generated_agent_instructions_do_not_use_broken_relative_bible(self):
    agent=(self.work/'AGENTS.md').read_text()
    self.assertIn('GAME_BIBLE.md',agent)
    self.assertNotIn('../studio-bible/GAME_BIBLE.md',agent)
 def test_old_report_recovers_and_leaves_a_completion_note(self):
    tree,job=self.worker('c'*12)
    (tree/'game.js').write_text('recovered shovel\n')
    saved={'id':job['id'],'project':'minesweeper','source':'codex-cli','state':'review',
           'archived':False,'read':False,'summary':'Shovel ready','agent_name':'Programmerarn'}
    path=mod.report_path('minesweeper',job['id'])
    path.write_text(__import__('json').dumps(saved),encoding='utf-8')
    with patch.object(mod,'project_mandate',return_value={'enabled':True}):
      result=mod.recover_completed_reviews('minesweeper')
    self.assertEqual(len(result),1)
    self.assertTrue(result[0][1])
    self.assertEqual((self.work/'game.js').read_text(),'recovered shovel\n')
    self.assertFalse(__import__('json').loads(path.read_text())['archived'])
    self.assertFalse(__import__('json').loads(path.read_text())['read'])
 def test_conflicting_file_keeps_live_game(self):
    a,ja=self.worker('a'*12);b,jb=self.worker('b'*12)
    (a/'game.js').write_text('shovel\n');(b/'game.js').write_text('other tool\n')
    self.assertTrue(mod.integrate_worker_result(ja)[0])
    with patch.object(mod,'staff_read',return_value=[{'role_type':'lead','station':'lead'}]):
      ok,msg=mod.integrate_worker_result(jb)
    self.assertFalse(ok);self.assertIn('krockar',msg)
    self.assertEqual((self.work/'game.js').read_text(),'shovel\n')
    self.assertFalse((self.work/'.git'/'MERGE_HEAD').exists())
if __name__=='__main__':unittest.main()
