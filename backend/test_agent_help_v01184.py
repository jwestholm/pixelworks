"""Agent help UX backend: temporary project only. No Codex, no network."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from backend import server


class AgentHelpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.slug = 'example-game'
        self.root = Path(self.tmp.name)
        self.project = self.root / self.slug
        (self.project / 'management' / 'reports').mkdir(parents=True)
        (self.project / 'management' / 'worktrees').mkdir(parents=True)
        patcher = patch.object(server, 'PROJECTS', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.agent = 'agent-1'
        self.rid = 'a' * 12
        self.order_id = 'order1'
        self.write_order('failed')
        self.write_report('failed')
        self.staff_patcher=patch.object(server, 'staff_read', return_value=[{'id':self.agent,'name':'QA'}])
        self.staff_patcher.start()
        self.addCleanup(self.staff_patcher.stop)

    def write_order(self,status):
        server.orders_write(self.slug, [{'id':self.order_id,'station':'qa','instruction':'Rätta felen i bildladdningen.',
            'priority':1,'attachment_ids':['reference1'], 'job_id':self.rid,'status':status}])

    def write_report(self,status, **extras):
        entry={'id':self.rid,'agent_id':self.agent,'agent_name':'QA','station':'qa',
               'order_id':self.order_id,'created_at':'2026-10-22T08:10:00+00:00',
               'state':status,'summary':'Kunde inte slutföra QA.',
               'error':'Filen saknas' if status=='failed' else '',
               'integration_note':'Git-konflikt' if status=='review' else '',
               'archived':False,'read':False,'integrated':False}
        entry.update(extras)
        server.report_path(self.slug,self.rid).write_text(json.dumps(entry),encoding='utf-8')

    def test_help_case_contains_actual_reason_and_work(self):
        case=server.list_help_cases(self.slug)[0]
        self.assertEqual(case['reason'],'Filen saknas')
        self.assertEqual(case['instruction'],'Rätta felen i bildladdningen.')
        self.assertEqual(case['agent_name'],'QA')
        self.assertEqual(case['priority'],1)

    def test_approve_failed_creates_new_order_without_starting_ai(self):
        with patch.object(server,'run_codex',side_effect=AssertionError('Must not start')):
            result=server.respond_to_help(self.slug,{'report_id':self.rid,'action':'approve'})
        self.assertEqual(result['status'],'queued')
        orders=server.orders_read(self.slug)
        self.assertEqual(len(orders),2)
        self.assertEqual(orders[0]['status'],'superseded')
        self.assertEqual(orders[1]['priority'],1)
        self.assertEqual(orders[1]['attachment_ids'],['reference1'])
        self.assertEqual(orders[1]['status'],'waiting')
        self.assertEqual(orders[1]['instruction'],'Rätta felen i bildladdningen.')
        self.assertEqual(server.list_help_cases(self.slug),[])
        self.assertEqual(server.reconcile_orders_from_reports(self.slug),0)
        self.assertEqual(server.orders_read(self.slug)[0]['status'],'superseded')

    def test_custom_instructions_and_no_double_send(self):
        server.respond_to_help(self.slug,{'report_id':self.rid,'action':'instruct',
                                         'instruction':'Använd en lokal fallback-bild.'})
        self.assertIn('Spelägarens önskemål',server.orders_read(self.slug)[1]['instruction'])
        self.assertIn('fallback-bild',server.orders_read(self.slug)[1]['instruction'])
        with self.assertRaisesRegex(ValueError,'redan löst|äldre arbetspass'):
            server.respond_to_help(self.slug,{'report_id':self.rid,'action':'instruct',
                                             'instruction':'Försök en gång till.'})
        self.assertEqual(len(server.orders_read(self.slug)),2)

    def test_stale_report_is_not_actionable(self):
        items=server.orders_read(self.slug)
        items[0]['job_id']='b'*12
        server.orders_write(self.slug,items)
        self.assertFalse(server.list_help_cases(self.slug))
        with self.assertRaises(ValueError):
            server.respond_to_help(self.slug,{'report_id':self.rid,'action':'approve'})

    def test_review_conflict_never_marks_as_done(self):
        self.write_report('review')
        self.write_order('review')
        (self.project/'management'/'worktrees'/('job-'+self.rid)).mkdir()
        with patch.object(server,'project_mandate',return_value={'enabled':True}),\
             patch.object(server,'integrate_worker_result',return_value=(False,'Konflikt: samma fil ändrad')):
            result=server.respond_to_help(self.slug,{'report_id':self.rid,'action':'approve'})
        self.assertEqual(result['status'],'blocked')
        self.assertEqual(server.orders_read(self.slug)[0]['status'],'review')
        self.assertFalse(json.loads(server.report_path(self.slug,self.rid).read_text())['archived'])
        self.assertEqual(len(server.list_help_cases(self.slug)),1)

    def test_review_integrates_only_when_safe(self):
        self.write_report('review')
        self.write_order('review')
        (self.project/'management'/'worktrees'/('job-'+self.rid)).mkdir()
        with patch.object(server,'project_mandate',return_value={'enabled':True}),\
             patch.object(server,'integrate_worker_result',return_value=(True,'Infört säkert')) as merger:
            result=server.respond_to_help(self.slug,{'report_id':self.rid,'action':'approve'})
        self.assertEqual(result['status'],'integrated')
        merger.assert_called_once()
        self.assertEqual(server.orders_read(self.slug)[0]['status'],'done')
        report=json.loads(server.report_path(self.slug,self.rid).read_text())
        self.assertTrue(report['integrated'])
        self.assertTrue(report['archived'])
        self.assertEqual(server.list_help_cases(self.slug),[])

    def test_cannot_retry_finished_or_archived(self):
        self.write_report('failed',archived=True)
        self.assertEqual(server.list_help_cases(self.slug),[])
        with self.assertRaises(ValueError):
            server.respond_to_help(self.slug,{'report_id':self.rid,'action':'approve'})


if __name__=='__main__':unittest.main()

class NonTechnicalHelpTests(unittest.TestCase):
    # Share fixtures without running the parent tests twice.
    setUp = AgentHelpTests.setUp
    write_order = AgentHelpTests.write_order
    write_report = AgentHelpTests.write_report
    def test_review_conflict_creates_new_safe_task_without_manual_git(self):
        self.write_report('review')
        self.write_order('review')
        (self.project/'management'/'worktrees'/('job-'+self.rid)).mkdir()
        with patch.object(server,'project_mandate',return_value={'enabled':True}), \
             patch.object(server,'integrate_worker_result',return_value=(False,'Arbetet krockar med andra ändringar.')) as merger, \
             patch.object(server,'run_codex',side_effect=AssertionError('Not authorized to start on dialog')):
            result=server.respond_to_help(self.slug,{'report_id':self.rid,'action':'resolve'})
        self.assertEqual(result['status'],'queued')
        merger.assert_called_once()
        orders=server.orders_read(self.slug)
        self.assertEqual(orders[0]['status'],'superseded')
        self.assertIn('aktuella spelbara versionen',orders[1]['instruction'])
        self.assertEqual(server.list_help_cases(self.slug),[])
        self.assertTrue(json.loads(server.report_path(self.slug,self.rid).read_text())['archived'])

    def test_missing_old_worktree_recreates_order_without_console(self):
        self.write_report('review')
        self.write_order('review')
        with patch.object(server,'project_mandate',return_value={'enabled':True}), \
             patch.object(server,'integrate_worker_result',side_effect=AssertionError('no old tree')):
            result=server.respond_to_help(self.slug,{'report_id':self.rid,'action':'resolve'})
        self.assertEqual(result['status'],'queued')
        self.assertEqual(len(server.orders_read(self.slug)),2)

    def test_blocked_when_writing_is_active(self):
        self.write_report('review')
        self.write_order('review')
        with patch.object(server,'project_mandate',return_value={'enabled':True}), \
             patch.dict(server.JOBS,{'active':{'project':self.slug,'state':'running'}}):
            result=server.respond_to_help(self.slug,{'report_id':self.rid,'action':'resolve'})
        self.assertEqual(result['status'],'blocked')
        self.assertEqual(len(server.orders_read(self.slug)),1)

    def test_help_case_uses_plain_swedish_and_retains_technical_details(self):
        self.write_report('review')
        self.write_order('review')
        case=server.list_help_cases(self.slug)[0]
        self.assertIn('spelet',case['friendly_reason'])
        self.assertNotIn('Git',case['friendly_reason'])
        self.assertIn('Git-konflikt',case['reason'])

    def test_followup_survives_report_write_interruption_without_second_retry(self):
        self.write_report('failed')
        items=server.orders_read(self.slug)
        items.append({'id':'new1','station':'qa','instruction':'Försök igen med bilder.',
                      'status':'waiting','parent_report_id':self.rid})
        server.orders_write(self.slug,items)
        self.assertFalse(server.list_help_cases(self.slug))
