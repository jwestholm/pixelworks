import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import pw_v012117

RID='aabbcc112233'
class BibleTests(unittest.TestCase):
 def setUp(self):
  self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);(root/'management').mkdir();self.root=root
  self.reportpath=root/(RID+'.json');self.report={'id':RID,'source':'gemini-api','state':'review','project':'abc',
   'summary':'En ny detaljerad figur med egen bakgrund, motivation, konflikter och mekanik, med möjlighet att utvecklas.',
   'work_request':'Skapa en karaktär','agent_id':None,'order_id':None}
  self.reportpath.write_text(json.dumps(self.report))
  self.page={'id':'characters','title':'Karaktärer','content':'# Tidigare karaktär\nDet här finns redan och är beslutat.'}
  self.saved=[]
  self.srv=SimpleNamespace(validate_slug=lambda x:x,report_path=lambda slug,rid:self.reportpath,
   orders_read=lambda slug:[],book_pages=lambda slug:[self.page.copy()],path_for=lambda slug:root,
   save_book_page=lambda slug,p:self.saved.append(p),BIBLE_UPDATE_LOCK=__import__('threading').RLock(),
   REPORT_UPDATE_LOCK=__import__('threading').RLock())
 def test_prepare_preserves_old_and_does_not_change_book(self):
  with patch('pw_v01210.reserve_gemini_call',return_value='FAKE'),patch('pw_v01210._gemini_send',return_value=('## Karaktärer\n'+self.page['content']+'\nNy karaktär får en huvudroll i spelet.',{'totalTokenCount':120})) as mock:
   r=pw_v012117.prepare(self.srv,'abc',RID)
  self.assertEqual(r['stage'],'review');self.assertEqual(r['original'],self.page['content']);self.assertIn('Ny karaktär',r['draft'])
  self.assertEqual(self.saved,[]);self.assertEqual(mock.call_count,1)
 def test_confirm_writes_once_and_creates_backup(self):
  with patch('pw_v01210.reserve_gemini_call',return_value='FAKE'),patch('pw_v01210._gemini_send',return_value=('## Karaktärer\n'+self.page['content']+'\nNy karaktär med egen drivkraft.',{})):
   pw_v012117.prepare(self.srv,'abc',RID)
  self.assertEqual(pw_v012117.confirm(self.srv,'abc',RID)['stage'],'saved')
  self.assertEqual(len(self.saved),1)
  self.assertIn('Ny karaktär',self.saved[0]['content'])
  self.assertTrue(list((self.root/'management'/'bible-history').glob('*.json')))
  with self.assertRaises(ValueError):pw_v012117.confirm(self.srv,'abc',RID)
 def test_changed_page_stops_confirmation(self):
  with patch('pw_v01210.reserve_gemini_call',return_value='FAKE'),patch('pw_v01210._gemini_send',return_value=('## Karaktärer\n'+self.page['content']+'\nNy figur och eget mål.',{})):
   pw_v012117.prepare(self.srv,'abc',RID)
  self.page['content']='En annan ändring har sparats'
  with self.assertRaisesRegex(ValueError,'ändrats'):
   pw_v012117.confirm(self.srv,'abc',RID)
  self.assertEqual(self.saved,[])
 def test_no_empty_template_allowed(self):
  self.report['summary']='Förslag: [Karaktärsnamn] – [Beskriv här]. Skriv ditt eget innehåll och fyll i alla värden.'
  self.reportpath.write_text(json.dumps(self.report))
  with self.assertRaisesRegex(ValueError,'färdigt innehåll'):
   pw_v012117.prepare(self.srv,'abc',RID)

if __name__=='__main__':unittest.main()
