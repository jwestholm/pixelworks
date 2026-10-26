"""v0.12.11.6 offline tests – approving decisions writes editable Bible, no network."""
import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock
import pw_v012115

class StoryDesignTests(unittest.TestCase):
    def setUp(self):
        temporary=TemporaryDirectory();self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        self.report_file=root/'12aabbcc9988.json'
        self.data={'id':'12aabbcc9988','project':'minesweeper','source':'gemini-api','state':'review',
           'agent_name':'Anders','agent_id':'a1','station':'docs','order_id':'aabbccddeeff',
           'summary':'Mira är en modig robot som samlar tappade minnen och hjälper spelaren att förstå staden.',
           'work_request':'Skapa en ny karaktär med en egen bakgrund','archived':False,'verified':False,'integrated':False}
        self.report_file.write_text(json.dumps(self.data,ensure_ascii=False))
        self.orders=[{'id':'aabbccddeeff','status':'review','job_id':'12aabbcc9988','instruction':'Skapa en karaktär'}]
        self.pages=[{'id':'characters','title':'Karaktärer','content':'# Tidigare beslut'},{'id':'ideas','title':'Idéer','content':''}]
        self.write_page=Mock(side_effect=self.save_page)
        self.move=Mock()
        self.srv=SimpleNamespace(validate_slug=lambda x:x,verify_project=lambda x:True,
             report_path=lambda s,r:self.report_file,orders_read=lambda x:self.orders,
             orders_write=lambda x,items:None,SKILL_STATIONS={'code':'coding','docs':'documentation'},
             REPORT_UPDATE_LOCK=threading.RLock(),BIBLE_UPDATE_LOCK=threading.RLock(),
             book_pages=lambda s:self.pages,save_book_page=self.write_page,
             LOCK=threading.RLock(),JOBS={},move_staff=self.move)
    def save_page(self,slug,payload):
        self.pages[0].update(content=payload['content'])
    def test_approved_design_saved_to_book_not_code(self):
        result=pw_v012115.review_gemini(self.srv,'minesweeper',{'report_id':'12aabbcc9988','action':'approve'})
        self.assertEqual(result['decision'],'approve')
        self.assertIn('Mira',self.pages[0]['content'])
        self.assertIn('Beslutad design',self.pages[0]['content'])
        self.assertIn('Tidigare beslut',self.pages[0]['content'])
        self.assertEqual(json.loads(self.report_file.read_text())['bible_chapter'],'characters')
        self.assertFalse(json.loads(self.report_file.read_text())['integrated'])
        self.move.assert_called_once()
        # Subsequent same decision does not append twice.
        pw_v012115.review_gemini(self.srv,'minesweeper',{'report_id':'12aabbcc9988','action':'approve'})
        self.assertEqual(self.pages[0]['content'].count('[GODKÄND DESIGN'),1)
    def test_template_cannot_be_approved(self):
        self.data['summary']='Roll: [Karaktärsnamn] – [Beskriv här] i projektet.'
        self.report_file.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError,'mallfält'):
            pw_v012115.review_gemini(self.srv,'minesweeper',{'report_id':'12aabbcc9988','action':'approve'})
        self.assertEqual(self.pages[0]['content'],'# Tidigare beslut')
        self.assertEqual(self.orders[0]['status'],'review')
    def test_revise_does_not_write_to_book_or_move(self):
        result=pw_v012115.review_gemini(self.srv,'minesweeper',{'report_id':'12aabbcc9988','action':'revise','feedback':'Ge figuren mer personlighet.'})
        self.assertEqual(result['decision'],'revise')
        self.write_page.assert_not_called()
        self.move.assert_not_called()
if __name__=='__main__':unittest.main()
