"""Offline regression tests for the 0.12.10 addon – never use Codex or Gemini.
Run: python3 -m unittest backend/test_pw_v01210.py (from project root)
"""
import importlib.util
import base64
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys
import threading
import unittest
from unittest.mock import patch

MODULE = Path(__file__).with_name('pw_v01210.py')
spec=importlib.util.spec_from_file_location('pw_v01210',MODULE)
pw=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

class TestPW01210(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        self.project=root/'projects'/'example';self.project.mkdir(parents=True)
        for n in ('management','studio-bible','work'):(self.project/n).mkdir()
        (self.project/'management'/'worktrees').mkdir()
        self.srv=SimpleNamespace(ROOT=root,APP=root,PROJECTS=root/'projects',
            JOBS={},LOCK=threading.RLock(),SKILL_STATIONS={'code':{},'research':{}},
            ASSET_MAGIC={'.png':lambda x:x.startswith(b'\x89PNG\r\n\x1a\n')},
            validate_slug=lambda s:s if s=='example' else (_ for _ in ()).throw(ValueError('invalid')),
            verify_project=lambda slug:True, path_for=lambda slug:self.project,
            library_base=lambda slug:self.project/'studio-bible',
            asset_list=lambda slug:[],
            staff_read=lambda slug:[{'id':'g1','name':'Gemini 1','provider':'gemini','station':'research'}],
            gemini_key_file=lambda:root/'secrets'/'gemini.key')
    def mark_model_verified_offline(self):
        pw._write_json(pw._cfg_file(self.srv), {'tested_model':pw.MODEL,
                'tested_key_sha256':hashlib.sha256(self.srv.gemini_key_file().read_bytes()).hexdigest(),
                'test_result':'ansluten'})

    def test_install_injects_only_one_addon_script_without_changing_original_file(self):
        import io
        html=self.srv.APP/'index.html'
        html.write_text('<!doctype html><html><body><p>Original</p></body></html>')
        class Handler:
            def allowed(self):return True
            def auth(self):return True
            def same_origin(self):return True
            def reply(self,status,payload):self.last=(status,payload)
            def send_response(self,status):self.status=status
            def send_header(self,k,v):pass
            def end_headers(self):pass
            def do_GET(self):raise AssertionError('old get should not handle HTML')
            def do_POST(self):raise AssertionError('old post should not handle our endpoints')
        self.srv.Handler=Handler
        self.srv.provider_status=lambda:{'codex':{'configured':False},'gemini':{'configured':False}}
        self.srv.run_codex=lambda *args:None
        self.srv.integrate_worker_result=lambda job:(True,'ok')
        self.srv.status=lambda:{'execution_enabled':False}
        pw.install(self.srv)
        pw.install(self.srv)
        handler=Handler()
        handler.path='/index.html';handler.wfile=io.BytesIO();handler.do_GET()
        contents=handler.wfile.getvalue().decode()
        self.assertIn('Original',contents)
        self.assertEqual(contents.count('pw-v01210.js'),1)
        self.assertEqual(contents.count('pw-v01211.js'),1)
        self.assertEqual(html.read_text().count('pw-v01210.js'),0)
        handler.path='/api/pw-v01210/status';handler.do_GET()
        self.assertEqual(handler.last[0],200)
        self.assertEqual(handler.last[1]['version'],pw.VERSION)

    def test_gemini_disabled_by_default(self):
        status=pw.gemini_status(self.srv)
        self.assertFalse(status['can_send'])
        self.assertEqual(status['quota'],'okänt')
    def test_saved_token_alone_makes_gemini_eligible_with_fixed_safe_cap(self):
        self.assertFalse(pw.gemini_status(self.srv)['configured'])
        (self.srv.ROOT/'secrets').mkdir()
        self.srv.gemini_key_file().write_text('test-key')
        status=pw.gemini_status(self.srv)
        self.assertFalse(status['can_send'])  # No genuine model test yet.
        self.mark_model_verified_offline()
        self.assertTrue(pw.gemini_status(self.srv)['can_send'])
        self.assertEqual(status['daily_limit'],12)
        for _ in range(12):pw.reserve_gemini_call(self.srv)
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
        with self.assertRaises(ValueError):pw.reserve_gemini_call(self.srv)

    def test_task_material_separate_from_game_bible(self):
        raw=b'\x89PNG\r\n\x1a\n' + b'images'
        rec=pw.save_material(self.srv,{'project':'example','station':'code','name':'bug.png',
                                        'data':base64.b64encode(raw).decode(),'comment':'Bugg i scenen'})
        self.assertEqual(rec['purpose'],'task')
        self.assertEqual(len(pw.get_materials(self.srv,'example')),1)
        self.assertFalse((self.project/'studio-bible'/'assets.json').exists())
        self.assertEqual(pw.select_materials(self.srv,'example',[rec['id']])[0][1].read_bytes(),raw)
    def test_material_bad_magic_rejected(self):
        with self.assertRaises(ValueError):pw.save_material(self.srv,{'project':'example','station':'code','name':'bug.png',
            'data':base64.b64encode(b'not a png').decode()})
    def test_material_symlink_rejected(self):
        rec=pw.save_material(self.srv,{'project':'example','station':'code','name':'bug.png',
            'data':base64.b64encode(b'\x89PNG\r\n\x1a\nX').decode()})
        f=pw.material_root(self.srv,'example')/rec['file']
        target=f.with_suffix('.old')
        f.rename(target)
        f.symlink_to(target)
        with self.assertRaises(ValueError):pw.select_materials(self.srv,'example',[rec['id']])
    def test_stage_copy_in_correct_isolated_worktree_and_cleanup(self):
        raw=b'\x89PNG\r\n\x1a\nX'
        rec=pw.save_material(self.srv,{'project':'example','station':'code','name':'bug.png',
            'data':base64.b64encode(raw).decode()})
        tree=self.project/'management'/'worktrees'/'job-abc';tree.mkdir()
        job={'id':'abc','worktree':str(tree)}
        self.srv.JOBS['abc']=job
        result=pw.stage_codex_materials(self.srv,'abc','example','Fix UI [[PW12_ATTACH:'+rec['id']+']]')
        self.assertNotIn('[[PW12_ATTACH:',result)
        self.assertIn('view_image',result)
        staged=tree/('.pw-job-materials-abc')/(rec['id']+'.png')
        self.assertEqual(staged.read_bytes(),raw)
        pw.clear_stage(job)
        self.assertFalse(staged.exists())
    def test_two_codex_workers_stage_in_independent_worktrees(self):
        raw=b'\x89PNG\r\n\x1a\nX'
        rec=pw.save_material(self.srv,{'project':'example','station':'code','name':'bug.png',
            'data':base64.b64encode(raw).decode()})
        calls=[]
        class Handler:
            def do_GET(self):pass
            def do_POST(self):pass
        self.srv.Handler=Handler
        self.srv.provider_status=lambda:{'codex':{},'gemini':{}}
        self.srv.run_codex=lambda job_id,slug,content:calls.append((job_id,content))
        self.srv.integrate_worker_result=lambda job:(True,'verified by mock')
        self.srv.status=lambda:{'execution_enabled':False}
        for j in ('abc','def'):
            tree=self.project/'management'/'worktrees'/('job-'+j)
            tree.mkdir()
            self.srv.JOBS[j]={'id':j,'worktree':str(tree)}
        pw.install(self.srv)
        threads=[threading.Thread(target=self.srv.run_codex,args=(j,'example','Inspect [[PW12_ATTACH:'+rec['id']+']]')) for j in ('abc','def')]
        for t in threads:t.start()
        for t in threads:t.join(timeout=2)
        self.assertEqual({j for j,_ in calls},{'abc','def'})
        for j,content in calls:
            self.assertIn('.pw-job-materials-'+j,content)
            self.assertFalse((self.project/'management'/'worktrees'/('job-'+j)/('.pw-job-materials-'+j)).exists())

    def test_legacy_bible_image_path_fixed(self):
        lib=self.project/'studio-bible'
        (lib/'assets').mkdir()
        name='abcdefabcdefabcd.png';rel='assets/'+name
        (lib/rel).write_bytes(b'\x89PNG\r\n\x1a\nold')
        self.srv.asset_list=lambda slug:[{'id':'abcdefabcdefabcd','name':'legacy','file':rel}]
        tree=self.project/'management'/'worktrees'/'job-abc';tree.mkdir()
        job={'id':'abc','worktree':str(tree)};self.srv.JOBS['abc']=job
        text=pw.stage_codex_materials(self.srv,'abc','example','Legacy ../studio-bible/'+rel)
        self.assertNotIn('../studio-bible/'+rel,text)
        self.assertTrue((tree/'.pw-job-materials-abc'/name).is_file())
        pw.clear_stage(job)
    def test_gemini_has_no_remote_call_on_save_or_startup(self):
        with patch.object(pw,'urlopen',side_effect=AssertionError('MUST NOT CONNECT')):
            self.assertFalse(pw.gemini_status(self.srv)['enabled'])
            pw.configure_gemini(self.srv,{'enabled':False,'free_project_confirmed':False,'daily_limit':3})
    def test_gemini_job_requires_explicit_approval(self):
        with self.assertRaises(ValueError):pw.gemini_run(self.srv,{'project':'example','agent_id':'g1','instruction':'Analyze these mechanics carefully'})
    def test_gemini_mock_answer_is_unverified_and_persistent(self):
        (self.srv.ROOT/'secrets').mkdir()
        self.srv.gemini_key_file().write_text('dummykey')
        self.mark_model_verified_offline()
        pw.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        pw.configure_gemini(self.srv,{'enabled':True,'free_project_confirmed':True,'daily_limit':2})
        with patch.object(pw,'_gemini_send',return_value=('I suggest a smaller HUD',{'promptTokenCount':4})):
            result=pw.gemini_run(self.srv,{'project':'example','agent_id':'g1','instruction':'Analyse this game interface carefully','approval':'RUN_GEMINI_FREE_TIER'})
            for thread in threading.enumerate():
                if thread.daemon and thread.name.startswith('Thread-'):thread.join(.05)
        jid=result['job_id']
        self.assertEqual(self.srv.JOBS[jid]['state'],'done')
        self.assertFalse(self.srv.JOBS[jid]['verified'])
        self.assertEqual(self.srv.JOBS[jid]['source'],'provider_reported')
        report=self.project/'management'/'gemini-reports'/(jid+'.json')
        self.assertTrue(report.is_file())
        self.assertNotIn('Analyze this',report.read_text())

    def test_gemini_requires_only_token_not_two_optin_controls(self):
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
        (self.srv.ROOT/'secrets').mkdir()
        self.srv.gemini_key_file().write_text('dummykey')
        status=pw.gemini_status(self.srv)
        self.assertFalse(status['can_send'])
        self.mark_model_verified_offline()
        self.assertTrue(pw.gemini_status(self.srv)['can_send'])
        self.assertEqual(status['auto_projects'],[])
        # Deprecated toggles cannot turn the token on/off.
        pw.configure_gemini(self.srv,{'enabled':False,'free_project_confirmed':False,'daily_limit':1})
        self.assertTrue(pw.gemini_status(self.srv)['can_send'])

    def _auto_setup(self):
        (self.srv.ROOT/'secrets').mkdir(exist_ok=True)
        self.srv.gemini_key_file().write_text('dummykey')
        self.mark_model_verified_offline()
        pw.configure_gemini(self.srv,{'enabled':True,'free_project_confirmed':True,'daily_limit':2})
        pw.auto_config(self.srv,'example',{'enabled':True,'approval':'ALLOW_CHIEF_GEMINI_FREE_TIER'})
        people=[{'id':'chief','name':'Chef','provider':'codex','role_type':'lead','station':'lead'},
                {'id':'g1','name':'Gemini 1','provider':'gemini','role_type':'writer',
                 'station':'cafe','home_station':'docs','allowed_stations':['docs','research']}]
        orders=[{'id':'xyz','status':'waiting','station':'docs','instruction':'Skriv en noggrant motiverad text om spelreglerna','priority':1,'created_at':'2020-01-01'}]
        self.srv.staff_read=lambda slug:people
        self.srv.orders_read=lambda slug:orders
        self.srv.orders_write=lambda slug,new:orders.__setitem__(slice(None),new)
        self.srv.project_mandate=lambda slug:{'enabled':True}
        self.srv.agent_authorized=lambda slug,agent,st:agent['id']=='chief'
        self.srv.dispatch_plan=lambda slug:{'assignments':[]}
        self.srv.move_staff=lambda slug,payload:None
        self.srv.report_path=lambda slug,rid:self.project/'management'/(rid+'.json')
        return orders,people

    def test_chief_can_pick_gemini_from_coffee_for_documentation(self):
        orders,staff=self._auto_setup()
        choice=pw.auto_candidate(self.srv,'example')
        self.assertEqual(choice[1]['id'],'g1')
        orders[0]['station']='code'
        self.assertIsNone(pw.auto_candidate(self.srv,'example'))
        orders[0]['station']='docs'
        staff[0]['station']='cafe'
        self.assertIsNone(pw.auto_candidate(self.srv,'example'))

    def test_auto_gemini_makes_review_report_and_updates_order(self):
        import time
        orders,people=self._auto_setup()
        pw.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        with patch.object(pw,'_gemini_send',return_value=('Beskriv hur spelregler fungerar.',{'totalTokenCount':25})):
            result=pw.start_auto_job(self.srv,'example',orders[0],people[1])
            for _ in range(80):
                if orders[0]['status']=='review' and (self.project/'management'/(result+'.json')).is_file():break
                time.sleep(.01)
        self.assertEqual(orders[0]['status'],'review')
        self.assertEqual(self.srv.JOBS[result]['state'],'review')
        report=json.loads((self.project/'management'/(result+'.json')).read_text())
        self.assertEqual(report['source'],'gemini-api')
        self.assertFalse(report['verified'])
        self.assertFalse(report['integrated'])
        self.assertIn('Beskriv',report['summary'])
        self.assertNotIn('Skriv en noggrant',report['summary'])
        self.assertEqual(pw.gemini_status(self.srv)['used_today'],1)

    def test_429_halts_auto_without_retry_and_is_reported_failed(self):
        import time
        orders,people=self._auto_setup()
        pw.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        with patch.object(pw,'_gemini_send',side_effect=ValueError('Gemini Free Tier svarade 429')) as send:
            jid=pw.start_auto_job(self.srv,'example',orders[0],people[1])
            for _ in range(100):
                if orders[0]['status']=='failed' and (self.project/'management'/(jid+'.json')).is_file():break
                time.sleep(.01)
            self.assertEqual(send.call_count,1)
        self.assertEqual(orders[0]['status'],'failed')
        self.assertFalse(pw.gemini_status(self.srv)['can_send'])
        self.assertEqual(pw.gemini_status(self.srv)['paused_until_day'],pw.google_day())

if __name__=='__main__':unittest.main()
