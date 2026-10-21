import base64,importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw010',Path(__file__).with_name('server.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class AssetTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.old=(s.ROOT,s.PROJECTS);s.ROOT=Path(self.temp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'minesweeper','name':'Minesweeper','idea':'Test game','genre':'Spel','platform':'web'})
 def tearDown(self):s.ROOT,s.PROJECTS=self.old
 def test_upload_edit_delete_and_isolation(self):
  png=b'\x89PNG\r\n\x1a\n'+b'123456'
  r=s.asset_upload('minesweeper',{'kind':'file','name':'shot.png','station':'qa','comment':'Bug','data':base64.b64encode(png).decode()})
  self.assertEqual(len(s.asset_list('minesweeper')),1)
  self.assertTrue((s.path_for('minesweeper')/'studio-bible'/r['file']).is_file())
  s.asset_update('minesweeper',{'id':r['id'],'action':'edit','status':'approved','comment':'Fix it'})
  self.assertEqual(s.asset_list('minesweeper')[0]['status'],'approved')
  s.asset_update('minesweeper',{'id':r['id'],'action':'delete'})
  self.assertEqual(s.asset_list('minesweeper'),[])
  self.assertFalse((s.path_for('minesweeper')/'studio-bible'/r['file']).exists())
 def test_invalid_types_rejected(self):
  with self.assertRaises(ValueError):s.asset_upload('minesweeper',{'name':'oops.py','station':'qa','data':base64.b64encode(b'print(1)').decode()})
  with self.assertRaises(ValueError):s.asset_upload('minesweeper',{'name':'bad.png','station':'qa','data':base64.b64encode(b'bad').decode()})
 def test_mandate(self):
  self.assertFalse(s.project_mandate('minesweeper')['enabled'])
  with self.assertRaises(ValueError):s.set_project_mandate('minesweeper',{'enabled':True})
  s.set_project_mandate('minesweeper',{'enabled':True,'approval':'ALLOW_CODEX_WORKSPACE_WRITE'})
  self.assertTrue(s.project_mandate('minesweeper')['enabled'])
if __name__=='__main__':unittest.main()
