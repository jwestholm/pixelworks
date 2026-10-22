import unittest, tempfile, json
from pathlib import Path
from unittest.mock import patch
from backend import server

class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  self.slug='test-game'
  (self.root/self.slug/'management'/'reports').mkdir(parents=True)
  self.patcher=patch.object(server,'PROJECTS',self.root)
  self.patcher.start();self.addCleanup(self.patcher.stop)
 def put(self,orders,reports):
  (self.root/self.slug/'management'/'WORK_ORDERS.json').write_text(json.dumps(orders))
  for r in reports:
   (self.root/self.slug/'management'/'reports'/(r['id']+'.json')).write_text(json.dumps(r))
 def test_recovers_failed_and_done(self):
  self.put([{'id':'a','job_id':'111111111111','status':'claimed'},{'id':'b','job_id':'222222222222','status':'review'}],[{'id':'111111111111','order_id':'a','state':'failed'},{'id':'222222222222','order_id':'b','state':'done','integrated':True}])
  self.assertEqual(server.reconcile_orders_from_reports(self.slug),2)
  self.assertEqual([o['status'] for o in server.orders_read(self.slug)],['failed','done'])
  self.assertEqual(server.reconcile_orders_from_reports(self.slug),0)
 def test_does_not_overwrite_newer_or_unmatched(self):
  self.put([{'id':'a','job_id':'333333333333','status':'claimed'}],[{'id':'222222222222','order_id':'a','state':'done'}])
  self.assertEqual(server.reconcile_orders_from_reports(self.slug),0)
 def test_review_not_mistaken_for_done(self):
  self.put([{'id':'a','job_id':'111111111111','status':'claimed'}],[{'id':'111111111111','order_id':'a','state':'review','integrated':False}])
  self.assertEqual(server.reconcile_orders_from_reports(self.slug),1)
  self.assertEqual(server.orders_read(self.slug)[0]['status'],'review')

if __name__=='__main__':unittest.main()
