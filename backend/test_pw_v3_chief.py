"""V3.4 deterministic recommendation, route/security, and v3.3 handoff tests.
No real AI calls, sockets, or project modifications. Run with PYTHONPATH=backend.
"""
from __future__ import annotations
import email.message,io,json,sys,tempfile,threading,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as crew
import pw_v3_chief as chief
import pw_v3_jobs as jobs

class Core:
 def __init__(self,folder):
  self.ROOT=Path(folder);self.LOCK=threading.RLock();self.JOBS={};self._PW33_LIVE={}
  self.PROJECTS=self.ROOT/'projects';(self.PROJECTS/'hackertoolkit'/'work').mkdir(parents=True)
  self.Handler=type('Handler',(),{'do_POST':lambda h:(404,{'error':'Legacy endpoint'})})
  self.Handler.allowed=lambda h:h.good_auth
  self.Handler.auth=lambda h:h.good_auth
  self.Handler.same_origin=lambda h:h.good_origin
  self.Handler.reply=lambda h,status,data:(status,data)
 def validate_slug(self,slug):
  if slug!='hackertoolkit':raise ValueError('Projektet är ogiltigt')
  return slug
 def verify_project(self,slug):
  if not (self.PROJECTS/slug/'work').is_dir():raise ValueError('Projektet saknas')
 def status(self):return {'execution_enabled':True}
 def isolated_ready(self,slug):return True,'Redo'
 def path_for(self,slug):return self.PROJECTS/slug

class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
  self.srv=Core(self.t.name)
  self.stub=types.ModuleType('pw_v01210')
  self.stub.gemini_status=lambda srv:{'can_send':True,'model':'mock-model','quota':'okänt'}
  self.stub.studio_access=lambda srv:{'enabled':True}
  self.mod=patch.dict(sys.modules,{'pw_v01210':self.stub});self.mod.start();self.addCleanup(self.mod.stop)
  self.w=patch.object(jobs.shutil,'which',return_value='/mock/bin/codex');self.w.start();self.addCleanup(self.w.stop)
  crew.activate(self.srv,{'approval':crew.APPROVAL})
  crew.hire(self.srv,{'approval':'HIRE_PERSON_V3','candidate_id':'mira','role':'artist','revision':1})
  crew.hire(self.srv,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'programmer','revision':2})
  crew.hire(self.srv,{'approval':'HIRE_PERSON_V3','candidate_id':'siv','role':'qa','revision':3})
 def payload(self,**kwargs):return {'project':'hackertoolkit','category':'coding','provider':'codex',
            'instruction':'Fixa sparningen och skriv tydliga tester',**kwargs}
 def test_ranked_specialist_not_chief_and_no_job(self):
  before=crew.read(self.srv)
  result=chief.recommend(self.srv,self.payload())
  self.assertEqual(result['ranked'][0]['person_id'],'pw3-joppe')
  self.assertEqual(result['ranked'][0]['level'],4)
  self.assertEqual(result['available_people'],4)
  self.assertFalse(result['hiring_recommended'])
  self.assertEqual(before,crew.read(self.srv))
  self.assertFalse(jobs.all_jobs(self.srv))
  self.assertFalse(self.srv.JOBS)
 def test_recruitment_advice_when_no_specialist(self):
  r=chief.recommend(self.srv,self.payload(category='music',provider='gemini'))
  self.assertTrue(r['hiring_recommended']);self.assertEqual(r['hiring_role'],'musician')
  self.assertIn('ljudfiler',r['ranked'][0]['limitation']);self.assertIn('fiktiv',r['note'].lower())
 def test_available_worker_before_busy_and_other_provider(self):
  self.srv._PW33_LIVE['aaa111aaa111']=True
  jobs.store(self.srv,{'schema':1,'id':'aaa111aaa111','person_id':'pw3-joppe','state':'running','project':'sjutbanan','provider':'gemini'})
  r=chief.recommend(self.srv,self.payload())
  j=next(p for p in r['ranked'] if p['person_id']=='pw3-joppe')
  self.assertFalse(j['can_start']);self.assertTrue(j['busy']);self.assertNotEqual(r['ranked'][0]['person_id'],'pw3-joppe')
 def test_gemini_quota_blocks_everyone_not_faked_available(self):
  self.stub.gemini_status=lambda srv:{'can_send':False,'model':'mock','quota':'okänt','pause_reason':'HTTP 503'}
  r=chief.recommend(self.srv,self.payload(provider='gemini'))
  self.assertEqual(r['available_people'],0);self.assertFalse(r['engine_available'])
  self.assertTrue(all(not x['can_start'] for x in r['ranked']))
 def test_dirty_git_blocks_codex_without_fixing_git(self):
  self.srv.isolated_ready=lambda slug:(False,'Arbetsytan är smutsig')
  r=chief.recommend(self.srv,self.payload())
  self.assertEqual(r['available_people'],0)
  self.assertIn('smutsig',r['ranked'][0]['blockers'][0])
 def test_no_crew_cannot_offer_fake_workers(self):
  (self.srv.ROOT/'studio-v3'/'CREW.json').unlink()
  with self.assertRaises(ValueError):chief.recommend(self.srv,self.payload())
 def test_invalid_task_category_provider_and_project(self):
  for d in [dict(category='codehack'),dict(provider='model-everything'),dict(project='unknown'),dict(instruction='hej')]:
   with self.subTest(d=d),self.assertRaises(ValueError):chief.recommend(self.srv,self.payload(**d))
 def test_immutable_character_skills_not_user_input(self):
  d=crew.read(self.srv)
  d['team'][1]['skills']={'coding':99}
  crew.write(self.srv,d)
  r=chief.recommend(self.srv,self.payload())
  self.assertEqual(next(p for p in r['ranked'] if p['person_id']=='pw3-mira')['level'],1)
 def test_real_start_is_not_reachable_from_chief_route(self):
  chief.install(self.srv)
  def request(payload,auth=True,origin=True,ct='application/json'):
   handler=self.srv.Handler();handler.path='/api/pw-v3/chief/recommend';handler.good_auth=auth;handler.good_origin=origin
   handler.headers=email.message.Message();handler.headers['Content-Type']=ct
   raw=json.dumps(payload).encode();handler.headers['Content-Length']=str(len(raw));handler.rfile=io.BytesIO(raw)
   return handler.do_POST()
  self.assertEqual(request(self.payload(),auth=False)[0],403)
  self.assertEqual(request(self.payload(),origin=False)[0],403)
  self.assertEqual(request(self.payload(),ct='text/plain')[0],400)
  code,result=request(self.payload());self.assertEqual(code,200)
  self.assertNotIn('approval',result)
  self.assertFalse(self.srv.JOBS)
  self.assertEqual(request({'approval':'START_V3_REAL_JOB'})[0],400)

if __name__=='__main__':unittest.main()
