import importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_reports',Path(__file__).with_name('server.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();mod.ROOT=Path(self.temp.name);mod.PROJECTS=mod.ROOT/'projects'
        mod.create_project({'name':'Minesweeper','slug':'minesweeper','idea':'Spel','genre':'Spel','platform':'Webbläsare','priority':'Kvalitet'})
    def tearDown(self):self.temp.cleanup()
    def test_report_persistence_dedupe_read_archive(self):
        job={'id':'a123b456c789','project':'minesweeper','state':'done','finished_at':'2026-10-21T08:00:00Z','exit_code':0,'events':['{"type":"item.completed","item":{"type":"agent_message","text":"Byggde spelet, tester återstår"}}']}
        r=mod.make_report(job);self.assertIn('Byggde',r['summary'])
        self.assertEqual(mod.make_report(job)['id'],r['id'])
        self.assertEqual(len(mod.list_reports('minesweeper')),1)
        mod.update_report('minesweeper',r['id'],'read');self.assertTrue(mod.list_reports('minesweeper')[0]['read'])
        mod.update_report('minesweeper',r['id'],'archive');self.assertTrue(mod.list_reports('minesweeper')[0]['archived'])
    def test_report_ids_and_links_rejected(self):
        with self.assertRaises(ValueError):mod.report_path('minesweeper','../secret')
        folder=mod.report_dir('minesweeper');(folder/'abcdef123456.json').symlink_to(mod.ROOT/'projects/minesweeper/project.json')
        with self.assertRaises(ValueError):mod.update_report('minesweeper','abcdef123456','read')
if __name__=='__main__':unittest.main()
