import importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('bible_sync_server',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class BibleAISyncTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=s.ROOT,s.PROJECTS
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'bible-test','name':'Bible Test','idea':'Ett kreativt spel','genre':'Äventyr','platform':'Webbläsare'})
  self.slug='bible-test'
 def tearDown(self):
  s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def test_owner_book_is_context_for_workers(self):
  s.save_book_page(self.slug,{'id':'world','title':'Platser','content':'Torget innehåller ett kafé.'})
  context=s.bible_context(self.slug)
  self.assertIn('Torget innehåller ett kafé',context)
  self.assertIn('Ett kreativt spel',context)
 def test_integrated_job_appends_without_overwriting_owner(self):
  s.save_book_page(self.slug,{'id':'world','title':'Platser','content':'Mina egna regler.'})
  job={'id':'abc123','project':self.slug,'integrated':True,'bible_updates':[{'chapter':'world','title':'Fotolabbet','content':'Ett fotolabb finns nu på den norra gatan.'}]}
  self.assertEqual(s.apply_worker_bible_updates(job),1)
  self.assertEqual(s.apply_worker_bible_updates(job),0)
  content=next(p['content'] for p in s.book_pages(self.slug) if p['id']=='world')
  self.assertIn('Mina egna regler.',content)
  self.assertEqual(content.count('Ett fotolabb finns'),1)
 def test_unintegrated_cannot_update_book(self):
  job={'id':'abc124','project':self.slug,'integrated':False,'bible_updates':[{'chapter':'world','title':'Plats','content':'En ändring som inte är införd.'}]}
  self.assertEqual(s.apply_worker_bible_updates(job),0)
 def test_vision_is_protected(self):
  job={'id':'abc125','project':self.slug,'integrated':True,'bible_updates':[{'chapter':'vision','title':'Skriv om','content':'Kasta bort användarens vision.'}]}
  with self.assertRaisesRegex(ValueError,'Ogiltig'):s.apply_worker_bible_updates(job)
if __name__=='__main__':unittest.main()
