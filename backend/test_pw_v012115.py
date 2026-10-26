"""Offline regression tests for reviewing Gemini reports; no network, no AI calls."""
import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import pw_v012115 as feature

class GeminiReviewTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name);self.project=self.root/'projects'/'minesweeper'
        for path in (self.project/'management'/'reports',self.project/'work',self.project/'studio-bible'):
            path.mkdir(parents=True,exist_ok=True)
        self.original={'id':'aabbccddeeff','station':'docs','instruction':'Ta fram snygga instruktioner bredvid spelplanen.','priority':2,
                       'status':'review','job_id':'112233445566','attachment_ids':[]}
        self.orders=[self.original.copy()]
        self.file=self.project/'management'/'reports'/'112233445566.json'
        self.report={'id':'112233445566','project':'minesweeper','source':'gemini-api','state':'review',
            'order_id':'aabbccddeeff','station':'docs','agent_name':'Gemini',
            'summary':'Placera instruktionerna i en separat panel till höger om spelplanen.',
            'verified':False,'integrated':False,'archived':False,'read':False}
        self.file.write_text(json.dumps(self.report,ensure_ascii=False))
        self.srv=SimpleNamespace(validate_slug=lambda x:x if x=='minesweeper' else (_ for _ in ()).throw(ValueError('fel slug')),
            verify_project=lambda slug:True,
            report_path=lambda slug,rid:self.project/'management'/'reports'/(rid+'.json'),
            orders_read=lambda slug:self.orders,
            orders_write=self.save_orders,
            SKILL_STATIONS={'code':'coding','docs':'documentation','research':'research'},
            REPORT_UPDATE_LOCK=threading.RLock())
    def save_orders(self,slug,orders):
        self.orders=json.loads(json.dumps(orders))
    def saved_report(self):return json.loads(self.file.read_text())
    def test_approve_marks_proposal_only_not_code(self):
        with patch('pw_v012115.urlopen',side_effect=AssertionError('No network'),create=True):
            result=feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'approve'})
        self.assertEqual(result['decision'],'approve')
        self.assertEqual(len(self.orders),1)
        self.assertEqual(self.orders[0]['status'],'done')
        self.assertFalse(self.saved_report()['integrated']);self.assertFalse(self.saved_report()['verified'])
        self.assertEqual(self.saved_report()['review_decision'],'approve')
    def test_forward_creates_real_codex_order_and_only_once(self):
        request={'report_id':'112233445566','action':'forward'}
        result=feature.review_gemini(self.srv,'minesweeper',request)
        self.assertEqual(len(self.orders),2)
        forwarded=self.orders[1]
        self.assertEqual(forwarded['station'],'code');self.assertEqual(forwarded['status'],'waiting')
        self.assertIn('REFERENSDATA',forwarded['instruction'])
        self.assertEqual(forwarded['source_report_id'],'112233445566')
        self.assertEqual(result['order_id'],forwarded['id'])
        self.assertFalse(self.saved_report()['integrated'])
        self.assertIn('redan sparat',feature.review_gemini(self.srv,'minesweeper',request)['message'])
        self.assertEqual(len(self.orders),2)
        with self.assertRaises(ValueError):feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'revise','feedback':'Gör om'})
    def test_request_revision_requires_feedback_and_preserves_queue(self):
        with self.assertRaises(ValueError):feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'revise','feedback':'nej'})
        self.assertEqual(len(self.orders),1)
        response=feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'revise','feedback':'Kortare instruktionstext tack.'})
        self.assertEqual(self.orders[0]['status'],'superseded')
        self.assertEqual(self.orders[1]['station'],'docs')
        self.assertEqual(self.orders[1]['status'],'waiting')
        self.assertIn('Kortare',self.orders[1]['instruction'])
        self.assertEqual(self.saved_report()['review_order_id'],response['order_id'])
        self.assertFalse(self.saved_report()['integrated'])
    def test_reject_does_not_modify_code(self):
        result=feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'reject'})
        self.assertEqual(result['decision'],'reject')
        self.assertEqual(self.orders[0]['status'],'archived')
        self.assertEqual(set(self.project.joinpath('work').iterdir()),set())
    def test_non_gemini_report_cannot_be_reviewed(self):
        self.report['source']='codex-cli';self.file.write_text(json.dumps(self.report))
        with self.assertRaisesRegex(ValueError,'Gemini'):
            feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'approve'})
    def test_no_path_traversal_and_no_archive_review(self):
        for rid in ('../etc/passwd','', 'abcdefghi','z'*12):
            with self.assertRaises(ValueError):feature.review_gemini(self.srv,'minesweeper',{'report_id':rid,'action':'approve'})
        self.report['archived']=True;self.file.write_text(json.dumps(self.report))
        with self.assertRaisesRegex(ValueError,'arkiverad'):
            feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'approve'})
    def test_report_update_failure_retry_does_not_duplicate_orders(self):
        # Report write fails once after order creation; follow-up request reuses same queued task.
        import pw_v01210
        first=True
        with patch.object(pw_v01210,'_write_json',side_effect=OSError('fail disk')):
            with self.assertRaises(OSError):feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'forward'})
        self.assertEqual(len(self.orders),2)
        feature.review_gemini(self.srv,'minesweeper',{'report_id':'112233445566','action':'forward'})
        self.assertEqual(len(self.orders),2)
        self.assertEqual(self.saved_report()['review_decision'],'forward')

if __name__=='__main__': unittest.main()
