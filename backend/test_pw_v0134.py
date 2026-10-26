"""Offline 0.13.4 regression: editable plan and playable project bootstrap."""
import copy, json, subprocess, tempfile, threading, unittest
from pathlib import Path
from types import SimpleNamespace
import pw_v0133, pw_v0134
import pw_v0121111 as planner

class Bootstrap(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name); self.project=self.root/'projects'/'test-game'
  (self.project/'work').mkdir(parents=True)
  (self.project/'studio-bible').mkdir()
  (self.project/'work'/'README.md').write_text('Start',encoding='utf-8')
  (self.project/'work'/'AGENTS.md').write_text('Only project',encoding='utf-8')
  (self.project/'studio-bible'/'GAME_BIBLE.md').write_text('# Vision\nEn idé\n',encoding='utf-8')
  (self.project/'project.json').write_text(json.dumps({'id':'test-game','name':'Minesweeper marathon','idea':'Minröjare i färg','genre':'Pussel'}),encoding='utf-8')
  subprocess.run(['git','-C',str(self.project/'work'),'init','-q'],check=True)
  self.srv=SimpleNamespace(path_for=lambda x:self.project,validate_slug=lambda x:x)
 def test_minesweeper_bootstrap_playable_git_and_gamebible(self):
  result=pw_v0134.bootstrap(self.srv,'test-game',{'name':'Minesweeper marathon','genre':'Pussel'})
  self.assertEqual(result['template'],'mines');self.assertFalse(result['ai_generated'])
  text=(self.project/'work'/'index.html').read_text();self.assertIn('game.js',text)
  self.assertIn('Minesweeper marathon',text)
  self.assertIn('SIZE=8,COUNT=10',(self.project/'work'/'game.js').read_text())
  self.assertIn('Första spelbara prototyp',(self.project/'studio-bible'/'GAME_BIBLE.md').read_text())
  state=subprocess.run(['git','-C',str(self.project/'work'),'status','--porcelain'],capture_output=True,text=True,check=True)
  self.assertEqual(state.stdout.strip(),'')
  head=subprocess.run(['git','-C',str(self.project/'work'),'rev-parse','HEAD'],capture_output=True,text=True,check=True)
  self.assertEqual(len(head.stdout.strip()),40)
  self.assertTrue(pw_v0134.inspect(self.srv,'test-game')['playable'])
 def test_old_game_with_files_is_never_overwritten(self):
  data=self.project/'work'/'game.js';data.write_text('ORIGINAL SECRET CODE',encoding='utf-8')
  oldbible=(self.project/'studio-bible'/'GAME_BIBLE.md').read_text()
  with self.assertRaisesRegex(ValueError,'spelkod|annat innehåll'):
   pw_v0134.bootstrap(self.srv,'test-game',{'name':'Example'})
  self.assertEqual(data.read_text(),'ORIGINAL SECRET CODE')
  self.assertEqual((self.project/'studio-bible'/'GAME_BIBLE.md').read_text(),oldbible)
 def test_new_project_hook_creates_starter_without_ai(self):
  old_calls=[]
  def create(payload):old_calls.append(payload);return {'id':'test-game'}
  class Handler:
   def do_GET(self):return 'base get'
   def do_POST(self):return 'base post'
  self.srv.create_project=create;self.srv.Handler=Handler
  pw_v0134.install(self.srv)
  result=self.srv.create_project({'slug':'test-game','name':'Minesweeper marathon'})
  self.assertEqual(len(old_calls),1)
  self.assertEqual(result['playable_bootstrap']['status'],'startprototyp')
  self.assertTrue((self.project/'work'/'index.html').is_file())
 def test_project_hook_never_destroys_old_code_on_failure(self):
  self.srv.create_project=lambda payload:{'id':'test-game'}
  self.srv.Handler=type('Handler',(),{'do_GET':lambda obj:None,'do_POST':lambda obj:None})
  old=self.project/'work'/'game.js';old.write_text('OLD WORK')
  pw_v0134.install(self.srv)
  result=self.srv.create_project({'slug':'test-game','name':'Minesweeper marathon'})
  self.assertEqual(result['playable_bootstrap']['status'],'failed')
  self.assertEqual(old.read_text(),'OLD WORK')
 def test_escape_untrusted_project_name(self):
  pw_v0134.bootstrap(self.srv,'test-game',{'name':'<img src=x onerror=alert(1)>','genre':'Spel'})
  html=(self.project/'work'/'index.html').read_text()
  self.assertNotIn('<img ',html)
  self.assertIn('&lt;img',html)
 def test_old_empty_project_can_bootstrap_with_explicit_approval(self):
  self.assertTrue(pw_v0134.inspect(self.srv,'test-game')['can_bootstrap'])
  with self.assertRaisesRegex(ValueError,'Välj'):
   pw_v0134.bootstrap_existing(self.srv,'test-game',{'approval':'WRONG'})
  self.assertFalse((self.project/'work'/'index.html').exists())
  result=pw_v0134.bootstrap_existing(self.srv,'test-game',{'approval':'CREATE_PLAYABLE_START_V0134'})
  self.assertTrue(result['first_local_commit'])
  with self.assertRaises(ValueError):pw_v0134.bootstrap_existing(self.srv,'test-game',{'approval':'CREATE_PLAYABLE_START_V0134'})

