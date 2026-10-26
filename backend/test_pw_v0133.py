"""Local offline safety and production tests. No paid/network AI calls."""
import io,json,tempfile,threading,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pw_v0133
import pw_v0121111 as staffplan
ORIGINAL_ELIGIBLE=staffplan._eligible

class Production(unittest.TestCase):
    def tearDown(self):
        staffplan._eligible=ORIGINAL_ELIGIBLE
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.chief={'id':'chief','name':'Chefen','role_type':'lead','provider':'codex',
                    'station':'lead','allowed_stations':['lead','meeting'],'home_station':'lead'}
        self.artist={'id':'sofia','name':'Sofia','role_type':'artist','provider':'codex',
                     'station':'art','allowed_stations':['art'],'home_station':'art'}
        self.coder={'id':'gunnar','name':'Gunnar','role_type':'programmer','provider':'codex',
                    'station':'code','allowed_stations':['code','qa'],'home_station':'code'}
        self.tester={'id':'test','name':'Testare','role_type':'qa','provider':'codex',
                     'station':'qa','allowed_stations':['qa'],'home_station':'qa'}
        self.staff=[self.chief,self.artist,self.coder,self.tester]
        self.orders=[];self.reports=[];self.jobs={}
        def write(slug,orders):self.orders=json.loads(json.dumps(orders))
        self.srv=SimpleNamespace(LOCK=threading.RLock(),JOBS=self.jobs,SKILL_STATIONS={
           'lead':'planning','art':'art','code':'coding','qa':'testing','docs':'documentation','music':'music'},
           staff_read=lambda slug:self.staff,orders_read=lambda slug:self.orders,
           orders_write=write,list_reports=lambda slug:self.reports,
           get_skill_settings=lambda slug:{p['id']:{'art':{'level':5},'coding':{'level':5},
                       'testing':{'level':5}} for p in self.staff},
           project_mandate=lambda slug:{'enabled':True},
           agent_authorized=lambda slug,p,station:station in p['allowed_stations'],
           path_for=lambda slug:self.root, bible_context=lambda slug,n:'# Minesweeper\nClassic game.')
        self.plan={'summary':'Spelproduktion','tasks':[
         {'key':'gfx','title':'Grafik till banan','station':'art','priority':2,
          'instruction':'Skapa sprites till Minesweeper-banan enligt Game Bible.','depends_on':[]},
         {'key':'code','title':'Implementera spelet','station':'code','priority':1,
          'instruction':'Implementera Minesweeper med spelregler och startbar HTML.','depends_on':['gfx']},
         {'key':'qa','title':'Testa spelet','station':'qa','priority':2,
          'instruction':'Testa att spelet verkligen startar och fungerar i webbläsaren.','depends_on':['code']} ]}
    def _release(self):
        draft=pw_v0133.get_view(self.srv,'demo')['draft_plans'][0]
        pw_v0133.change_plan(self.srv,'demo',{'plan_id':draft['id'],'revision':draft['revision'],
            'steps':[{k:step[k] for k in ('id','title','instruction','priority','assigned_agent_id','depends_on_order_ids')}
                for step in draft['steps']]},release=True)
    def _job(self,ident='abc123def456'):
        return {'id':ident,'station':'lead','agent_id':'chief','project':'demo',
                'instruction':'Gör en prioriterad utvecklingsplan','state':'running'}
    def test_parse_normal_plan(self):
        x=pw_v0133._json_plan(json.dumps(self.plan),set(self.srv.SKILL_STATIONS))
        self.assertEqual([t['key'] for t in x['tasks']],['gfx','code','qa'])
    def test_reject_invalid_dependency_and_circular_plan(self):
        bad=json.loads(json.dumps(self.plan));bad['tasks'][0]['depends_on']=['qa']
        with self.assertRaisesRegex(ValueError,'Beroenden'):
            pw_v0133._json_plan(json.dumps(bad),set(self.srv.SKILL_STATIONS))
    def test_reject_malformed_freetext_without_creating_orders(self):
        with self.assertRaises(ValueError):
            pw_v0133._json_plan('Först ska Gunnar programmera... etc',set(self.srv.SKILL_STATIONS))
        self.assertFalse(self.orders)
    def test_reject_manager_as_ordinary_worker_station(self):
        bad=json.loads(json.dumps(self.plan));bad['tasks'][0]['station']='lead'
        with self.assertRaisesRegex(ValueError,'arbetsstation'):
            pw_v0133._json_plan(json.dumps(bad),set(self.srv.SKILL_STATIONS))
    def test_actual_orders_are_created_with_assignees(self):
        tasks,_=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self.assertEqual(len(self.orders),3)
        self.assertEqual([o['assigned_agent_name'] for o in tasks],['Sofia','Gunnar','Testare'])
        self.assertEqual(tasks[1]['depends_on_order_ids'],[tasks[0]['id']])
        self.assertEqual(tasks[2]['depends_on_order_ids'],[tasks[1]['id']])
        self.assertEqual(set(t['status'] for t in self.orders),{'waiting'})
    def test_idempotent_same_job_cannot_duplicate_orders(self):
        pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        tasks,created=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self.assertFalse(created);self.assertEqual(len(tasks),3);self.assertEqual(len(self.orders),3)
    def test_second_generic_chief_job_does_not_duplicate_plan(self):
        pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        tasks,created=pw_v0133.create_orders(self.srv,'demo',self._job('123456abcdef'),self.plan)
        self.assertFalse(created);self.assertEqual(tasks,[]);self.assertEqual(len(self.orders),3)
    def test_dependency_only_unlocks_after_real_code_integration(self):
        tasks,_=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self._release()
        self.assertFalse(pw_v0133.ready(self.srv,'demo',self.orders[1])[0])
        self.orders[0]['status']='done'
        self.assertFalse(pw_v0133.ready(self.srv,'demo',self.orders[1])[0])
        self.reports=[{'order_id':tasks[0]['id'],'state':'done','integrated':True}]
        self.assertTrue(pw_v0133.ready(self.srv,'demo',self.orders[1])[0])
        self.orders[1]['status']='done'
        self.assertFalse(pw_v0133.ready(self.srv,'demo',self.orders[2])[0])
        self.reports=[{'order_id':tasks[0]['id'],'state':'done','integrated':True},
                      {'order_id':tasks[1]['id'],'state':'done','integrated':False}]
        self.assertFalse(pw_v0133.ready(self.srv,'demo',self.orders[2])[0])
        self.reports=[{'order_id':tasks[0]['id'],'state':'done','integrated':True},
                      {'order_id':tasks[1]['id'],'state':'done','integrated':True}]
        self.assertTrue(pw_v0133.ready(self.srv,'demo',self.orders[2])[0])
    def test_failed_predecessor_blocks_next_task(self):
        tasks,_=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self._release()
        self.orders[0]['status']='failed'
        ok,message=pw_v0133.ready(self.srv,'demo',self.orders[1]);self.assertFalse(ok);self.assertIn('misslyckats',message)
    def test_missing_staff_does_not_substitute_random_person(self):
        self.staff=[self.chief,self.coder]
        tasks,_=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self.assertTrue(tasks[0]['needs_staff']);self.assertIsNone(tasks[0]['assigned_agent_id'])
        self.assertEqual(tasks[1]['assigned_agent_name'],'Gunnar')
    def test_recruitment_enables_unstaffed_order(self):
        self.staff=[self.chief,self.coder]
        pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        def base_reconcile(slug):return None
        self.srv.reconcile_orders_from_reports=base_reconcile
        self.srv.dispatch_plan=lambda slug:{'assignments':[],'blocked':[]}
        self.srv.Handler=type('Handler',(),{'do_POST':lambda s:None,'do_GET':lambda s:None})
        self.srv.run_codex=lambda *args:None
        pw_v0133.install(self.srv)
        self.staff.append(self.artist)
        self.srv.reconcile_orders_from_reports('demo')
        self.assertEqual(self.orders[0]['assigned_agent_name'],'Sofia')
        self.assertFalse(self.orders[0]['needs_staff'])
    def test_dispatch_rejects_dependency_and_wrong_assignee(self):
        tasks,_=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self._release()
        self.srv.reconcile_orders_from_reports=lambda slug:None
        self.srv.dispatch_plan=lambda slug:{'assignments':[
             {'order_id':tasks[1]['id'],'agent_id':'sofia','station':'code'},
             {'order_id':tasks[0]['id'],'agent_id':'sofia','station':'art'}],
             'blocked':[]}
        self.srv.Handler=type('Handler',(),{'do_POST':lambda s:None,'do_GET':lambda s:None})
        self.srv.run_codex=lambda *args:None
        pw_v0133.install(self.srv)
        plan=self.srv.dispatch_plan('demo')
        self.assertEqual(len(plan['assignments']),1)
        self.assertEqual(plan['assignments'][0]['order_id'],tasks[0]['id'])
    def test_production_endpoint_does_not_modify_orders(self):
        pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self._release()
        before=json.dumps(self.orders)
        data=pw_v0133.get_view(self.srv,'demo')
        self.assertEqual(before,json.dumps(self.orders))
        self.assertEqual(len(data['orders']),3)
        self.assertEqual(data['orders'][1]['state'],'dependency')
    def test_authenticated_direct_job_cannot_bypass_dependencies(self):
        tasks,_=pw_v0133.create_orders(self.srv,'demo',self._job(),self.plan)
        self._release()
        self.srv.reconcile_orders_from_reports=lambda slug:None
        self.srv.dispatch_plan=lambda slug:{'assignments':[],'blocked':[]}
        fake=self
        class Handler:
            def allowed(self):return True
            def auth(self):return True
            def same_origin(self):return True
            def reply(self,code,data):return code,data
            def do_POST(self):
                raw=self.rfile.read(int(self.headers['Content-Length']))
                return 202,json.loads(raw)
            def do_GET(self):return 404,{}
        self.srv.Handler=Handler;self.srv.run_codex=lambda *args:None
        self.srv.validate_slug=lambda x:x
        pw_v0133.install(self.srv)
        def call(order,person):
            h=Handler();h.path='/api/jobs'
            raw=json.dumps({'project':'demo','order_id':order['id'],
                            'agent_id':person,'station':order['station']}).encode()
            h.rfile=io.BytesIO(raw);h.headers={'Content-Length':str(len(raw))}
            return h.do_POST()
        blocked=call(tasks[1],'gunnar')
        self.assertEqual(blocked[0],409)
        wrong=call(tasks[0],'gunnar')
        self.assertEqual(wrong[0],409)
        self.assertEqual(call(tasks[0],'sofia')[0],202)

    def test_manager_actual_codex_plan_creates_real_orders(self):
        tree=self.root/'management'/'worktrees'/'job-abc';tree.mkdir(parents=True)
        job={**self._job(),'worktree':str(tree),'state':'queued'}
        self.jobs[job['id']]=job
        self.srv.finalize_worker_job=lambda j:setattr(self.srv,'final',dict(j))
        response=SimpleNamespace(returncode=0,stderr='',stdout=json.dumps({
           'type':'item.completed','item':{'type':'agent_message','text':json.dumps(self.plan,ensure_ascii=False)}})+'\n')
        with patch.object(pw_v0133.shutil,'which',return_value='/usr/bin/codex'),\
             patch.object(pw_v0133.subprocess,'run',return_value=response) as call:
            pw_v0133.manager_worker(self.srv,job['id'],'demo','Gör en prioriterad utvecklingsplan')
        self.assertEqual(self.srv.final['state'],'done')
        self.assertEqual(len(self.orders),3)
        self.assertIn('--sandbox',call.call_args.args[0]);self.assertIn('read-only',call.call_args.args[0])
        self.assertNotIn('workspace-write',call.call_args.args[0])
        self.assertEqual(list(tree.iterdir()),[])
    def test_manager_failed_ai_json_creates_no_orders(self):
        tree=self.root/'management'/'worktrees'/'job-abc';tree.mkdir(parents=True)
        job={**self._job(),'worktree':str(tree),'state':'queued'};self.jobs[job['id']]=job
        self.srv.finalize_worker_job=lambda j:setattr(self.srv,'final',dict(j))
        response=SimpleNamespace(returncode=0,stderr='',stdout=json.dumps({
           'type':'item.completed','item':{'type':'agent_message','text':'Jag föreslår att vi ...'}})+'\n')
        with patch.object(pw_v0133.shutil,'which',return_value='/usr/bin/codex'),\
             patch.object(pw_v0133.subprocess,'run',return_value=response):
            pw_v0133.manager_worker(self.srv,job['id'],'demo','Gör en utvecklingsplan')
        self.assertEqual(self.srv.final['state'],'failed')
        self.assertEqual(self.orders,[])

if __name__=='__main__':unittest.main()
