import unittest, tempfile, importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('book_under_test',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class BookTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();s.ROOT=Path(self.t.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'boken','name':'Boken','idea':'Spela','genre':'Äventyr','platform':'Webbläsare'})
 def tearDown(self):self.t.cleanup()
 def test_original_preserved(self):
  source=s.path_for('boken')/'studio-bible/GAME_BIBLE.md';before=source.read_bytes()
  pages=s.book_pages('boken');self.assertEqual(pages[0]['id'],'original');self.assertTrue(pages[0]['readonly'])
  s.save_book_page('boken',{'id':'world','title':'Platser','content':'Fotolabbet och kaféet'})
  self.assertEqual(source.read_bytes(),before)
  self.assertIn('Fotolabbet',s.book_pages('boken')[2]['content'])
 def test_invalid_page_blocked(self):
  with self.assertRaises(ValueError):s.save_book_page('boken',{'id':'../work','title':'Fel','content':'hej'})
  with self.assertRaises(ValueError):s.save_book_page('boken',{'id':'world','title':'X','content':'a'*50001})
 def test_symlink_page_blocked(self):
  folder=s.book_dir('boken');(folder/'world.json').symlink_to(s.path_for('boken')/'project.json')
  with self.assertRaises(ValueError):s.save_book_page('boken',{'id':'world','title':'Risk','content':'hej'})
if __name__=='__main__':unittest.main()
