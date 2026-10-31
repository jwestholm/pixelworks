"""Request wrapping/auth/crew safety regression for v3.3 (no server socket)."""
import email.message,io,json,sys,tempfile,threading,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as crew
import pw_v3_jobs as jobs

class Core:
 def __init__(self,root):
  self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={}
  self.dispatch_plan=lambda slug:{'assignments':[]}
  self.reconcile_orders_from_reports=lambda *args:[]
  self.recover_completed_reviews=lambda *args:[]
  self.chief_block_report=lambda *args:None
  self.office_scheduler=lambda port,event:None
  self.Handler=type('Handler',(object,),{'do_GET':lambda this:('original',404),
                                       'do_POST':lambda this:('original',404)})
  self.Handler.allowed=lambda this: this.good_auth
  self.Handler.auth=lambda this: this.good_auth
  self.Handler.same_origin=lambda this:this.good_origin
  self.Handler.reply=lambda this,code,data:(code,data)
 def status(self):return {'execution_enabled':False}

class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.core=Core(self.tmp.name)
  self.stub=types.ModuleType('pw_v01210')
  self.stub.auto_candidate=lambda *_:None
  self.stub.gemini_status=lambda srv:{'can_send':False,'model':'gemini-mock','quota':'okänt'}
  self.module=patch.dict(sys.modules,{'pw_v01210':self.stub});self.module.start();self.addCleanup(self.module.stop)
  crew.install(self.core);jobs.install(self.core)
 def request(self,method,path,payload=None,auth=True,origin=True,content_type='application/json'):
  h=self.core.Handler();h.good_auth=auth;h.good_origin=origin;h.path=path
  h.headers=email.message.Message();h.headers['Content-Type']=content_type
  data=json.dumps(payload or {}).encode('utf8');h.headers['Content-Length']=str(len(data));h.rfile=io.BytesIO(data)
  return getattr(h,'do_'+method)()
 def test_read_requires_auth_and_no_mutations(self):
  status,obj=self.request('GET','/api/pw-v3/jobs',auth=False)
  self.assertEqual(status,403)
  self.assertFalse((self.core.ROOT/'studio-v3').exists())
  status,obj=self.request('GET','/api/pw-v3/jobs')
  self.assertEqual(status,200);self.assertEqual(obj['jobs'],[])
  self.assertEqual(obj['rules']['execution'],'manual-per-job')
 def test_wrong_origin_and_no_json_refused(self):
  status,obj=self.request('POST','/api/pw-v3/jobs/start',payload={'approval':'START_V3_REAL_JOB'},origin=False)
  self.assertEqual(status,403)
  status,obj=self.request('POST','/api/pw-v3/jobs/start',payload={'approval':'START_V3_REAL_JOB'},content_type='text/plain')
  self.assertEqual(status,400)
 def test_crew_profile_route_body_roundtrip(self):
  crew.activate(self.core,{'approval':crew.APPROVAL})
  payload={'person_id':'pw3-chef','role':'lead','work_description':'Gör inga anställningar, föreslå personal.','revision':1}
  status,obj=self.request('POST','/api/pw-v3/crew/profile',payload=payload)
  self.assertEqual(status,200,obj)
  self.assertIn('Gör inga anställningar',obj['people'][0]['work_description'])
 def test_busy_worker_cannot_be_dismissed_from_crew_route(self):
  crew.activate(self.core,{'approval':crew.APPROVAL})
  crew.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'mira','role':'artist','revision':1})
  job={'schema':1,'id':'123456abcdef','person_id':'pw3-mira','state':'running','project':'hackertoolkit','provider':'gemini'}
  jobs.store(self.core,job);self.core._PW33_LIVE[job['id']]=True
  status,obj=self.request('POST','/api/pw-v3/crew/dismiss',payload={'person_id':'pw3-mira','approval':'DISMISS_PERSON_V3','revision':2})
  self.assertEqual(status,409)
  self.assertTrue(any(p['person_id']=='pw3-mira' for p in crew.state(self.core)['people']))

if __name__=='__main__':unittest.main()