class Editor(unittest.TestCase):
 def setUp(self):
  self.people=[{'id':'chief','name':'Chefen','role_type':'lead','provider':'codex','station':'lead','allowed_stations':['lead']},
               {'id':'gunnar','name':'Gunnar','role_type':'programmer','provider':'codex','station':'code','allowed_stations':['code','qa']},
               {'id':'sofia','name':'Sofia','role_type':'artist','provider':'codex','station':'art','allowed_stations':['art']}]
  self.orders=[];self.jobs={}
  def write(slug,v):self.orders=copy.deepcopy(v)
  self.srv=SimpleNamespace(project_mandate=lambda slug:{'enabled':True},
    orders_read=lambda slug:self.orders,orders_write=write,
    staff_read=lambda slug:self.people,
    get_skill_settings=lambda slug:{},list_reports=lambda slug:[],
    LOCK=threading.RLock(),JOBS=self.jobs,SKILL_STATIONS={'lead':'planning','art':'art','code':'coding'},
    agent_authorized=lambda slug,p,station:station in p['allowed_stations'])
  plan={'summary':'Gör spelet','tasks':[{'key':'art','station':'art','title':'Grafik','priority':2,
    'instruction':'Skapa en tydlig grafisk prototyp för spelaren','depends_on':[]},
    {'key':'code','station':'code','title':'Kod','priority':1,
    'instruction':'Implementera grundläggande spelmekanik i HTML5','depends_on':['art']}]}
  self.draft,_=pw_v0133.create_orders(self.srv,'test-game',{'id':'aabbccddeeff','station':'lead','instruction':'Gör produktionsplan'},plan)
 def payload(self):
  view=pw_v0133.get_view(self.srv,'test-game')['draft_plans'][0]
  return {'project':'test-game','plan_id':view['id'],'revision':view['revision'],'steps':[
    {k:step[k] for k in ('id','title','instruction','priority','assigned_agent_id','depends_on_order_ids')}
    for step in view['steps']]}
 def test_all_multi_order_plan_staged_before_one_approval(self):
  self.assertEqual(len(self.draft),2)
  for order in self.orders:
   self.assertFalse(pw_v0133.ready(self.srv,'test-game',order)[0])
  self.assertEqual(len(pw_v0133.get_view(self.srv,'test-game')['draft_plans']),1)
 def test_release_allows_first_order_and_blocks_second_until_verified(self):
  data=self.payload()
  result=pw_v0133.change_plan(self.srv,'test-game',data,release=True)
  self.assertTrue(result['released'])
  self.assertTrue(pw_v0133.ready(self.srv,'test-game',self.orders[0])[0])
  self.assertFalse(pw_v0133.ready(self.srv,'test-game',self.orders[1])[0])
  self.assertFalse(pw_v0133.get_view(self.srv,'test-game')['draft_plans'])
  with self.assertRaisesRegex(ValueError,'godkänd'):pw_v0133.change_plan(self.srv,'test-game',data,release=True)
 def test_plan_edit_saved_atomically(self):
  data=self.payload();data['steps'][0]['title']='Nytt namn';data['steps'][0]['priority']=3
  result=pw_v0133.change_plan(self.srv,'test-game',data)
  self.assertFalse(result['released'])
  self.assertEqual(self.orders[0]['title'],'Nytt namn')
  self.assertEqual(self.orders[0]['priority'],3)
  self.assertFalse(pw_v0133.ready(self.srv,'test-game',self.orders[0])[0])
 def test_no_wrong_agent_or_cyclic_dependencies_or_partial_write(self):
  original=copy.deepcopy(self.orders)
  data=self.payload();data['steps'][0]['assigned_agent_id']='chief'
  with self.assertRaisesRegex(ValueError,'får inte'):pw_v0133.change_plan(self.srv,'test-game',data,True)
  self.assertEqual(self.orders,original)
  data=self.payload();data['steps'][0]['depends_on_order_ids']=[data['steps'][1]['id']]
  with self.assertRaisesRegex(ValueError,'tidigare'):pw_v0133.change_plan(self.srv,'test-game',data,True)
  self.assertEqual(self.orders,original)
 def test_optimistic_concurrency_rejects_stale_plan(self):
  data=self.payload();pw_v0133.change_plan(self.srv,'test-game',data)
  with self.assertRaisesRegex(ValueError,'ändrats'):pw_v0133.change_plan(self.srv,'test-game',data)
 def test_no_staff_visible_in_editor(self):
  self.people=[self.people[0],self.people[1]]
  data=self.payload();data['steps'][0]['assigned_agent_id']=None
  pw_v0133.change_plan(self.srv,'test-game',data)
  self.assertTrue(self.orders[0]['needs_staff'])
  view=pw_v0133.get_view(self.srv,'test-game')['draft_plans'][0]
  self.assertEqual(view['steps'][0]['staff_choices'],[])

if __name__=='__main__':unittest.main()
