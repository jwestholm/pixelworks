import unittest
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pw_v0121111 as target

class Fake:
    def __init__(self):
        import threading
        self.LOCK=threading.RLock();self.JOBS={}
        self.staff=[dict(id='g',name='Greta',role_type='writer',role='Creative Director',provider='gemini',station='cafe',home_station='docs',allowed_stations=['docs','meeting','research']),dict(id='u',name='Gunnar',role_type='allround',role='Allroundare',provider='codex',station='meeting',home_station='code',allowed_stations=['docs','meeting','code']),dict(id='c',name='Chefen',role_type='lead',role='Arbetsledare',provider='codex',station='lead',home_station='lead',allowed_stations=['lead'])]
        self.orders=[dict(id='1',status='waiting',station='meeting',priority=2,instruction='Skapa en ny spelidé med karaktärer')]
    def staff_read(self,slug):return self.staff
    def orders_read(self,slug):return self.orders
    def get_skill_settings(self,slug):return {'g':{'meeting':{'level':5}},'u':{'meeting':{'level':5}}}
    def agent_authorized(self,slug,p,station):return station in p['allowed_stations']
    def status(self):return {'execution_enabled':True}

class Tests(unittest.TestCase):
    def setUp(self):self.s=Fake()
    def test_creative_person_first_even_when_codex_at_desk(self):
        self.assertEqual('Greta',target.selection(self.s,'minesweeper',self.s.orders[0])['name'])
    def test_programmer_selected_for_code(self):
        order={'station':'code','instruction':'Implementera javascript inventariesystem'}
        self.assertEqual('Gunnar',target.selection(self.s,'minesweeper',order)['name'])
    def test_blocked_specialist_does_not_fallback(self):
        base=lambda slug:{'assignments':[{'order_id':'1','agent_id':'u','station':'meeting','agent_name':'Gunnar'}], 'blocked':[], 'next':{}, 'leader_active':True}
        with patch.object(target,'_capacity',return_value='Jag behöver vänta'):
            result=target.plan_for_staff(self.s,'minesweeper',base)
        self.assertEqual([],result['assignments'])
        self.assertIn('Greta väntar',result['blocked'][0]['reason'])
    def test_provider_does_not_change_ranking(self):
        first=target.selection(self.s,'minesweeper',self.s.orders[0])['id']
        self.s.staff[0]['provider']='codex';self.s.staff[1]['provider']='gemini'
        self.assertEqual(first,target.selection(self.s,'minesweeper',self.s.orders[0])['id'])
    def test_busy_specialist_not_replaced(self):
        self.assertEqual('Greta',target.selection(self.s,'minesweeper',self.s.orders[0],working={'g'})['name'])
    def test_status_human_readable(self):
        with patch.object(target,'_capacity',return_value=None):
            entries=target.worker_status(self.s,'minesweeper')
        self.assertEqual('waiting',entries[0]['state'])
        self.assertNotIn('Gemini',entries[0]['message'])

if __name__=='__main__':unittest.main()
