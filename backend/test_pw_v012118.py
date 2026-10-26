"""No real provider calls: guarantee provenance, complete handoff and no false authority."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
import pw_v012118 as patch

class Handoff(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.rid='abcdef123456';self.jid='123456abcdef';self.slug='demo'
  self.proposal='Silas och Gruvarbetarens sista skift. ' * 180
  (self.root/(self.rid+'.json')).write_text(json.dumps({'project':self.slug,'source':'gemini-api','review_decision':'forward','review_order_id':'order1','summary':self.proposal}),encoding='utf8')
  self.order={'id':'order1','job_id':self.jid,'source_report_id':self.rid,'review_action':'forward'}
  self.srv=SimpleNamespace(LOCK=threading.RLock(),JOBS={self.jid:{'project':self.slug,'order_id':'order1'}},orders_read=lambda slug:[self.order],report_path=lambda slug,rid:self.root/(rid+'.json'),bible_context=lambda slug,n:'Aktuell godkänd Game Bible')
 def tearDown(self):self.tmp.cleanup()
 def test_full_proposal_is_preserved(self):
  s=patch.implementation_context(self.srv,self.slug,self.jid,'Implementera sidouppdraget')
  self.assertIn(self.proposal.strip(),s);self.assertIn('Aktuell godkänd Game Bible',s)
  self.assertIn('Inga filändringar; ingen ny funktion implementerad',s)
 def test_only_authorized_order_is_expanded(self):
  self.order['review_action']='revise'
  self.assertEqual(patch.implementation_context(self.srv,self.slug,self.jid,'Original'),'Original')
 def test_no_cross_project_leak(self):
  self.assertEqual(patch.implementation_context(self.srv,'other',self.jid,'Original'),'Original')
 def test_unknown_report_cannot_authorize(self):
  self.order['source_report_id']='fedcba654321'
  with self.assertRaises(ValueError):patch.implementation_context(self.srv,self.slug,self.jid,'Original')
 def test_nonapproved_report_rejected(self):
  p=self.root/(self.rid+'.json');d=json.loads(p.read_text());d['review_decision']='reject';p.write_text(json.dumps(d))
  with self.assertRaises(ValueError):patch.implementation_context(self.srv,self.slug,self.jid,'Original')
if __name__=='__main__':unittest.main()
