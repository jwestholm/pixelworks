"""Offline regression tests for v0.12.11.13. No external requests."""
import hashlib, io, json, tempfile, time, unittest
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import patch
import pw_v01210 as pw
import pw_v0121112 as capacity

class Fake:
    def __init__(self,root):
        self.ROOT=Path(root)
        self.ROOT.joinpath('secrets').mkdir(parents=True)
        self.ROOT.joinpath('secrets','gemini.key').write_text('TEST-ONLY-NOT-REAL-KEY')
    def gemini_key_file(self):return self.ROOT/'secrets'/'gemini.key'

class OKResponse:
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n=None):return json.dumps({'candidates':[{'content':{'parts':[{'text':'OK'}]}}]}).encode()

class Tests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory();self.s=Fake(self.dir.name)
        self.set_verified()
    def tearDown(self):self.dir.cleanup()
    def set_verified(self):
        pw._write_json(pw._cfg_file(self.s),{'test_result':'ansluten', 'tested_model':pw.MODEL,
            'tested_key_sha256':hashlib.sha256(self.s.gemini_key_file().read_bytes()).hexdigest(),
            'owner_local_daily_limit':12})
    def status(self):
        return capacity.apply_limit(pw,self.s,pw.gemini_status(self.s))
    def test_old_cap_ignored_even_if_usage_is_800(self):
        pw._write_json(pw._counter_file(self.s),{'date':pw.google_day(),'count':800})
        state=self.status()
        self.assertIsNone(state['daily_limit']);self.assertEqual(800,state['used_today']);self.assertTrue(state['can_send'])
        self.assertFalse(state['local_limit_exhausted'])
    def test_reservation_above_old_cap_is_local_only(self):
        pw._write_json(pw._counter_file(self.s),{'date':pw.google_day(),'count':100})
        with patch.object(pw,'urlopen',side_effect=AssertionError('Must not call Google')):
            self.assertEqual('TEST-ONLY-NOT-REAL-KEY',pw.reserve_gemini_call(self.s))
        self.assertEqual(101,self.status()['used_today'])
    def test_manual_verification_does_not_hit_old_cap(self):
        pw._write_json(pw._counter_file(self.s),{'date':pw.google_day(),'count':600})
        with patch.object(pw,'urlopen',return_value=OKResponse()) as send:
            result=pw.test_gemini_connection(self.s)
        self.assertTrue(result['verified']);self.assertEqual(601,self.status()['used_today'])
        self.assertEqual(1,send.call_count)
    @staticmethod
    def error(desc,headers=None):
        return HTTPError(pw.GEMINI_URL,429,'Too many requests',headers or {},io.BytesIO(json.dumps({'error':{'message':desc}}).encode()))
    def test_google_minute_rate_response_respects_retry_after(self):
        with patch.object(pw,'urlopen',side_effect=self.error('Too many requests per minute RPM',{'Retry-After':'120'})) as send:
            with self.assertRaises(pw.GoogleQuotaError) as ctx:pw._gemini_send('TEST','Hej')
        self.assertFalse(ctx.exception.daily);self.assertEqual(120,ctx.exception.retry_seconds);self.assertEqual(1,send.call_count)
        pw.mark_auto_pause(self.s,ctx.exception)
        st=self.status();self.assertFalse(st['can_send']);self.assertIsNotNone(st['paused_until_epoch']);self.assertIsNone(st['paused_until_day'])
        with patch.object(pw.time,'time',return_value=time.time()+121):
            self.assertTrue(self.status()['can_send'])
    def test_google_daily_quota_pauses_until_google_day(self):
        e=self.error('Quota exceeded: GenerateRequestsPerDay 500')
        q=pw._quota_error(e);self.assertTrue(q.daily)
        pw.mark_auto_pause(self.s,q)
        self.assertFalse(self.status()['can_send']);self.assertEqual(pw.google_day(),self.status()['paused_until_day'])
    def test_unknown_429_cannot_be_misreported_as_15rpm(self):
        q=pw._quota_error(self.error('RESOURCE_EXHAUSTED'))
        self.assertFalse(q.daily);self.assertIn('429',str(q));self.assertNotIn('15',str(q))
    def test_manual_connection_429_does_not_erase_previous_verification(self):
        with patch.object(pw,'urlopen',side_effect=self.error('RPM reached',{'Retry-After':'60'})) as send:
            outcome=pw.test_gemini_connection(self.s)
        self.assertEqual('kvotgräns nådd',outcome['status']);self.assertEqual(1,send.call_count)
        s=self.status();self.assertTrue(s['test_is_generation']);self.assertFalse(s['can_send'])
    def test_unverified_or_no_key_still_blocks(self):
        self.s.gemini_key_file().unlink()
        self.assertFalse(self.status()['can_send'])
        self.s.gemini_key_file().write_text('DIFFERENT-KEY')
        self.assertFalse(self.status()['can_send'])
    def test_legacy_limit_endpoint_not_present_in_ui(self):
        client=Path(__file__).parent.parent/'src'/'pw-v0121112.js'
        js=client.read_text()
        self.assertNotIn('data-capacity-save',js)
        self.assertNotIn('data-capacity-value',js)
        self.assertIn('Ingen lokal dygnsgräns',js)
if __name__=='__main__':unittest.main()
