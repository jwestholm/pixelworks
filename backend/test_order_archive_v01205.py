"""Archiving abandoned orders keeps all project files and reports intact."""
import tempfile
import unittest
from pathlib import Path
from backend import server as s

class ArchiveOrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old=(s.ROOT,s.PROJECTS)
        s.ROOT=Path(self.tmp.name)
        s.PROJECTS=s.ROOT/'projects'
        s.create_project({'slug':'sandbox','name':'Sandbox','idea':'Ett spel att testa','genre':'Äventyr'})
        self.old_jobs=s.JOBS.copy()
        s.JOBS.clear()

    def tearDown(self):
        s.JOBS.clear();s.JOBS.update(self.old_jobs)
        s.ROOT,s.PROJECTS=self.old
        self.tmp.cleanup()

    def make(self,status='waiting',job_id=None):
        order=s.order_action('sandbox',{'action':'create','station':'qa','instruction':'Undersök och dokumentera spelbugg i QA'})['item']
        rows=s.orders_read('sandbox');rows[-1]['status']=status;rows[-1]['job_id']=job_id;s.orders_write('sandbox',rows)
        return order['id']

    def test_old_orders_can_be_archived_without_deletion(self):
        work=s.path_for('sandbox')/'work'
        guard=work/'GAME_BIBLE.md'
        guard.write_text('Vår vision ska inte ändras')
        for status in ('waiting','review','failed','claimed','running'):
            with self.subTest(status=status):
                oid=self.make(status,'zz-job-12')
                result=s.order_action('sandbox',{'action':'archive','id':oid})
                entry=next(x for x in result['orders'] if x['id']==oid)
                self.assertEqual(entry['status'],'archived')
                self.assertEqual(entry['archived_from'],status)
                self.assertTrue(entry.get('archived_at'))
                self.assertEqual(guard.read_text(),'Vår vision ska inte ändras')
                with self.assertRaises(ValueError):s.order_action('sandbox',{'action':'archive','id':oid})

    def test_known_running_job_cannot_be_archived(self):
        oid=self.make('running','123abc')
        s.JOBS['123abc']={'id':'123abc','project':'sandbox','order_id':oid,'state':'running'}
        with self.assertRaisesRegex(ValueError,'pågår'):
            s.order_action('sandbox',{'action':'archive','id':oid})
        self.assertEqual(s.orders_read('sandbox')[0]['status'],'running')

    def test_restart_reconcile_does_not_reactivate_archived_order(self):
        oid=self.make('review','feedfeedfeed')
        s.order_action('sandbox',{'action':'archive','id':oid})
        # A report from an old job would previously flip archived -> review/done.
        old=s.list_reports
        s.list_reports=lambda slug:[{'id':'feedfeedfeed','order_id':oid,'state':'done','integrated':True}]
        try:self.assertEqual(s.reconcile_orders_from_reports('sandbox'),0)
        finally:s.list_reports=old
        self.assertEqual(s.orders_read('sandbox')[0]['status'],'archived')

    def test_late_completion_does_not_unarchive_order(self):
        oid=self.make('claimed','beef000')
        s.order_action('sandbox',{'action':'archive','id':oid})
        original=s.make_report
        s.make_report=lambda job:None
        try:
            self.assertTrue(s.finalize_worker_job({'id':'beef000','project':'sandbox','order_id':oid,
                                                    'agent_id':None,'state':'done'}))
        finally:s.make_report=original
        self.assertEqual(s.orders_read('sandbox')[0]['status'],'archived')

    def test_archive_missing_order_and_no_active_job_removal(self):
        with self.assertRaisesRegex(ValueError,'saknas'):
            s.order_action('sandbox',{'action':'archive','id':'unknown'})
        oid=self.make('claimed','oldjob')
        s.JOBS['elsewhere']={'id':'elsewhere','project':'other','order_id':oid,'state':'running'}
        self.assertEqual(s.order_action('sandbox',{'action':'archive','id':oid})['item']['status'],'archived')

if __name__=='__main__':unittest.main()
