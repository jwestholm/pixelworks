import io, json, sys, tempfile, threading, types, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as v3

class FakeHandler:
    path='';headers={};rfile=None
    def __init__(self,path='',data=None,authorized=True):
        self.path=path;self.data=data or {};self._authorized=authorized
        self.headers={'Content-Type':'application/json','Content-Length':str(len(json.dumps(self.data)))}
        self.rfile=io.BytesIO(json.dumps(self.data).encode())
    def allowed(self):return self._authorized
    def auth(self):return self._authorized
    def same_origin(self):return self._authorized
    def reply(self,status,payload):return status,payload
    def do_GET(self):return 404,{'error':'fallback'}
    def do_POST(self):return 404,{'error':'fallback'}
class FakeCore:
    def __init__(self,root):
        self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={};self.Handler=type('TestHandler',(FakeHandler,),{})
        self.dispatch_plan=lambda slug:{'project':slug,'assignments':[{'order_id':'x'}],'next':{'order_id':'x'}}

class Recruitment(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.core=FakeCore(self.tmp.name)
        v3.install(self.core)
    def activate(self):return v3.activate(self.core,{'approval':v3.APPROVAL})
    def test_start_only_after_explicit_approval_and_no_legacy_writes(self):
        legacy=self.core.ROOT/'projects'/'hackertoolkit'/'management'/'STAFF.json'
        legacy.parent.mkdir(parents=True);legacy.write_text('OLD EMPLOYEE BYTES')
        before=v3.state(self.core);self.assertFalse(before['enabled']);self.assertEqual(len(before['candidates']),6)
        self.assertFalse((self.core.ROOT/'studio-v3').exists())
        with self.assertRaises(ValueError):v3.activate(self.core,{})
        new=self.activate();self.assertEqual(len(new['people']),1);self.assertEqual(new['people'][0]['name'],'Chefen')
        self.assertEqual(legacy.read_text(),'OLD EMPLOYEE BYTES')
        self.assertEqual(len(v3.state(self.core)['people']),1)
    def test_old_scheduler_and_job_route_blocked_after_activation(self):
        self.assertTrue(self.core.dispatch_plan('x')['assignments'])
        self.activate();self.assertEqual(self.core.dispatch_plan('x')['assignments'],[])
        self.assertEqual(self.core.Handler('/api/jobs',{}).do_POST()[0],409)
        self.assertEqual(self.core.Handler('/api/projects/hackertoolkit/hire',{}).do_POST()[0],409)
    def test_active_job_prevents_activation(self):
        self.core.JOBS['work']={'state':'running'}
        with self.assertRaises(v3.Conflict):self.activate()
        self.assertFalse(v3.state(self.core)['enabled'])
    def test_six_unique_personas_any_role_and_fixed_traits(self):
        db=self.activate();char={x['id']:x for x in db['candidates']};self.assertEqual(len(char),6)
        hired=v3.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'mira','role':'programmer','revision':1})
        p=hired['people'][-1];self.assertEqual(p['role'],'programmer');self.assertEqual(p['character']['skills']['art'],5)
        self.assertEqual(p['engine']['can_execute'],False)
        original=p['character']['traits'].copy()
        updated=v3.profile(self.core,{'person_id':p['person_id'],'role':'artist','work_description':'Rita pixelgorillor; rapportera tester','revision':2,'immutable_character':{'traits':{'careful':0}}})
        self.assertEqual(updated['people'][-1]['character']['traits'],original)
        self.assertEqual(updated['people'][-1]['role'],'artist')
        self.assertEqual(updated['people'][-1]['worker']['id'],p['person_id'])
        with self.assertRaises(v3.Conflict):v3.profile(self.core,{'person_id':p['person_id'],'role':'qa','work_description':'abc','revision':2})
    def test_player_controls_hire_dismiss_and_rehire(self):
        self.activate()
        with self.assertRaises(ValueError):v3.hire(self.core,{'candidate_id':'joppe','role':'programmer','revision':1})
        a=v3.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'programmer','revision':1})
        with self.assertRaises(v3.Conflict):v3.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'programmer','revision':2})
        with self.assertRaises(ValueError):v3.dismiss(self.core,{'approval':'DISMISS_PERSON_V3','person_id':'pw3-chef','revision':2})
        d=v3.dismiss(self.core,{'approval':'DISMISS_PERSON_V3','person_id':'pw3-joppe','revision':2})
        self.assertEqual(len(d['people']),1)
        b=v3.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'artist','revision':3})
        self.assertEqual(b['people'][-1]['person_id'],'pw3-joppe')
        self.assertEqual(len(v3.read(self.core)['team']),2)
    def test_interviews_are_demo_persistent_and_browser_revision_safe(self):
        self.activate()
        x=v3.interview(self.core,{'candidate_id':'mira','role':'artist','revision':1})
        self.assertEqual(x['interview']['source'],'DEMO');self.assertIn('32×32',x['interview']['text']) if '32×32' in x['interview']['text'] else self.assertIn('gorilla',x['interview']['text'])
        self.assertEqual(v3.state(self.core)['interviews']['mira'],x['interview'])
        with self.assertRaises(v3.Conflict):v3.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'mira','role':'artist','revision':1})
    def test_http_boundaries(self):
        st,g=self.core.Handler('/api/pw-v3/crew').do_GET();self.assertEqual(st,200);self.assertFalse(g['enabled'])
        st,_=self.core.Handler('/api/pw-v3/crew',authorized=False).do_GET();self.assertEqual(st,403)
        st,_=self.core.Handler('/api/pw-v3/crew/activate',{'approval':v3.APPROVAL},authorized=False).do_POST();self.assertEqual(st,403)
        st,r=self.core.Handler('/api/pw-v3/crew/activate',{'approval':v3.APPROVAL}).do_POST();self.assertEqual(st,200);self.assertTrue(r['enabled'])
        st,r=self.core.Handler('/api/pw-v3/crew/hire',{'approval':'HIRE_PERSON_V3','candidate_id':'lova','role':'writer','revision':1}).do_POST()
        self.assertEqual(st,200);self.assertEqual(len(r['people']),2)

if __name__=='__main__':unittest.main()
