"""Real persisted report test: successful Codex completion must reach the owner's inbox.
No AI network calls, no user projects are touched.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('pw_completion_mail', Path(__file__).with_name('server.py'))
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class CompletionMailTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        server.ROOT = Path(self.temp.name)
        server.PROJECTS = server.ROOT / 'projects'
        server.JOBS.clear()
        server.create_project({'name':'Demo','slug':'demo','idea':'A game',
                               'genre':'Spel','platform':'Webbläsare','priority':'Kvalitet'})

    def tearDown(self):
        self.temp.cleanup()

    def test_integrated_work_is_unread_and_not_archived_until_owner_acts(self):
        job={'id':'a123b456c789','project':'demo','state':'done', 'integrated':True,
             'agent_name':'Programmerarn','events':[], 'last_agent_message':'Spaden är införd.'}
        self.assertTrue(server.finalize_worker_job(job))
        saved=server.list_reports('demo')[0]
        self.assertEqual(saved['title'],'Programmerarn – klart och infört i spelet')
        self.assertFalse(saved['read'])
        self.assertFalse(saved['archived'])
        self.assertEqual(len([r for r in server.list_reports('demo') if not r['read'] and not r['archived']]),1)
        server.update_report('demo',job['id'],'read')
        self.assertEqual(len([r for r in server.list_reports('demo') if not r['read'] and not r['archived']]),0)
        self.assertFalse(server.list_reports('demo')[0]['archived'])
        server.update_report('demo',job['id'],'archive')
        self.assertTrue(server.list_reports('demo')[0]['archived'])
        self.assertTrue(server.finalize_worker_job(job))
        self.assertTrue(server.list_reports('demo')[0]['archived'],'repeated finalization must not revive archived reports')

    def test_nonintegrated_review_remains_unread(self):
        report=server.make_report({'id':'b123b456c789','project':'demo','state':'review',
                                   'integrated':False,'agent_name':'QA','events':[]})
        self.assertFalse(report['read'])
        self.assertFalse(report['archived'])

    def test_recovery_integration_creates_unread_completion_note(self):
        report={'id':'c123b456c789','project':'demo','source':'codex-cli','state':'review',
                'archived':False,'read':True,'summary':'Done','agent_name':'Programmerarn'}
        tree=server.path_for('demo')/'management'/'worktrees'/('job-'+report['id'])
        tree.mkdir(parents=True)
        server.report_path('demo',report['id']).write_text(json.dumps(report), encoding='utf-8')
        with patch.object(server,'project_mandate',return_value={'enabled':True}), \
             patch.object(server,'integrate_worker_result',return_value=(True,'Infört utan konflikt')):
            result=server.recover_completed_reviews('demo')
        self.assertEqual(len(result),1)
        new=server.list_reports('demo')[0]
        self.assertTrue(new['integrated'])
        self.assertEqual(new['state'],'done')
        self.assertFalse(new['archived'])
        self.assertFalse(new['read'],'integration completion is a fresh user-visible event')
        with patch.object(server,'project_mandate',return_value={'enabled':True}), \
             patch.object(server,'integrate_worker_result') as integrate:
            self.assertEqual(server.recover_completed_reviews('demo'),[])
            integrate.assert_not_called()
        self.assertEqual(len(server.list_reports('demo')),1)

if __name__=='__main__': unittest.main()
