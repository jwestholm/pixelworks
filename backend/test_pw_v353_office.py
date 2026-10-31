"""V3.5.3 office movement: real persisted UI position, no AI and no legacy staff writes."""
import sys,tempfile,threading,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as v3
class Core:
 def __init__(self,root):self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={}
class TestOffice(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.s=Core(self.tmp.name)
  v3.activate(self.s,{'approval':v3.APPROVAL})
  v3.hire(self.s,{'approval':'HIRE_PERSON_V3','revision':1,'candidate_id':'mira','role':'programmer'})
 def test_move_is_global_and_keeps_role_and_persona(self):
  old=v3.state(self.s);self.assertEqual(old['revision'],2)
  before=old['people'][1]
  after=v3.place(self.s,{'person_id':'pw3-mira','x':36.4,'y':64.7,'station_id':'art','revision':2})
  p=after['people'][1]
  self.assertEqual(p['office_position'],{'x':36.4,'y':64.7,'station_id':'art'})
  self.assertEqual(p['role'],'programmer')
  self.assertEqual(p['persona_config']['traits'],before['persona_config']['traits'])
  self.assertEqual(p['worker']['id'],'pw3-mira');self.assertFalse(self.s.JOBS)
  self.assertEqual(v3.state(self.s)['people'][1]['office_position'],p['office_position'])
 def test_invalid_position_never_modifies_registry(self):
  for x,y in [(None,70),(True,68),(math.inf,65),(60,35),(99,60),(-1,72),(20,False)]:
   with self.subTest(x=x,y=y),self.assertRaises(ValueError):
    v3.place(self.s,{'person_id':'pw3-mira','x':x,'y':y,'revision':2})
  self.assertNotIn('office_position',v3.state(self.s)['people'][1])
 def test_conflict_second_client_wont_overwrite(self):
  v3.place(self.s,{'person_id':'pw3-mira','x':36,'y':65,'revision':2})
  with self.assertRaises(v3.Conflict):v3.place(self.s,{'person_id':'pw3-mira','x':77,'y':75,'revision':2})
  self.assertEqual(v3.state(self.s)['people'][1]['office_position']['x'],36)
 def test_unknown_user_and_station_no_mutation(self):
  for pid,st in [('pw3-nope','art'),('pw3-mira','server-room')]:
   with self.subTest(pid=pid,st=st),self.assertRaises(ValueError):
    v3.place(self.s,{'person_id':pid,'x':40,'y':65,'station_id':st,'revision':2})
  self.assertEqual(v3.state(self.s)['revision'],2)
if __name__=='__main__':unittest.main()
