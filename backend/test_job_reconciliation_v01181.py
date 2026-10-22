import importlib.util, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pw_sync',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects';s.JOBS.clear()
        s.create_project({'name':'Test','slug':'testspel','idea':'Spel','genre':'Spel','platform':'Webbläsare','priority':'Kvalitet'})
        self.order=s.order_action('testspel',{'action':'create','station':'code','instruction':'Gör något betydelsefullt','priority':2})['item']
    def tearDown(self):self.tmp.cleanup();s.JOBS.clear()
    def job(self, **kw):
        return dict({'id':'a123b456c789','project':'testspel','state':'failed','order_id':self.order['id'],'agent_id':None,'events':[]},**kw)
    def test_failed_job_has_report_and_failed_order(self):
        self.assertTrue(s.finalize_worker_job(self.job()))
        self.assertEqual(s.orders_read('testspel')[0]['status'],'failed')
        self.assertEqual(len(s.list_reports('testspel')),1)
        self.assertFalse(s.list_reports('testspel')[0]['read'])
    def test_report_failure_keeps_order_from_looking_complete(self):
        with patch.object(s,'make_report',side_effect=OSError('disk full')):
            self.assertFalse(s.finalize_worker_job(self.job(state='done')))
        self.assertEqual(s.orders_read('testspel')[0]['status'],'waiting')
    def test_repeated_completion_does_not_duplicate_report(self):
        job=self.job();self.assertTrue(s.finalize_worker_job(job));self.assertTrue(s.finalize_worker_job(job))
        self.assertEqual(len(s.list_reports('testspel')),1)
    def test_old_job_cannot_override_new_assignment(self):
        items=s.orders_read('testspel');items[0]['status']='running';items[0]['job_id']='b123b456c789';s.orders_write('testspel',items)
        self.assertTrue(s.finalize_worker_job(self.job()))
        self.assertEqual(s.orders_read('testspel')[0]['status'],'running')
if __name__=='__main__':unittest.main()
