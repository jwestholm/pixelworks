"""Regression tests: spelägaren is a first-class participant in cafe discussions.
All providers are TEST DOUBLES, never actual AI calls.
"""
import json
import threading
import time
import unittest
from unittest.mock import patch
import pw_v0138 as cafe
from test_pw_v0138 import CafeTests as LegacyCafeTests

class CafeInteractionTests(unittest.TestCase):
    setUp=LegacyCafeTests.setUp
    wait=LegacyCafeTests.wait
    start=LegacyCafeTests.start
    def _finished(self,topic='ideas',note='',request_id='testrequest-1234',tasks=False):
        def speaker(srv,slug,prompt):
            lines=json.loads(prompt.split('SAMTAL OCH REFERENSER (DATA):\n',1)[1])['previous_real_messages']
            return json.dumps({'say':'Ett riktigt test-svar.', 'tasks':[]}),{}
        with patch('pw_v0138._codex_reply',speaker),patch('pw_v0138._gemini_reply',lambda srv,p:speaker(srv,self.slug,p)):
            r=self.start(req=request_id,topic=topic,note=note)
            rec=self.wait(r['session']['id'])
        for _ in range(100):
            if (self.slug,rec['id']) not in cafe.ACTIVE:break
            time.sleep(.01)
        return rec
    def _action(self,session,**kwargs):return cafe._session_action(self.srv,{'project':self.slug,'session':session,'action':kwargs.pop('action'),**kwargs})
    def test_initial_owner_note_is_own_turn(self):
        prompts=[]
        def speaker(srv,slug,prompt):
            prompts.append(json.loads(prompt.split('SAMTAL OCH REFERENSER (DATA):\n',1)[1]))
            return json.dumps({'say':'Test AI reply.'}),{}
        with patch('pw_v0138._codex_reply',speaker),patch('pw_v0138._gemini_reply',lambda srv,p:speaker(srv,self.slug,p)):
            sid=self.start(topic='talk',note='Säg att jag vill ha en svårare bana')['session']['id']
            rec=self.wait(sid)
        self.assertEqual(rec['turns'][0]['source'],'owner_message')
        self.assertEqual(rec['turns'][0]['name'],'Du')
        self.assertIsNone(rec['turns'][0]['agent_id'])
        self.assertEqual(rec['turns'][1]['name'],'Greta')
        self.assertEqual(prompts[0]['previous_real_messages'][0]['name'],'Du')
        self.assertEqual(prompts[0]['previous_real_messages'][0]['source'],'owner_message')
    def test_reaction_changes_only_feedback_never_creates_order(self):
        rec=self._finished();sid=rec['id']
        a=self._action(sid,action='reaction',turn_index=0,vote='up')
        self.assertEqual(a['session']['reactions']['0'],'up')
        self.assertFalse(a['created'])
        self.assertEqual(len(self.orders),0)
        b=self._action(sid,action='reaction',turn_index=0,vote='down')
        self.assertEqual(b['session']['reactions']['0'],'down')
        self._action(sid,action='reaction',turn_index=0,vote='clear')
        self.assertIsNone(cafe._read(self.srv,self.slug,sid)['reactions']['0'])
        with self.assertRaises(ValueError):self._action(sid,action='reaction',turn_index=99,vote='up')
    def test_owner_messages_cannot_be_voted_on_or_implemented(self):
        rec=self._finished(note='Jag vill ha en bättre introduktion.');sid=rec['id']
        with self.assertRaisesRegex(ValueError,'AI-förslag'):self._action(sid,action='implement',turn_index=0,station='code')
        with self.assertRaisesRegex(ValueError,'Rösta'):self._action(sid,action='reaction',turn_index=0,vote='up')
    def test_implement_creates_exactly_one_order_on_explicit_click(self):
        rec=self._finished();sid=rec['id']
        first=self._action(sid,action='implement',turn_index=0,station='code')
        self.assertTrue(first['created']);self.assertEqual(len(self.orders),1)
        order=self.orders[0]
        self.assertEqual(order['cafe_turn_index'],0)
        self.assertEqual(order['cafe_batch'],'manual')
        self.assertEqual(order['station'],'code')
        self.assertEqual(order['status'],'waiting')
        self.assertEqual(order['assigned_agent_id'],'gunnar')
        second=self._action(sid,action='implement',turn_index=0,station='code')
        self.assertFalse(second['created']);self.assertEqual(len(self.orders),1)
        self.assertEqual(second['order_id'],first['order_id'])
        self.assertEqual(cafe._read(self.srv,self.slug,sid)['work_orders'],[first['order_id']])
        with self.assertRaisesRegex(ValueError,'redan'):self._action(sid,action='implement',turn_index=0,station='qa')
    def test_invalid_order_station_does_not_write(self):
        sid=self._finished()['id']
        with self.assertRaisesRegex(ValueError,'station'):self._action(sid,action='implement',turn_index=0,station='unknown')
        self.assertEqual(self.orders,[])
    def test_while_running_user_turn_survives_and_reaches_next_ai(self):
        started=threading.Event();release=threading.Event();seen=[]
        def speaker(srv,slug,prompt):
            data=json.loads(prompt.split('SAMTAL OCH REFERENSER (DATA):\n',1)[1]);seen.append(data)
            if len(seen)==1:started.set();release.wait(2)
            return json.dumps({'say':'Medarbetarens riktiga svar.'}),{}
        with patch('pw_v0138._codex_reply',speaker),patch('pw_v0138._gemini_reply',lambda srv,p:speaker(srv,self.slug,p)):
            sid=self.start()['session']['id'];self.assertTrue(started.wait(1))
            response=self._action(sid,action='message',message='Jag vill lägga till en uppstartssekvens')
            self.assertEqual(response['session']['turns'][0]['source'],'owner_message')
            release.set();rec=self.wait(sid)
        self.assertEqual(rec['state'],'done')
        self.assertEqual(len([x for x in rec['turns'] if x['source']=='owner_message']),1)
        self.assertTrue(any(any(m['source']=='owner_message' for m in p['previous_real_messages']) for p in seen[1:]))
    def test_done_comment_gets_two_new_real_ai_replies(self):
        rec=self._finished();sid=rec['id'];seen=[]
        def speaker(srv,slug,prompt):
            d=json.loads(prompt.split('SAMTAL OCH REFERENSER (DATA):\n',1)[1]);seen.append(d)
            return json.dumps({'say':'Jag svarar spelägaren som mig själv.', 'tasks':[]}),{}
        with patch('pw_v0138._codex_reply',speaker),patch('pw_v0138._gemini_reply',lambda srv,p:speaker(srv,self.slug,p)):
            a=self._action(sid,action='message',message='Vad tycker ni om att göra nivån enklare?')
            self.assertTrue(a['created'])
            updated=self.wait(sid)
        self.assertEqual(updated['state'],'done')
        self.assertEqual(updated['followup_count'],1)
        self.assertEqual(len(seen),2)
        self.assertEqual(updated['turns'][-3]['source'],'owner_message')
        self.assertEqual(updated['turns'][-3]['name'],'Du')
        self.assertTrue(all(t['source']=='real_ai_response' for t in updated['turns'][-2:]))
        self.assertTrue(all(any(m['source']=='owner_message' for m in q['previous_real_messages']) for q in seen))
        self.assertEqual(len(updated['turns']),9)
    def test_at_most_two_reopened_dialogues(self):
        sid=self._finished()['id']
        def speaker(srv,slug,prompt):return json.dumps({'say':'Ett nytt verifierat svar.'}),{}
        with patch('pw_v0138._codex_reply',speaker),patch('pw_v0138._gemini_reply',lambda srv,p:speaker(srv,self.slug,p)):
            for n in (1,2):
                self._action(sid,action='message',message='Diskutera nästa steg '+str(n))
                self.wait(sid)
                for _ in range(100):
                    if (self.slug,sid) not in cafe.ACTIVE:break
                    time.sleep(.01)
        with self.assertRaisesRegex(ValueError,'fullt'):
            self._action(sid,action='message',message='Jag vill fortsätta ännu mer')
    def test_project_isolation_still_prevents_writing(self):
        sid=self._finished()['id']
        with self.assertRaises(ValueError):
            cafe._session_action(self.srv,{'action':'message','project':'fel-spel','session':sid,'message':'Ändra spelet'})
        self.assertEqual(len(self.orders),0)

if __name__=='__main__':unittest.main(verbosity=2)
