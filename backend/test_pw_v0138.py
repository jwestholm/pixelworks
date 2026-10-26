"""Offline contract tests. Provider replies below are test doubles, NEVER shipped as cafe dialogue."""
import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_v0138 as cafe

class CafeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.slug='spel'
        project=self.root/self.slug
        (project/'management').mkdir(parents=True)
        (project/'work').mkdir()
        (project/'project.json').write_text(json.dumps({'id':self.slug}),encoding='utf-8')
        self.staff=[
          {'id':'gunnar','name':'Gunnar','provider':'codex','role_type':'programmer','role':'Programmerare','station':'code','work_mode':'autonomous','skills':{'coding':5},'allowed_stations':['code','qa']},
          {'id':'greta','name':'Greta','provider':'gemini','role_type':'writer','role':'Game Designer','station':'docs','work_mode':'autonomous','skills':{'documentation':5},'allowed_stations':['docs','research']},
          {'id':'chief','name':'Chefen','provider':'codex','role_type':'lead','role':'Arbetsledare','station':'lead','work_mode':'autonomous','skills':{'planning':5},'allowed_stations':['lead']},
        ]
        self.jobs={};self.orders=[]
        self.srv=SimpleNamespace(ROOT=self.root,LOCK=threading.RLock(),JOBS=self.jobs,
           path_for=lambda slug:self.root/slug,
           validate_slug=lambda slug:slug if slug==self.slug else (_ for _ in ()).throw(ValueError('Fel spel')),
           staff_read=lambda slug:self.staff,
           bible_context=lambda slug,amount:'Detta är ett pusselspel.',
           project_mandate=lambda slug:{'enabled':True},
           orders_read=lambda slug:list(self.orders),
           orders_write=lambda slug,rows:self.orders.__setitem__(slice(None),rows),
           get_skill_settings=lambda slug:{},
           agent_authorized=lambda slug,member,station:station in member.get('allowed_stations',[]),
           SKILL_STATIONS={'code':'coding','docs':'documentation','lead':'planning','qa':'testing'})
        self.p1=patch('pw_v0138._provider_ready',lambda srv,p:True)
        self.p2=patch('pw_v0138._check_access',lambda srv,slug:None)
        self.p1.start();self.p2.start();self.addCleanup(self.p1.stop);self.addCleanup(self.p2.stop)
        self.p3=patch('pw_v0133._assign', lambda srv,slug,steps:[('gunnar','Gunnar') for s in steps]);self.p3.start();self.addCleanup(self.p3.stop)
        self.call_prompts=[]
    def providers(self,finish_qa=True):
        def codex(srv,slug,prompt):
            self.call_prompts.append(prompt)
            d=json.loads(prompt.split('SAMTAL OCH REFERENSER (DATA):\n',1)[1])
            prior=d.get('previous_real_messages') or []
            self.assertEqual(len(prior),len(self.call_prompts)-1)
            if 'Svara ENBART JSON:' in prompt and 'tasks' in prompt:
                task={'station':'qa','title':'Testa huvudmekaniken','instruction':'Kontrollera samtliga spelregler i den spelbara prototypen.', 'priority':2}
                return json.dumps({'say':'Jag föreslår att testaren testar spelet.','tasks':[task] if finish_qa else []}),{}
            return json.dumps({'say':'Jag hör vad ni säger och vill förbättra känslan.'}),{}
        def gemini(srv,prompt):return codex(srv,'spel',prompt)
        return patch('pw_v0138._codex_reply',codex), patch('pw_v0138._gemini_reply',gemini)
    def wait(self,sid):
        for _ in range(350):
            rec=cafe._read(self.srv,self.slug,sid)
            if rec['state']!='running':return rec
            time.sleep(.01)
        self.fail('Conversation did not complete')
    def start(self,req='testrequest-1234',topic='talk',note=''):
        return cafe.begin(self.srv,{'project':self.slug,'topic':topic,'note':note,'request_id':req})
    def test_real_turns_linked_to_prior_dialogue(self):
        a,b=self.providers();
        with a,b:
            result=self.start();rec=self.wait(result['session']['id'])
        self.assertEqual(rec['state'],'done')
        self.assertEqual(len(rec['turns']),6)
        self.assertEqual(len(self.call_prompts),6)
        self.assertEqual({t['source'] for t in rec['turns']},{'real_ai_response'})
        self.assertEqual(rec['turns'][0]['name'],'Greta')
        self.assertEqual(rec['turns'][-1]['name'],'Chefen')
        self.assertEqual(len(rec['work_orders']),1)
        self.assertEqual(self.orders[0]['station'],'qa')
        self.assertFalse(self.orders[0]['status']=='done')
    def test_a_test_topic_creates_qa_from_real_dialogue(self):
        a,b=self.providers(finish_qa=False)
        with a,b:
            rec=self.wait(self.start(topic='test')['session']['id'])
        self.assertEqual(rec['state'],'done')
        self.assertEqual(self.orders[0]['station'],'qa')
        self.assertEqual(len(self.orders),1)
    def test_no_fake_talk_if_provider_fails(self):
        with patch('pw_v0138._codex_reply',side_effect=RuntimeError('Kunde inte ansluta')):
            rec=self.wait(self.start()['session']['id'])
        self.assertEqual(rec['state'],'failed')
        self.assertEqual(len(rec['turns']),0)
        self.assertEqual(self.orders,[])
    def test_replayed_request_does_not_restart(self):
        a,b=self.providers();
        with a,b:
            first=self.start();self.wait(first['session']['id'])
            second=self.start()
        self.assertEqual(first['session']['id'],second['session']['id'])
        self.assertFalse(second['created'])
        self.assertEqual(len(self.call_prompts),6)
        self.assertEqual(len(self.orders),1)
    def test_only_one_session_at_a_time(self):
        blocking=threading.Event()
        def stall(*args):blocking.wait(1);raise RuntimeError('Offline')
        with patch('pw_v0138._gemini_reply',side_effect=stall):
            self.start()
            with self.assertRaisesRegex(ValueError,'pågår redan'):self.start(req='another-request-123')
            blocking.set()
        for _ in range(100):
            if not cafe.ACTIVE:break
            time.sleep(.01)
    def test_two_participants_if_only_two_available(self):
        self.staff.pop(0)
        a,b=self.providers();
        with a,b:
            rec=self.wait(self.start()['session']['id'])
        self.assertEqual(len(rec['participants']),2)
        self.assertEqual(len(rec['turns']),4)
    def test_not_enough_employees(self):
        self.staff[:]=self.staff[:1]
        with self.assertRaisesRegex(ValueError,'minst två'):self.start()
        self.assertFalse(cafe.ACTIVE)
    def test_other_requires_real_topic(self):
        with self.assertRaisesRegex(ValueError,'Skriv vad'):self.start(topic='other')
    def test_requires_existing_mandate(self):
        self.p2.stop()
        with patch('pw_v01210.studio_access',return_value={'enabled':True}):
            self.srv.project_mandate=lambda slug:{'enabled':False}
            with self.assertRaisesRegex(ValueError,'arbetsmandat'):self.start()
    def test_project_isolation(self):
        with self.assertRaises(ValueError):cafe.overview(self.srv,'annat')
        with self.assertRaises(ValueError):self.start(req='request-123456789',note='',topic='wrong')
    def test_cafe_jobs_are_not_claimed_by_dispatcher(self):
        a,b=self.providers();
        with a,b:
            rec=self.wait(self.start()['session']['id'])
        self.assertEqual(rec['state'],'done')
        self.assertTrue(all(j['state']=='done' and not j['integrated'] for j in self.jobs.values()))
    def test_duplicate_followups_filtered(self):
        a,b=self.providers();
        with a,b:
            first=self.wait(self.start()['session']['id'])
            second=self.wait(self.start(req='another-request-123')['session']['id'])
        self.assertEqual(len(first['work_orders']),1)
        self.assertEqual(second['work_orders'],[])
        self.assertEqual(len(self.orders),1)

if __name__=='__main__':unittest.main(verbosity=2)
