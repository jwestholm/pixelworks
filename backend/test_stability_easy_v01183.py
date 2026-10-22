"""Regressions for the targeted 0.11.8.3 stability fixes; no real AI services."""
import io
import json
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from backend import server


class StabilityFixes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.slug = 'test-game'
        self.project = self.root / self.slug
        (self.project / 'management' / 'reports').mkdir(parents=True)
        (self.project / 'management' / 'worktrees').mkdir(parents=True)
        self.patch_project = patch.object(server, 'PROJECTS', self.root)
        self.patch_project.start()
        self.addCleanup(self.patch_project.stop)

    def write_order(self, item):
        (self.project / 'management' / 'WORK_ORDERS.json').write_text(json.dumps([item]))

    def put_report(self, entry):
        path = server.report_path(self.slug, entry['id'])
        path.write_text(json.dumps(entry))
        return path

    def test_stale_review_does_not_integrate_or_complete_new_job(self):
        old = 'a' * 12
        newer = 'b' * 12
        (self.project / 'management' / 'worktrees' / ('job-' + old)).mkdir()
        self.write_order({'id': 'one', 'job_id': newer, 'status': 'running'})
        self.put_report({'id': old, 'order_id': 'one', 'source': 'codex-cli',
                         'state': 'review', 'read': False, 'archived': False})
        with patch.object(server, 'project_mandate', return_value={'enabled': True}), \
                patch.object(server, 'integrate_worker_result', return_value=(True, 'merged')) as merge:
            self.assertEqual(server.recover_completed_reviews(self.slug), [])
            merge.assert_not_called()
        self.assertEqual(server.orders_read(self.slug)[0]['status'], 'running')

    def test_current_review_can_be_integrated(self):
        old = 'c' * 12
        (self.project / 'management' / 'worktrees' / ('job-' + old)).mkdir()
        self.write_order({'id': 'one', 'job_id': old, 'status': 'review'})
        self.put_report({'id': old, 'order_id': 'one', 'source': 'codex-cli',
                         'state': 'review', 'read': False, 'archived': False})
        with patch.object(server, 'project_mandate', return_value={'enabled': True}), \
                patch.object(server, 'integrate_worker_result', return_value=(True, 'merged')):
            result = server.recover_completed_reviews(self.slug)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0][1])
        self.assertEqual(server.orders_read(self.slug)[0]['status'], 'done')

    def test_parallel_report_updates_preserve_read_and_archive(self):
        rid = 'd' * 12
        self.put_report({'id': rid, 'state': 'review', 'archived': False, 'read': False})
        start = threading.Event()
        failures = []
        def update(action):
            start.wait()
            try:
                server.update_report(self.slug, rid, action)
            except Exception as error:
                failures.append(error)
        threads = [threading.Thread(target=update, args=(action,))
                   for action in ('read', 'archive')]
        for thread in threads:
            thread.start()
        start.set()
        for thread in threads:
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
        self.assertFalse(failures)
        updated = json.loads(server.report_path(self.slug, rid).read_text())
        self.assertTrue(updated['read'])
        self.assertTrue(updated['archived'])

    def test_isolated_queued_job_is_not_mistaken_for_direct_writer(self):
        work = self.project / 'work'
        work.mkdir()
        def git(*args):
            res = subprocess.run(['git', '-C', str(work), *args],
                                 capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
        git('init', '-q')
        (work / 'README.md').write_text('game')
        git('add', 'README.md')
        git('-c', 'user.name=Test', '-c', 'user.email=test@localhost',
            'commit', '-q', '-m', 'base')
        with patch.dict(server.JOBS, {'a' * 12: {
                'id': 'a' * 12, 'project': self.slug, 'state': 'queued',
                'isolated': True, 'worktree': None}}, clear=True):
            self.assertTrue(server.prepare_parallel_git(self.slug)['ready'])
        with patch.dict(server.JOBS, {'b' * 12: {
                'id': 'b' * 12, 'project': self.slug, 'state': 'queued',
                'isolated': False, 'worktree': None}}, clear=True):
            with self.assertRaisesRegex(ValueError, 'direktjobb'):
                server.prepare_parallel_git(self.slug)

    def test_long_codex_stream_keeps_recent_events_and_final_agent_message(self):
        jid = 'e' * 12
        tree = self.project / 'management' / 'worktrees' / ('job-' + jid)
        tree.mkdir()
        entries = [json.dumps({'type':'item.completed','item':{
            'type':'command_execution','command':f'check-{i}'}}) for i in range(300)]
        entries.append(json.dumps({'type':'item.completed', 'item':{
            'type':'agent_message','text':'Slutrapport efter 300 händelser: färdig.'}}))
        class FakeProcess:
            def __init__(self):
                self.stdout = io.StringIO('\n'.join(entries) + '\n')
                self.returncode = 0
                self.pid = 11111
            def poll(self):
                return 0
        job = {'id':jid, 'project':self.slug, 'state':'queued','worktree':str(tree),
               'events':[], 'order_id':None, 'agent_name':'Testare'}
        with patch.dict(server.JOBS, {jid:job}, clear=True), \
                patch('shutil.which', return_value='/fake/codex'), \
                patch('subprocess.Popen',return_value=FakeProcess()), \
                patch.object(server,'integrate_worker_result',return_value=(True,'infört')), \
                patch.object(server,'staff_read',return_value=[]), \
                patch.object(server,'staff_write'):
            server.run_codex(jid, self.slug, 'Testa detta')
        self.assertEqual(job['event_seq'], 301)
        self.assertEqual(len(job['events']), 60)
        self.assertIn('check-299', '\n'.join(job['events']))
        self.assertEqual(job['state'],'done')
        report = json.loads(server.report_path(self.slug,jid).read_text())
        self.assertIn('Slutrapport efter 300 händelser', report['summary'])


if __name__ == '__main__':
    unittest.main()
