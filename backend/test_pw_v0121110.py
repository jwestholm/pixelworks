import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_v0121110 as meeting

class MockSrv:
    def validate_slug(self,s):
        if s!='demo':raise ValueError('wrong project')
        return s
    def orders_read(self,s):return [{'id':'o1','status':'waiting','station':'meeting'}]

class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.srv=MockSrv()
        self.mod=types.ModuleType('pw_v01210')
        self.mod.SAFE_GEMINI_STATIONS=frozenset(('meeting','docs','research'))
        self.mod.studio_access=lambda s:{'enabled':True}
        self.mod.gemini_status=lambda s:{'can_send':True,'configured':True,'used_today':0,'daily_limit':12}
        self.mod.auto_candidate=lambda s,p:({'id':'o1','station':'meeting'},{'name':'Greta'},object())
        self.calls=[]
        self.mod.start_auto_job=lambda *args:self.calls.append(args) or 'abc123'
        self.patcher=patch.dict(sys.modules,{'pw_v01210':self.mod});self.patcher.start()
    def tearDown(self):self.patcher.stop()
    def test_meeting_starts_from_eligible_worker(self):
        r=meeting.dispatch_now(self.srv,'demo','meeting')
        self.assertEqual(r['state'],'started');self.assertIn('Greta',r['message']);self.assertEqual(len(self.calls),1)
    def test_no_studio_consent_blocks_without_call(self):
        self.mod.studio_access=lambda s:{'enabled':False}
        self.assertEqual(meeting.dispatch_now(self.srv,'demo','meeting')['state'],'blocked')
        self.assertFalse(self.calls)
    def test_quota_blocks_without_call(self):
        self.mod.gemini_status=lambda s:{'can_send':False,'configured':True,'used_today':12,'daily_limit':12}
        self.assertIn('dagstak',meeting.dispatch_now(self.srv,'demo','meeting')['message'])
        self.assertFalse(self.calls)
    def test_no_worker_reports_blocked(self):
        self.mod.auto_candidate=lambda *args:None
        self.assertEqual(meeting.dispatch_now(self.srv,'demo','meeting')['state'],'blocked')
    def test_never_start_wrong_station_order(self):
        self.mod.auto_candidate=lambda s,p:({'id':'o2','station':'docs'},{'name':'Greta'},object())
        self.assertEqual(meeting.dispatch_now(self.srv,'demo','meeting')['state'],'queued_elsewhere')
        self.assertFalse(self.calls)
    def test_safe_non_advisory_station(self):
        self.assertEqual(meeting.dispatch_now(self.srv,'demo','code')['state'],'not_applicable')
        self.assertFalse(self.calls)

if __name__=='__main__':unittest.main()
