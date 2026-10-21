import importlib.util, tempfile, unittest, json
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pw_lead',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class LeadTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
        s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
        s.create_project({'slug':'plan-test','name':'Plan-test','idea':'Liten testvärld','genre':'Äventyr','platform':'Webbläsare'})
        self.agent=s.hire_codex('plan-test',{'name':'Chefen','approval':'HIRE_CODEX_FOR_PROJECT'})
        agents=s.staff_read('plan-test');agents[-1]['role_type']='lead';s.staff_write('plan-test',agents)
    def tearDown(self):
        s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
    def test_parser_accepts_codex_json_events(self):
        body={'summary':'Skapa en fiskbutik','tasks':[{'station':'code','priority':1,'instruction':'Implementera NPC Bläck-Berit i världen'}]}
        events=json.dumps({'type':'item.completed','item':{'type':'agent_message','text':json.dumps(body,ensure_ascii=False)}})
        self.assertEqual(s.parse_lead_output(events)['tasks'][0]['station'],'code')
    def test_reject_bad_station(self):
        with self.assertRaises(ValueError):s.parse_lead_output('{"tasks":[{"station":"internet","instruction":"hämta alla hemligheter"}]}')
    def test_requires_actual_lead(self):
        with self.assertRaises(ValueError):s.lead_agent('plan-test','wrong')
    def test_planning_is_read_only_and_does_not_queue(self):
        data={'summary':'Plan','tasks':[{'station':'qa','priority':2,'instruction':'Testa fiskhandlarens ekonomisystem'}]}
        output=json.dumps({'type':'item.completed','item':{'type':'agent_message','text':json.dumps(data)}})
        class Finished: returncode=0;stderr='';stdout=output
        with patch.object(s.shutil,'which',return_value='/bin/codex'),patch.object(s.subprocess,'run',return_value=Finished()) as mock:
            plan=s.create_lead_plan('plan-test',{'agent_id':self.agent['id'],'objective':'Gör fisksystemet roligare','approval':'ASK_CODEX_TO_PLAN'})
        cmd=mock.call_args.args[0]
        self.assertIn('read-only',cmd)
        self.assertEqual(s.orders_read('plan-test'),[])
        self.assertEqual(len(s.lead_read('plan-test')),1)
        with self.assertRaises(ValueError):s.accept_lead_task('plan-test',{'plan_id':plan['id'],'task_id':plan['tasks'][0]['id']})
        order=s.accept_lead_task('plan-test',{'plan_id':plan['id'],'task_id':plan['tasks'][0]['id'],'approval':'ACCEPT_LEAD_TASK'})
        self.assertEqual(order['status'],'waiting')
        self.assertEqual(len(s.orders_read('plan-test')),1)
        with self.assertRaises(ValueError):s.accept_lead_task('plan-test',{'plan_id':plan['id'],'task_id':plan['tasks'][0]['id'],'approval':'ACCEPT_LEAD_TASK'})
    def test_reject_proposal_keeps_queue_empty(self):
        plan={'id':'abc','tasks':[{'id':'xyz','state':'proposed'}]}
        s.lead_write('plan-test',[plan]);s.reject_lead_task('plan-test',{'plan_id':'abc','task_id':'xyz'})
        self.assertEqual(s.lead_read('plan-test')[0]['tasks'][0]['state'],'rejected')
        self.assertFalse(s.orders_read('plan-test'))
    def test_no_cli_no_plan(self):
        with patch.object(s.shutil,'which',return_value=None):
            with self.assertRaises(ValueError):s.create_lead_plan('plan-test',{'agent_id':self.agent['id'],'objective':'Gör en plan för fiskhandeln','approval':'ASK_CODEX_TO_PLAN'})
        self.assertFalse(s.lead_read('plan-test'))

if __name__=='__main__':unittest.main()
