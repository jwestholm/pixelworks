"""Offline regression tests for real manager planning job scheduling and safety."""
import json
import io
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pw_v0121111 as staffplan
import pw_v0121115 as parallel
import pw_v0132


class Planning(unittest.TestCase):
    def setUp(self):
        self.chief={'id':'chief','name':'Chefen','role_type':'lead','provider':'codex',
                    'station':'lead','allowed_stations':['lead','meeting'], 'home_station':'lead'}
        self.gre={'id':'gre','name':'Greta','role_type':'writer','provider':'gemini',
                  'station':'docs','allowed_stations':['docs','meeting'],'home_station':'docs'}
        self.orders=[{'id':f'{i:012x}','station':'lead','priority':2,'status':'waiting',
                      'instruction':txt} for i,txt in enumerate([
            'Gör en prioriterad utvecklingsplan.',
            'Föreslå arbetsorder och ansvariga utan att själv starta AI-jobb.',
            'Granska befintliga rapporter och föreslå förbättringar.'],1)]
        self.people=[self.chief,self.gre]
        self.srv=SimpleNamespace(LOCK=threading.RLock(),JOBS={},
            staff_read=lambda s:self.people, orders_read=lambda s:self.orders,
            agent_authorized=lambda s,p,st: st in p['allowed_stations'],
            get_skill_settings=lambda s:{'chief':{'planning':{'level':5}}},
            isolated_ready=lambda s:(True,''))
    def test_chief_is_selected_only_at_chief_desk(self):
        self.assertEqual(staffplan.selection(self.srv,'demo',self.orders[0])['id'],'chief')
        self.assertIsNone(staffplan.selection(self.srv,'demo',{'station':'code','instruction':'skriv kod'}))
        self.chief['station']='cafe'
        self.assertIsNone(staffplan.selection(self.srv,'demo',self.orders[0]))
    def test_three_management_orders_start_one_at_a_time(self):
        p=parallel.parallel_plan(self.srv,lambda slug:{'leader_active':True,'assignments':[],
                            'blocked':[], 'active_jobs':[]},staffplan,'demo')
        self.assertEqual(len(p['assignments']),1)
        self.assertEqual(p['assignments'][0]['agent_id'],'chief')
        self.assertEqual(len(p['blocked']),2)
        self.assertTrue(p['assignments'][0]['fallback_lead'])
    def test_explicit_start_uses_existing_order_and_chief_identity(self):
        import pw_v0121112 as dispatcher
        self.srv.SKILL_STATIONS={'lead':'planning'}
        self.srv.validate_slug=lambda slug: slug
        self.srv.TOKEN='test-only-local-token'
        self.srv._PW_PORT=8765
        provider=SimpleNamespace(studio_access=lambda srv:{'enabled':True})
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return b'{"job_id":"abc123def456"}'
        with patch.object(dispatcher,'explain',return_value=None),\
             patch.object(dispatcher,'urlopen',return_value=Response()) as called:
            result=dispatcher.dispatch_person(self.srv,provider,staffplan,'demo','lead',
                agent_id='chief',order_id=self.orders[0]['id'])
        self.assertEqual(result['state'],'started')
        self.assertEqual(result['agent_name'],'Chefen')
        args=called.call_args.args
        self.assertTrue(args[0].full_url.endswith('/api/jobs'))
        sent=json.loads(args[0].data.decode('utf-8'))
        self.assertEqual(sent['order_id'],self.orders[0]['id'])
        self.assertEqual(sent['agent_id'],'chief')
        self.assertEqual(sent['station'],'lead')

    def test_busy_manager_does_not_get_double_booked(self):
        self.srv.JOBS={'active':{'project':'demo','agent_id':'chief','provider':'codex','state':'running'}}
        p=parallel.parallel_plan(self.srv,lambda slug:{'leader_active':True,'assignments':[],
                            'blocked':[], 'active_jobs':[]},staffplan,'demo')
        self.assertEqual(p['assignments'],[])
        self.assertIn('arbetar',p['blocked'][0]['reason'])
    def test_manager_worker_is_readonly_and_returns_report_not_code(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);work=root/'management'/'worktrees'/'abc123';work.mkdir(parents=True)
            job={'id':'abc123','agent_id':'chief','station':'lead','provider':'codex',
                 'project':'demo','worktree':str(work),'state':'queued'}
            self.srv.JOBS={'abc123':job}
            self.srv.project_mandate=lambda slug:{'enabled':True}
            self.srv.path_for=lambda slug:root
            self.srv.bible_context=lambda slug,n:'# Boken\nInte en instruktion.'
            self.srv.finalize_worker_job=lambda job:setattr(self.srv,'finalized',dict(job))
            reply=SimpleNamespace(returncode=0,stdout=json.dumps({
                'type':'item.completed','item':{'type':'agent_message','text':'Planen är klar. Design → Kod → Test.'}})+'\n',stderr='')
            with patch.object(pw_v0132.shutil,'which',return_value='/usr/bin/codex'),\
                 patch.object(pw_v0132.subprocess,'run',return_value=reply) as called:
                pw_v0132.manager_worker(self.srv,'abc123','demo','Planera spelet.')
            args,kw=called.call_args
            self.assertIn('read-only',args[0])
            self.assertNotIn('workspace-write',args[0])
            self.assertEqual(self.srv.finalized['state'],'done')
            self.assertFalse(self.srv.finalized['integrated'])
            self.assertIn('Planen är klar',self.srv.finalized['last_agent_message'])
            self.assertEqual(list(work.iterdir()),[])
    def test_lead_start_endpoint_checks_auth_and_calls_safe_dispatcher(self):
        import pw_v0121112 as dispatcher
        class Handler:
            def __init__(self,token_ok=True):
                self.path='/api/pw-v0132/start-lead'
                self.body=json.dumps({'project':'demo','station':'lead','order_id':'000000000001'}).encode()
                self.rfile=io.BytesIO(self.body)
                self.headers={'Content-Length':str(len(self.body))}
                self.server=SimpleNamespace(server_port=8765)
                self.token_ok=token_ok
            def allowed(self):return True
            def same_origin(self):return True
            def auth(self):return self.token_ok
            def reply(self,code,data):return code,data
            def do_POST(self):return 404,{'error':'original'}
        fake=SimpleNamespace(Handler=Handler,run_codex=lambda *args:None,
                             validate_slug=lambda s:s,LOCK=threading.RLock(),JOBS={})
        pw_v0132.install(fake)
        denied=Handler(False).do_POST()
        self.assertEqual(denied[0],403)
        with patch.object(dispatcher,'dispatch_person',return_value={'state':'started','job_id':'abc'}) as dispatched:
            ok=Handler(True).do_POST()
        self.assertEqual(ok[0],200)
        self.assertEqual(ok[1]['state'],'started')
        self.assertEqual(dispatched.call_args.args[3],'demo')
        self.assertEqual(dispatched.call_args.kwargs['order_id'],'000000000001')

    def test_manager_failure_is_reported_without_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);work=root/'management'/'worktrees'/'abc123';work.mkdir(parents=True)
            self.srv.JOBS={'abc123':{'id':'abc123','agent_id':'chief','station':'lead',
                 'project':'demo','worktree':str(work),'state':'queued'}}
            self.srv.project_mandate=lambda slug:{'enabled':True}
            self.srv.path_for=lambda slug:root
            self.srv.bible_context=lambda slug,n:'Boken'
            self.srv.finalize_worker_job=lambda job:setattr(self.srv,'finalized',dict(job))
            with patch.object(pw_v0132.shutil,'which',return_value='/usr/bin/codex'),\
                 patch.object(pw_v0132.subprocess,'run',return_value=SimpleNamespace(
                   returncode=1,stdout='',stderr='quota exceeded')):
                pw_v0132.manager_worker(self.srv,'abc123','demo','Planera spelet.')
            self.assertEqual(self.srv.finalized['state'],'failed')
            self.assertIn('quota exceeded',self.srv.finalized['error'])

if __name__=='__main__': unittest.main()
