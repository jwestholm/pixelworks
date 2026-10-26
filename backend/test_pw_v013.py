"""Studio 0.13 contract tests with a simulated existing v0.12 server."""
import copy
import io
import json
import pathlib
import tempfile
import threading
import types
import unittest
from pw_v013 import activate,inventory,transfer,repair,install,_settings


def person(name, id, provider='codex',station='cafe'):
    return {'name':name,'id':id,'role':'Programmerare','role_type':'programmer',
            'provider':provider,'station':station,'allowed_stations':['code','qa','docs'],
            'skills':{'coding':5},'work_mode':'autonomous'}

class FakeHandler:
    def __init__(self):
        self.path='/';self.code=None;self.output=None
        self.headers={};self.rfile=io.BytesIO();self.wfile=io.BytesIO()
        self.denied=False;self.authorized=True;self.origin=True
    def allowed(self):return not self.denied
    def auth(self):return self.authorized
    def same_origin(self):return self.origin
    def reply(self,code,body):self.code=code;self.output=body;return body
    def do_GET(self):return 'original-get'
    def do_POST(self):return 'original-post'
    def send_response(self,code):self.code=code
    def send_header(self,key,val):pass
    def end_headers(self):pass

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        home=pathlib.Path(self.tmp.name)
        self.p=home/'projects';self.p.mkdir()
        self.groups={'alpha':[person('Gunnar','chief-1')], 'beta':[person('Greta','chief-1','gemini')]}
        for slug in self.groups:self.mk(slug)
        def sf(slug):return self.p/slug/'management'/'STAFF.json'
        def read(slug):return json.loads(sf(slug).read_text(encoding='utf-8'))
        def write(slug,items):sf(slug).write_text(json.dumps(items,ensure_ascii=False),encoding='utf-8')
        def skill(slug):return self.p/slug/'management'/'SKILL_SETTINGS.json'
        self.s=types.SimpleNamespace(ROOT=home,PROJECTS=self.p,JOBS={},LOCK=threading.Lock(),
              staff_file=sf,staff_read=read,staff_write=write,skill_settings_file=skill,
              validate_slug=lambda x: x if x in self.groups else (_ for _ in ()).throw(ValueError('Okänt projekt')),
              path_for=lambda x:self.p/x,Handler=type('Handler',(FakeHandler,),{}),
              APP=home,APP_VERSION='previous',create_project=lambda d:{'verified':True,'starter_team_created':True})
        self.enable={'approval':'ENABLE_SHARED_STUDIO_V013'}
    def mk(self,slug):
        folder=self.p/slug; (folder/'management').mkdir(parents=True)
        (folder/'project.json').write_text(json.dumps({'id':slug,'name':slug.title()}))
        (folder/'management'/'STAFF.json').write_text(json.dumps(self.groups[slug]))
        (folder/'management'/'SKILL_SETTINGS.json').write_text('{}')
        (folder/'studio-bible').mkdir()
        (folder/'studio-bible'/'GAME_BIBLE.md').write_text('# '+slug)
        (folder/'work').mkdir();(folder/'work'/'game.js').write_text(slug)
    def action(self,p,source=None,target='beta'):
        return transfer(self.s,{'approval':'ASSIGN_STUDIO_EMPLOYEE_V013',
            'studio_id':p['studio_id'],'target_project':target})
    def test_inventory_is_read_only_and_separates_same_legacy_ids(self):
        staff=inventory(self.s)
        self.assertEqual(len(staff['staff']),2)
        self.assertNotEqual(staff['staff'][0]['studio_id'],staff['staff'][1]['studio_id'])
        self.assertFalse((self.s.ROOT/'studio-v013').exists())
    def test_enable_is_explicit_and_repeat_safe(self):
        with self.assertRaises(ValueError):activate(self.s,{})
        self.assertFalse(_settings(self.s)['shared'])
        self.assertTrue(activate(self.s,self.enable)['shared'])
        self.assertTrue(activate(self.s,self.enable)['already_enabled'])
        self.assertEqual(len(self.s.staff_read('alpha')),1)
    def test_transfer_collision_is_renamed_preserves_game_and_history(self):
        activate(self.s,self.enable)
        files=[p.read_bytes() for p in [self.p/'alpha'/'studio-bible'/'GAME_BIBLE.md',self.p/'beta'/'work'/'game.js']]
        srcskill=self.s.skill_settings_file('alpha');srcskill.write_text(json.dumps({'chief-1':{'coding':{'level':4,'instruction':'abcde'}}}))
        p=inventory(self.s)['staff'][0];r=self.action(p)
        self.assertTrue(r['moved']);self.assertEqual(len(self.s.staff_read('alpha')),0)
        target=self.s.staff_read('beta');self.assertEqual(len(target),2)
        self.assertNotEqual(target[0]['id'],target[1]['id'])
        moved=next(x for x in target if x.get('studio_id')==p['studio_id'])
        self.assertEqual(moved['station'],'cafe')
        self.assertEqual(moved['skills']['coding'],5)
        self.assertIn(moved['id'],json.loads(self.s.skill_settings_file('beta').read_text()))
        self.assertEqual(files,[q.read_bytes() for q in [self.p/'alpha'/'studio-bible'/'GAME_BIBLE.md',self.p/'beta'/'work'/'game.js']])
        self.assertFalse((self.s.ROOT/'studio-v013'/'TRANSFER_PENDING.json').exists())
        self.assertEqual(self.action(next(x for x in inventory(self.s)['staff'] if x.get('studio_id')==p['studio_id']))['moved'],False)
    def test_busy_person_cannot_transfer(self):
        activate(self.s,self.enable)
        p=inventory(self.s)['staff'][0]
        self.s.JOBS['task']={'project':'alpha','agent_id':'chief-1','state':'running'}
        with self.assertRaisesRegex(ValueError,'arbetar'):self.action(p)
        self.assertEqual(len(self.s.staff_read('alpha')),1)
    def test_no_enable_blocks_move(self):
        p=inventory(self.s)['staff'][0]
        with self.assertRaisesRegex(ValueError,'Aktivera'):self.action(p)
    def test_no_other_project_damage_after_error(self):
        activate(self.s,self.enable)
        p=inventory(self.s)['staff'][0]
        original=copy.deepcopy(self.groups)
        self.s.staff_write('alpha',original['alpha'])
        save=self.s.staff_write
        calls=[]
        def bad(slug,items):
            if slug=='alpha' and len(items)==0 and not calls:
                calls.append('failed');raise OSError('Simulerat diskfel')
            return save(slug,items)
        self.s.staff_write=bad
        with self.assertRaises(OSError):self.action(p)
        self.assertEqual(self.s.staff_read('alpha'),original['alpha'])
        self.assertEqual(self.s.staff_read('beta'),original['beta'])
        self.assertFalse((self.s.ROOT/'studio-v013'/'TRANSFER_PENDING.json').exists())
    def test_interrupted_transfer_requires_explicit_repair(self):
        activate(self.s,self.enable)
        import pw_v013
        root=self.s.ROOT/'studio-v013';root.mkdir(exist_ok=True)
        pw_v013._save(self.s,root/'TRANSFER_PENDING.json',{
            'source':'alpha','target':'beta',
            'source_staff':copy.deepcopy(self.groups['alpha']),'target_staff':copy.deepcopy(self.groups['beta']),
            'target_skill':{}})
        p=inventory(self.s)['staff'][0]
        with self.assertRaisesRegex(ValueError,'tidigare personalbyte'):self.action(p)
        with self.assertRaises(ValueError):repair(self.s,{})
        self.assertTrue(repair(self.s,{'approval':'RESTORE_STUDIO_TRANSFER_V013'})['restored'])
        self.assertFalse((root/'TRANSFER_PENDING.json').exists())
    def test_parallel_jobs_belong_to_distinct_people_and_projects(self):
        self.s.JOBS={
            'a':{'project':'alpha','agent_id':'chief-1','state':'running'},
            'b':{'project':'beta','agent_id':'chief-1','state':'running'}}
        state=inventory(self.s)
        self.assertEqual(sum(p['busy'] for p in state['staff']),2)
        self.assertEqual({p['project_id'] for p in state['staff']},{'alpha','beta'})
        self.assertFalse((self.s.ROOT/'studio-v013').exists())
    def test_no_symlink_staff_may_be_imported_or_transferred(self):
        activate(self.s,self.enable)
        real=self.s.staff_file('beta')
        real.rename(real.with_name('STAFF.saved'))
        real.symlink_to(real.with_name('STAFF.saved'))
        state=inventory(self.s)
        self.assertEqual(state['staff_count'],1)
        with self.assertRaisesRegex(ValueError,'Osäker personalfil'):
            self.action(state['staff'][0])
    def test_starter_seed_skipped_only_in_shared_mode(self):
        import pw_v01210
        old=pw_v01210.seed_project_staff
        pw_v01210.seed_project_staff=lambda server,slug:['starter']
        try:
            self.s.create_project=lambda payload:{'verified':True,'starter_team_created':bool(pw_v01210.seed_project_staff(self.s,'alpha'))}
            install(self.s)
            self.assertTrue(self.s.create_project({})['starter_team_created'])
            activate(self.s,self.enable)
            result=self.s.create_project({})
            self.assertFalse(result['starter_team_created'])
            self.assertTrue(result['shared_studio'])
        finally:pw_v01210.seed_project_staff=old

    def test_install_auth_and_forward_routes(self):
        import sys
        import pw_v01210
        old=pw_v01210.seed_project_staff
        try:
            install(self.s)
            handler=self.s.Handler();handler.path='/api/pw-v013/studio';handler.do_GET()
            self.assertEqual(handler.code,200)
            self.assertEqual(handler.output['staff_count'],2)
            blocked=self.s.Handler();blocked.path='/api/pw-v013/studio';blocked.authorized=False;blocked.do_GET()
            self.assertEqual(blocked.code,403)
            payload=json.dumps({'approval':'ENABLE_SHARED_STUDIO_V013'}).encode()
            h=self.s.Handler();h.path='/api/pw-v013/studio/enable';h.rfile=io.BytesIO(payload);h.headers['Content-Length']=str(len(payload));h.do_POST()
            self.assertTrue(h.output['shared'])
            denial=self.s.Handler();denial.path=h.path;denial.origin=False;denial.rfile=io.BytesIO(payload);denial.headers['Content-Length']=str(len(payload));denial.do_POST()
            self.assertEqual(denial.code,403)
            self.assertEqual(self.s.Handler().do_POST(),'original-post')
            self.assertEqual(self.s.create_project({})['starter_team_created'],False)
        finally:pw_v01210.seed_project_staff=old

if __name__=='__main__':unittest.main()
