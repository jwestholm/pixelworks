import base64, importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pw_attachment',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class AttachedJobTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'example','name':'Example','idea':'Example','genre':'Spel','platform':'web'})
 def tearDown(self):s.ROOT,s.PROJECTS=self.old
 def test_image_can_be_saved_for_qa(self):
  picture=b'\x89PNG\r\n\x1a\n'+b'valid-placeholder'
  asset=s.asset_upload('example',{'name':'issue.png','station':'qa','comment':'Varför finns ingen grafik?','data':base64.b64encode(picture).decode()})
  self.assertRegex(asset['id'],r'^[a-f0-9]{16}$')
  self.assertEqual((s.library_base('example')/asset['file']).read_bytes(),picture)
  self.assertEqual(s.asset_list('example')[0]['station'],'qa')
 def test_station_separation(self):
  pic=base64.b64encode(b'\x89PNG\r\n\x1a\n'+b'valid-placeholder').decode()
  s.asset_upload('example',{'name':'example.png','station':'qa','data':pic})
  self.assertEqual([x for x in s.asset_list('example') if x['station']=='music'],[])
