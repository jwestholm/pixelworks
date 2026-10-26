import copy
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('pw_v0121114', HERE/'pw_v0121114.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class FakeLock:
    def __enter__(self): return self
    def __exit__(self,*args): pass

class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.orders=[{'id':'orderA','job_id':'aaaaaa111111','status':'review'},
                     {'id':'orderB','job_id':'bbbbbb111111','status':'review'},
                     {'id':'orderC','job_id':'cccccc111111','status':'archived'},
                     {'id':'orderD','job_id':'dddddd111111','status':'review'},
                     {'id':'orderE','job_id':'eeeeee111111','status':'waiting'}]
        self.reports=[{'id':'aaaaaa111111','order_id':'orderA','review_decision':'approve','state':'review'},
                      {'id':'bbbbbb111111','order_id':'orderB','review_decision':'forward','state':'review'},
                      {'id':'cccccc111111','order_id':'orderC','review_decision':'approve','state':'review'},
                      {'id':'dddddd111111','order_id':'other_order','review_decision':'approve','state':'review'},
                      {'id':'eeeeee111111','order_id':'orderE','review_decision':'approve','state':'review'}]
        outer=self
        class S:
            REPORT_UPDATE_LOCK=FakeLock()
            def list_reports(_,slug):return outer.reports
            def orders_read(_,slug):return copy.deepcopy(outer.orders)
            def orders_write(_,slug,orders):outer.orders=copy.deepcopy(orders)
        self.srv=S()
    def test_approved_review_recovers(self):
        self.assertEqual(mod.normalize_reviewed_orders(self.srv,'game'),2)
        self.assertEqual([r['status'] for r in self.orders],['done','done','archived','review','waiting'])
    def test_recovery_is_idempotent(self):
        mod.normalize_reviewed_orders(self.srv,'game')
        self.assertEqual(mod.normalize_reviewed_orders(self.srv,'game'),0)
    def test_rejected_is_archived(self):
        self.reports[0]['review_decision']='reject'
        self.assertEqual(mod.normalize_reviewed_orders(self.srv,'game'),2)
        self.assertEqual(self.orders[0]['status'],'archived')
    def test_revision_is_superseded(self):
        self.reports[0]['review_decision']='revise'
        mod.normalize_reviewed_orders(self.srv,'game')
        self.assertEqual(self.orders[0]['status'],'superseded')
    def test_no_decision_leaves_review(self):
        self.reports[0].pop('review_decision')
        mod.normalize_reviewed_orders(self.srv,'game')
        self.assertEqual(self.orders[0]['status'],'review')
    def test_no_fake_code_change(self):
        job={'state':'done','provider':'codex','integrated':True,'integration_note':'Inga nya filer att införa.'}
        self.assertTrue(mod.classify_codex_completion(job))
        self.assertFalse(job['integrated'])
        self.assertEqual(job['completion_kind'],'no_code_changes')
        self.assertEqual(job['state'],'done')
    def test_already_present_not_new_implementation(self):
        job={'state':'done','provider':'codex','integrated':True,'integration_note':'Resultatet finns redan i spelet.'}
        self.assertTrue(mod.classify_codex_completion(job));self.assertFalse(job['integrated'])
    def test_real_integration_unchanged(self):
        job={'state':'done','provider':'codex','integrated':True,'integration_note':'Ändringen infördes direkt i spelet.'}
        self.assertFalse(mod.classify_codex_completion(job));self.assertTrue(job['integrated'])
    def test_failed_unmodified(self):
        job={'state':'failed','provider':'codex','integrated':False}
        self.assertFalse(mod.classify_codex_completion(job))
    def test_no_change_never_claims_bible_sidecar_update(self):
        class Runtime:
            _PW_V0121114=False
            APP_VERSION='old'
            def reconcile_orders_from_reports(self,slug):return 0
            def finalize_worker_job(self,job):return job
            def apply_worker_bible_updates(self,job):raise AssertionError('No Bible write allowed')
        rt=Runtime();mod.install(rt)
        no_diff={'integration_note':'Inga nya filer att införa.'}
        self.assertEqual(rt.apply_worker_bible_updates(no_diff),0)

    def test_studio_revocation_blocks_one_shot_manual_run(self):
        import pw_v01210 as provider
        from unittest.mock import patch
        with patch.object(provider,'studio_access',return_value={'enabled':False}):
            class Fake:pass
            with self.assertRaisesRegex(ValueError,'Studiotillstånd saknas'):
                provider.gemini_run(Fake(),{'approval':'RUN_GEMINI_FREE_TIER'})

    def test_other_provider_unmodified(self):
        job={'state':'done','provider':'gemini','integrated':True,'integration_note':'Inga nya filer att införa.'}
        self.assertFalse(mod.classify_codex_completion(job));self.assertTrue(job['integrated'])

if __name__=='__main__':unittest.main()
