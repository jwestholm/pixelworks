"""Provider-mocked v3.3 safety, personality, real-job and review tests. No AI calls."""
import io, json, os, subprocess, sys, tempfile, threading, time, types, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as crew
import pw_v3_jobs as jobs

class Core:
    def __init__(self,root):
        self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={};self._PW33_LIVE={}
        self.PROJECTS=self.ROOT/'projects';self.PROJECTS.mkdir()
        self.call_count=0;self.integrate_calls=0;self.allow_integration=True
    def add_project(self,name='hackertoolkit'):
        p=self.PROJECTS/name;(p/'work').mkdir(parents=True)
        subprocess.run(['git','init','-q',str(p/'work')],check=True)
        (p/'work'/'index.html').write_text('<html><body>OK</body></html>')
        subprocess.run(['git','-C',str(p/'work'),'add','-A'],check=True)
        subprocess.run(['git','-C',str(p/'work'),'-c','user.name=Tester','-c','user.email=test@localhost','commit','-qm','initial'],check=True)
        return p
    def validate_slug(self,s):
        if not isinstance(s,str) or s not in ('hackertoolkit','sjutbanan'):raise ValueError('Ogiltigt projekt')
        return s
    def verify_project(self,s):
        if not (self.PROJECTS/s/'work').is_dir():raise ValueError('Projektet saknas')
    def path_for(self,s):return self.PROJECTS/s
    def bible_context(self,s,maxlen=7000):return 'Skriv ett bra spel med tydlig start.'
    def status(self):return {'execution_enabled':True}
    def isolated_ready(self,s):
        work=self.PROJECTS/s/'work'
        if not work.is_dir():return False,'Projektmapp saknas'
        res=subprocess.run(['git','-C',str(work),'status','--porcelain'],text=True,capture_output=True)
        return (res.returncode==0 and not res.stdout.strip(), 'Smutsig Git-mapp')
    def create_worker_tree(self,s,jid):
        root=self.PROJECTS/s/'management'/'worktrees';root.mkdir(parents=True,exist_ok=True)
        target=root/('job-'+jid);branch='pixelworks/job-'+jid
        subprocess.run(['git','-C',str(self.PROJECTS/s/'work'),'worktree','add','-q','-b',branch,str(target),'HEAD'],check=True)
        return target,branch
    def integrate_worker_result(self,job):
        self.integrate_calls+=1
        if not self.allow_integration:return False,'Konflikt i Git'
        self.call_count+=1
        return True,'Inga konflikter – infört efter godkännande'

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.core=Core(t.name);self.core.add_project()
        crew.activate(self.core,{'approval':crew.APPROVAL})
        result=crew.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'programmer','revision':1})
        self.assertEqual(result['revision'],2)
        self.stub=types.ModuleType('pw_v01210')
        self.stub._gemini_send=lambda key,prompt:('FAKTISKT TEST-DUBBELSVAR: '+prompt[-100:],{'totalTokenCount':12})
        self.stub.gemini_status=lambda srv:{'can_send':True,'model':'gemini-test-model','quota':'okänt'}
        self.stub.studio_access=lambda srv:{'enabled':True}
        self.stub.reserve_gemini_call=lambda srv:'FAKE-NON-SECRET-TESTKEY'
        self.stub.GoogleQuotaError=type('GoogleQuotaError',(Exception,),{})
        self.stub.mark_auto_pause=lambda srv,error:None
        self.m=patch.dict(sys.modules,{'pw_v01210':self.stub});self.m.start();self.addCleanup(self.m.stop)
    def tearDown(self):
        # Avoid deleting TemporaryDirectory while an explicitly started worker persists.
        for _ in range(100):
            if not self.core._PW33_LIVE:break
            time.sleep(.02)
    def start_payload(self,person='pw3-joppe',engine='gemini',project='hackertoolkit',text='Förbättra startsidans formuleringar i vårt hackarspel.'):
        return {'approval':'START_V3_REAL_JOB','person_id':person,'provider':engine,'project':project,'instruction':text}
    def test_no_external_calls_until_approval(self):
        health=jobs.overview(self.core)
        self.assertTrue(health['enabled']);self.assertEqual(health['jobs'],[])
        with self.assertRaisesRegex(ValueError,'godkänna'):
            jobs.begin(self.core,{**self.start_payload(),'approval':'NO'})
        self.assertEqual(jobs.all_jobs(self.core),[])
    def test_invalid_instructions_projects_people_and_provider(self):
        for changes in ({'project':'../other'},{'person_id':'pw3-unhired'},{'provider':'evil'}, {'instruction':'A'*3}, {'instruction':'X'*3001}):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):jobs.begin(self.core,{**self.start_payload(),**changes})
        self.assertFalse(jobs.all_jobs(self.core))
    def test_persona_is_immutable_and_real_prompt_contains_work_policy(self):
        p,c=jobs.character(self.core,'pw3-joppe')
        prompt=jobs.prompt_for(self.core,p,c,'hackertoolkit','Lös sparproblemet med tydliga tester och återrapportering.')
        self.assertIn('Tjaba',prompt)
        self.assertIn('SPELARENS GODKÄNDA UPPDRAG',prompt)
        self.assertIn('Gör inga egna merge-',prompt)
        self.assertIn('FÖRETAGETS ROLL: Programmerare',prompt)
    def test_gemini_real_provider_is_mocked_review_only(self):
        res=jobs.begin(self.core,self.start_payload())
        jid=res['job']['id']
        for i in range(100):
            j=jobs.load(self.core,jid)
            if j['state'] in jobs.TERMINAL:break
            time.sleep(.02)
        self.assertEqual(j['state'],'review',j)
        self.assertEqual(j['provider'],'gemini');self.assertIn('Tjaba',j['prompt'])
        self.assertIn('FAKTISKT TEST-DUBBELSVAR',j['answer'])
        self.assertFalse(j['verified']);self.assertFalse(j['integrated'])
        self.assertEqual(self.core.integrate_calls,0)
        accepted=jobs.decide(self.core,{'job_id':jid,'action':'approve','approval':'PLAYER_V3_REVIEW_DECISION','feedback':''})
        self.assertEqual(accepted['job']['state'],'done');self.assertFalse(accepted['job']['integrated'])
        self.assertEqual(self.core.integrate_calls,0)
    def test_gemini_fail_visible_without_automatic_retry(self):
        calls=[]
        def fail(key,text):calls.append(text);raise ValueError('HTTP 503')
        self.stub._gemini_send=fail
        jid=jobs.begin(self.core,self.start_payload())['job']['id']
        for _ in range(100):
            j=jobs.load(self.core,jid)
            if j['state'] in jobs.TERMINAL:break
            time.sleep(.02)
        self.assertEqual(j['state'],'failed');self.assertEqual(len(calls),1)
        self.assertEqual(j['error'],'HTTP 503')
    def test_gemini_busy_provider_global_capacity(self):
        first=jobs.load(self.core,jobs.begin(self.core,self.start_payload())['job']['id'])
        # Do not race a live asynchronous worker. Create a stable locked job.
        for _ in range(100):
            if first['id'] not in self.core._PW33_LIVE:break
            time.sleep(.02)
        first['state']='running';jobs.store(self.core,first);self.core._PW33_LIVE[first['id']]=True
        res=crew.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'siv','role':'qa','revision':2})
        self.core.add_project('sjutbanan')
        with self.assertRaises(jobs.Conflict):
            jobs.begin(self.core,self.start_payload(person='pw3-siv',project='sjutbanan'))
        self.assertEqual(res['people'][-1]['character_id'],'siv')
        self.core._PW33_LIVE.clear()
    def test_code_unavailable_closed_not_fallback(self):
        with patch.object(jobs.shutil,'which',return_value=None):
            with self.assertRaisesRegex(ValueError,'verifierad'):
                jobs.begin(self.core,self.start_payload(engine='codex'))
    def test_code_refuses_dirty_worktree(self):
        (self.core.PROJECTS/'hackertoolkit'/'work'/'dirty.txt').write_text('dirty')
        with patch.object(jobs.shutil,'which',return_value='/bin/true'):
            with self.assertRaisesRegex(ValueError,'Isolerat'):
                jobs.begin(self.core,self.start_payload(engine='codex'))
    def test_code_requires_explicit_studio_access(self):
        self.stub.studio_access=lambda srv:{'enabled':False}
        with patch.object(jobs.shutil,'which',return_value='/bin/true'):
            with self.assertRaisesRegex(ValueError,'Skrivmandat'):
                jobs.begin(self.core,self.start_payload(engine='codex'))
    def test_codex_real_worktree_fake_cli_review_and_explicit_merge(self):
        # A fake executable, not a fake subprocess module: real Git worktree and
        # real subprocess IO are exercised, but no network or Codex API calls.
        tool=Path(self.core.ROOT)/'fake-codex'
        tool.write_text("#!/usr/bin/env python3\nimport json,pathlib,sys\nassert '--sandbox' in sys.argv and 'workspace-write' in sys.argv\nassert 'Joppe' in sys.argv[-1] and 'Tjaba' in sys.argv[-1]\npathlib.Path('feature.js').write_text('export const x = 1;')\nprint(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'Jag skapade en testfil. Testning ej verifierad.'}}))\n")
        tool.chmod(0o755)
        real_which=jobs.shutil.which
        with patch.object(jobs.shutil,'which',side_effect=lambda arg: str(tool) if arg=='codex' else real_which(arg)):
            job=jobs.begin(self.core,self.start_payload(engine='codex'))['job']
            jid=job['id']
            for _ in range(100):
                j=jobs.load(self.core,jid)
                if j['state'] in jobs.TERMINAL:break
                time.sleep(.02)
        self.assertEqual(j['state'],'review',j)
        self.assertTrue(Path(j['worktree'],'feature.js').is_file())
        self.assertIn('feature.js',jobs.overview(self.core)['jobs'][0]['changed_files'])
        self.assertFalse((self.core.PROJECTS/'hackertoolkit'/'work'/'feature.js').exists())
        self.assertEqual(self.core.integrate_calls,0)
        self.assertFalse(j['integrated']);self.assertFalse(j['verified'])
        self.core.allow_integration=False
        denied=jobs.decide(self.core,{'job_id':jid,'action':'approve','approval':'PLAYER_V3_REVIEW_DECISION','feedback':''})
        self.assertEqual(denied['job']['state'],'review')
        self.core.allow_integration=True
        approved=jobs.decide(self.core,{'job_id':jid,'action':'approve','approval':'PLAYER_V3_REVIEW_DECISION','feedback':''})
        self.assertEqual(approved['job']['state'],'done');self.assertTrue(approved['job']['integrated'])
        self.assertFalse(approved['job']['verified'])
        self.assertEqual(self.core.integrate_calls,2)
    def test_reject_and_later_keep_results(self):
        jid=jobs.begin(self.core,self.start_payload())['job']['id']
        for _ in range(100):
            if jobs.load(self.core,jid)['state']=='review':break
            time.sleep(.02)
        later=jobs.decide(self.core,{'job_id':jid,'action':'later','approval':'PLAYER_V3_REVIEW_DECISION','feedback':''})
        self.assertEqual(later['job']['state'],'review')
        denied=jobs.decide(self.core,{'job_id':jid,'action':'reject','approval':'PLAYER_V3_REVIEW_DECISION','feedback':'Behöver bättre dialog'})
        self.assertEqual(denied['job']['state'],'rejected');self.assertIn('Behöver bättre',jobs.load(self.core,jid)['feedback'])
        with self.assertRaises(jobs.Conflict):jobs.decide(self.core,{'job_id':jid,'action':'approve','approval':'PLAYER_V3_REVIEW_DECISION','feedback':''})
    def test_reviewer_requires_approval_and_feedback_bound(self):
        with self.assertRaises(ValueError):jobs.decide(self.core,{'approval':'none','job_id':'012345abcdef','action':'reject'})
        with self.assertRaises(ValueError):jobs.decide(self.core,{'approval':'PLAYER_V3_REVIEW_DECISION','job_id':'012345abcdef','action':'reject','feedback':'x'*1201})
    def test_restart_read_only_interrupted_and_not_locked(self):
        job={'schema':1,'id':'012345abcdef','state':'running','person_id':'pw3-joppe','project':'hackertoolkit',
             'provider':'gemini','answer':'','verified':False,'integrated':False}
        jobs.store(self.core,job)
        self.assertEqual(jobs.overview(self.core)['jobs'][0]['state'],'interrupted')
        self.assertEqual(jobs.load(self.core,job['id'])['state'],'running')
        self.assertNotIn(job['id'],self.core._PW33_LIVE)
        res=jobs.begin(self.core,self.start_payload());self.assertEqual(res['job']['provider'],'gemini')
    def test_overview_does_not_expose_full_persona_prompt_or_keys(self):
        j={'schema':1,'id':'012345abcdea','state':'review','person_id':'pw3-joppe',
           'project':'hackertoolkit','provider':'gemini','prompt':'TEST SECRET PROMPT',
           'usage_metadata':{'private':'SHOULD NOT EXPOSE'},'worktree':'/private/path',
           'answer':'Resultat','verified':False,'integrated':False}
        jobs.store(self.core,j)
        result=jobs.overview(self.core)['jobs'][0]
        self.assertNotIn('prompt',result)
        self.assertNotIn('usage_metadata',result)
        self.assertNotIn('worktree',result)
    def test_concurrent_job_start_only_one_wins(self):
        import concurrent.futures
        began=threading.Event();release=threading.Event()
        count=[]
        def slow(key,text):
            count.append(1);began.set();release.wait(timeout=3)
            return 'Mocked full response',{}
        self.stub._gemini_send=slow
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures=[executor.submit(jobs.begin,self.core,self.start_payload()) for _ in range(8)]
            self.assertTrue(began.wait(2))
            good=0;bad=0
            for f in futures:
                try:f.result(timeout=3);good+=1
                except jobs.Conflict:bad+=1
            self.assertEqual((good,bad),(1,7))
            release.set()
        self.assertEqual(len(count),1)
    def test_approve_same_job_twice_cannot_double_integrate(self):
        jid=jobs.begin(self.core,self.start_payload())['job']['id']
        for _ in range(100):
            if jobs.load(self.core,jid)['state']=='review':break
            time.sleep(.02)
        req={'job_id':jid,'action':'approve','approval':'PLAYER_V3_REVIEW_DECISION','feedback':''}
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fs=[executor.submit(jobs.decide,self.core,req) for _ in range(2)]
            good=0;bad=0
            for f in fs:
                try:f.result(timeout=2);good+=1
                except jobs.Conflict:bad+=1
        self.assertEqual((good,bad),(1,1))

    def test_dismissed_employee_work_stays_reviewable(self):
        jid=jobs.begin(self.core,self.start_payload())['job']['id']
        for _ in range(100):
            if jobs.load(self.core,jid)['state']=='review':break
            time.sleep(.02)
        state=crew.state(self.core)
        crew.dismiss(self.core,{'person_id':'pw3-joppe','approval':'DISMISS_PERSON_V3','revision':state['revision']})
        approved=jobs.decide(self.core,{'job_id':jid,'action':'approve','approval':'PLAYER_V3_REVIEW_DECISION'})
        self.assertEqual(approved['job']['state'],'done')
        self.assertFalse(approved['job']['integrated'])

    def test_code_does_not_retry_bad_auth_or_auto_start(self):
        crew_state=crew.state(self.core)
        self.assertEqual(crew_state['people'][1]['engine']['can_execute'],False)
        self.assertFalse(jobs.all_jobs(self.core))
        self.assertEqual(self.core.integrate_calls,0)

if __name__=='__main__': unittest.main()
