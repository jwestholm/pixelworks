import importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_orders',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class WorkOrderTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(s.ROOT,s.PROJECTS)
  s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
  s.create_project({'slug':'sample','name':'Sample','idea':'A fun game','genre':'Pussel','platform':'Webbläsare'})
 def tearDown(self):s.ROOT,s.PROJECTS=self.old;self.tmp.cleanup()
 def create(self,text='Undersök grafiken i startsidan',station='qa',priority=2):return s.order_action('sample',{'station':station,'instruction':text,'priority':priority})['item']
 def test_persistence_and_priorities(self):
  a=self.create();b=self.create('Granska koden för en krasch',priority=1)
  self.assertEqual(len(s.orders_read('sample')),2)
  self.assertEqual([x['id'] for x in sorted(s.orders_read('sample'),key=lambda x:x['priority'])],[b['id'],a['id']])
  s.order_action('sample',{'action':'priority','id':a['id'],'priority':3})
  self.assertEqual(s.orders_read('sample')[0]['priority'],3)
 def test_edit_restricted_and_delete(self):
  a=self.create()
  s.order_action('sample',{'action':'claim','id':a['id']})
  with self.assertRaises(ValueError):s.order_action('sample',{'action':'delete','id':a['id']})
  b=self.create('Rätta färgerna i paletten')
  s.order_action('sample',{'action':'delete','id':b['id']})
  self.assertEqual(len(s.orders_read('sample')),1)
 def test_bad_input_fails_closed(self):
  for payload in [{'station':'INVALID','instruction':'En korrekt text'},{'station':'qa','instruction':'kort'},{'station':'qa','instruction':'En tillräckligt lång text','priority':5},{'station':'qa','instruction':'En tillräckligt lång text','attachment_ids':['not-real']}]:
   with self.subTest(payload=payload):
    with self.assertRaises(ValueError):s.order_action('sample',payload)
  self.assertFalse(s.orders_file('sample').exists())
 def test_project_local_file(self):
  self.create()
  self.assertTrue((s.path_for('sample')/'management'/'WORK_ORDERS.json').exists())
  self.assertFalse((s.path_for('sample')/'work'/'WORK_ORDERS.json').exists())
if __name__=='__main__':unittest.main()
