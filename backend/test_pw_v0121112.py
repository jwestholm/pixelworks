import sys, unittest, threading, tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_v0121112 as mod

class Provider:
    CONF_LOCK=threading.RLock()
    def __init__(self):self.config={};self._status=dict(configured=True,test_is_generation=True,paused_until_day=None,used_today=12,can_send=False)
    def _cfg_file(self,srv):return '/tmp/not-written-by-tests'
    def _read_json(self,path,default):return dict(self.config)
    def _write_json(self,path,data):self.config=dict(data)
    def studio_access(self,srv):return {'enabled':True}
    def gemini_status(self,srv):return mod.apply_limit(self,srv,self._status)
    def start_auto_job(self,srv,slug,order,p):return 'abcdef123456'

class StaffPlanner:
    @staticmethod
    def _eligible(srv,slug,p,order):return order['station'] in p.get('allowed_stations',[]) and p['role_type']!='lead'
    @staticmethod
    def selection(srv,slug,order,people=None):return (people or srv.staff_read(slug))[0]

class Fake:
    def __init__(self):
        self.LOCK=threading.RLock();self.JOBS={};self.TOKEN='test-token'
        self.SKILL_STATIONS={'docs':'documentation','meeting':'meeting'}
        self.people=[{'id':'greta','name':'Greta','role_type':'writer','provider':'gemini','station':'docs','allowed_stations':['docs']},
                     {'id':'gunnar','name':'Gunnar','role_type':'allround','provider':'codex','station':'docs','allowed_stations':['docs']}]
        self.orders=[{'id':'1234','status':'waiting','station':'docs','priority':2,'instruction':'Skapa en egen spelfigur med unik personlighet'}]
        self._PW_PORT=8765
    def validate_slug(self,slug):
        if slug!='minesweeper':raise ValueError('Ogiltigt projekt')
        return slug
    def orders_read(self,slug):return self.orders
    def staff_read(self,slug):return self.people
    def status(self):return {'execution_enabled':True}

class Tests(unittest.TestCase):
    def setUp(self):self.s=Fake();self.provider=Provider()
    def test_local_cap_defaults_to_12_and_is_not_google_quota(self):
        r=self.provider.gemini_status(self.s)
        self.assertEqual(12,r['daily_limit']);self.assertFalse(r['can_send']);self.assertTrue(r['local_limit_exhausted']);self.assertIn('lokalt',r['limit_source'])
    def test_owner_can_set_higher_local_limit_without_resetting_uses(self):
        self.provider.config['owner_local_daily_limit']=25
        r=self.provider.gemini_status(self.s)
        self.assertEqual(25,r['daily_limit']);self.assertEqual(12,r['used_today']);self.assertTrue(r['can_send'])
    def test_bad_setting_falls_back_safely(self):
        for n in (-1,10,501,True,'100'):
            self.provider.config['owner_local_daily_limit']=n
            self.assertEqual(12,mod.local_limit(self.provider,self.s))
    def test_real_pause_or_failed_test_always_blocks_even_after_limit_raise(self):
        self.provider.config['owner_local_daily_limit']=100
        self.provider._status['paused_until_day']='2026-10-23'
        self.assertFalse(self.provider.gemini_status(self.s)['can_send'])
        self.provider._status['paused_until_day']=None
        self.provider._status['test_is_generation']=False
        self.assertFalse(self.provider.gemini_status(self.s)['can_send'])
    def test_block_reason_accurately_names_person_and_local_cap(self):
        msg=mod.explain(self.provider,self.s,self.s.people[0]);self.assertIn('Greta',msg);self.assertIn('12/12',msg);self.assertIn('LOKALA',msg);self.assertNotIn('Codex',msg)
    def test_manual_greta_blocked_without_external_call(self):
        with patch.object(self.provider,'start_auto_job',side_effect=AssertionError('No provider request')):
            r=mod.dispatch_person(self.s,self.provider,StaffPlanner,'minesweeper','docs','greta')
        self.assertEqual('blocked',r['state']);self.assertIn('LOKALA',r['message'])
    def test_manual_gunnar_beats_greta_and_starts_via_safe_api(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return b'{"job_id":"abc123"}'
        with patch.object(mod,'urlopen',return_value=Response()) as send:
            r=mod.dispatch_person(self.s,self.provider,StaffPlanner,'minesweeper','docs','gunnar')
        self.assertEqual('started',r['state']);self.assertEqual('Gunnar',r['agent_name'])
        payload=__import__('json').loads(send.call_args.args[0].data)
        self.assertEqual('gunnar',payload['agent_id']);self.assertEqual('1234',payload['order_id']);self.assertTrue(payload['isolated'])
    def test_manual_cannot_force_nonpermitted_station(self):
        self.s.people[1]['allowed_stations']=[]
        r=mod.dispatch_person(self.s,self.provider,StaffPlanner,'minesweeper','docs','gunnar')
        self.assertEqual('blocked',r['state'])
    def test_manual_cannot_start_when_no_waiting_order(self):
        self.s.orders[0]['status']='review'
        r=mod.dispatch_person(self.s,self.provider,StaffPlanner,'minesweeper','docs','gunnar')
        self.assertEqual('idle',r['state'])
    def test_no_explicit_employee_still_prefers_greta(self):
        r=mod.dispatch_person(self.s,self.provider,StaffPlanner,'minesweeper','docs')
        self.assertEqual('blocked',r['state']);self.assertEqual('Greta',r['agent_name'])
    def test_no_studio_consent(self):
        self.provider.studio_access=lambda srv:{'enabled':False}
        r=mod.dispatch_person(self.s,self.provider,StaffPlanner,'minesweeper','docs','gunnar')
        self.assertEqual('blocked',r['state']);self.assertIn('Studioåtkomst',r['message'])

if __name__=='__main__':unittest.main()
