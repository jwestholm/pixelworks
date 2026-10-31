import hashlib
import json
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pw_global_staff_v25 as v25
import pw_global_workforce_v27 as w

class FakeServer:
    SKILL_DEFAULTS={'coding':('Programmering','Skriv robust och testbar spelkod.')}
    def __init__(self,root):
        self.ROOT=Path(root);self.PROJECTS=self.ROOT/'projects';self.PROJECTS.mkdir()
        self.LOCK=threading.RLock();self.JOBS={}
        self.names={};self.rosters={};self.orders={}
        self.Handler=type('Handler',(),{'do_GET':lambda h:None,'do_POST':lambda h:None})
    def add(self,slug,name,staff):
        self.names[slug]=name;self.rosters[slug]=staff;self.orders[slug]=[]
        mgmt=self.PROJECTS/slug/'management';mgmt.mkdir(parents=True)
        (self.PROJECTS/slug/'project.json').write_text(json.dumps({'id':slug,'name':name}))
        for name,data in [('STAFF.json',staff),('SKILL_SETTINGS.json',{}),('STATION_ASSIGNMENTS.json',{})]:
            (mgmt/name).write_text(json.dumps(data,ensure_ascii=False))
    def staff_read(self,slug):
        if slug not in self.rosters:raise ValueError('Projektet finns inte')
        return json.loads(json.dumps(self.rosters[slug]))
    def staff_write(self,slug,people):
        self.rosters[slug]=people
        (self.PROJECTS/slug/'management'/'STAFF.json').write_text(json.dumps(people))
    def orders_read(self,slug):return self.orders[slug]
    def dismiss_staff(self,slug,payload):raise AssertionError('old dismiss should not be used')
    def get_skill_settings(self,slug):
        return {p['id']:{'coding':{'name':'Programmering',
                                  'level':p.get('skills',{}).get('coding',2),
                                  'instruction':'Skriv robust och testbar spelkod.'}}
                for p in self.staff_read(slug)}
    def save_skill_setting(self,slug,payload):
        raise AssertionError('Old skill file must not be written after activation')

def uid(slug,agent_id):return 'pw-'+hashlib.sha256((slug+'\0'+agent_id).encode()).hexdigest()[:20]
def make_inventory(srv):
    people=[]
    for slug in sorted(srv.names):
        for p in srv.staff_read(slug):
            people.append({'studio_id':p.get('studio_id') or uid(slug,p['id']),
                           'project_id':slug,'project_name':srv.names[slug],'agent_id':p['id'],
                           'name':p['name'],'role':p.get('role',''),'role_type':p.get('role_type',''),
                           'busy':False})
    return {'staff':people,'projects':fake_projects(srv)}
def fake_projects(srv):return [{'id':k,'name':n} for k,n in srv.names.items()]
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.s=FakeServer(self.tmp.name)
        self.s.add('hackertoolkit','Hackertoolkit',[
          {'id':'codex-1','name':'Gunnar','provider':'codex','role':'Programmerare','role_type':'programmer','station':'code','skills':{'coding':4},'allowed_stations':['cafe','code','qa']},
          {'id':'codex-2','name':'Chefen','provider':'codex','role':'Arbetsledare','role_type':'lead','station':'lead','allowed_stations':['cafe','lead']},])
        self.s.add('sjutbanan','Sjutbanan',[
          {'id':'codex-1','name':'Gunnar','provider':'codex','role':'Programmerare','role_type':'programmer','station':'qa','allowed_stations':['cafe','code','qa']}])
        self.s.add('pussel','Pussel',[])
        self.prev=sys.modules.get('pw_v013')
        self.v13=types.SimpleNamespace(inventory=make_inventory,_projects=fake_projects,
            transfer=lambda s,p:{'legacy':True})
        sys.modules['pw_v013']=self.v13
        v25.activate(self.s,{'approval':v25.APPROVAL,'expected_ids':sorted(x['studio_id'] for x in make_inventory(self.s)['staff'])})
        self.original={slug:(self.s.PROJECTS/slug/'management'/'STAFF.json').read_bytes() for slug in self.s.names}
        self.s._raw_read=self.s.staff_read
        w.install(self.s)
    def tearDown(self):
        if self.prev is None:sys.modules.pop('pw_v013',None)
        else:sys.modules['pw_v013']=self.prev
        self.tmp.cleanup()
    @property
    def raw(self):return self.s._raw_read
    def enable(self):
        data=v25.read_registry(self.s)
        return w.activate(self.s,{'approval':w.APPROVAL,'expected_ids':sorted(x['studio_id'] for x in data['people'])},self.raw)
    def test_requires_approval_no_startup_write(self):
        self.assertFalse(w.workforce_file(self.s).exists())
        self.assertFalse(w.preview(self.s)['active'])
        with self.assertRaisesRegex(ValueError,'uttryckliga'):
            w.activate(self.s,{'expected_ids':[]},self.raw)
        self.assertFalse(w.workforce_file(self.s).exists())
    def test_activation_copies_unique_people_and_leaves_legacy_bytes(self):
        self.enable();self.assertEqual(w.preview(self.s)['count'],3)
        for slug,raw in self.original.items():
            self.assertEqual((self.s.PROJECTS/slug/'management'/'STAFF.json').read_bytes(),raw)
        self.assertEqual(len({x['studio_id'] for x in w.preview(self.s)['people']}),3)
    def test_legacy_alias_and_project_scoped_reads(self):
        self.enable()
        self.assertEqual(len(self.s.staff_read('hackertoolkit')),2)
        self.assertEqual(len(self.s.staff_read('sjutbanan')),1)
        self.assertEqual(len(self.s.staff_read('pussel')),0)
        self.assertEqual(self.s.staff_read('sjutbanan')[0]['id'],'codex-1')
    def test_reassignment_keeps_uid_and_original_history(self):
        self.enable();gunnar=uid('hackertoolkit','codex-1')
        got=w.assign(self.s,{'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27','studio_id':gunnar,'target_project':'pussel'},self.raw)
        self.assertEqual(got['project_id'],'pussel')
        self.assertEqual(len(self.s.staff_read('pussel')),1)
        self.assertEqual(self.s.staff_read('pussel')[0]['studio_id'],gunnar)
        self.assertTrue(self.s.staff_read('pussel')[0]['id'].startswith('studio-'))
        self.assertEqual(len(self.s.staff_read('hackertoolkit')),1)
        self.assertEqual(len(self.s.staff_read('sjutbanan')),1)
        w.assign(self.s,{'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27','studio_id':gunnar,'target_project':'hackertoolkit'},self.raw)
        self.assertEqual(self.s.staff_read('hackertoolkit')[0]['id'],'codex-1')
        for slug,raw in self.original.items():
            self.assertEqual((self.s.PROJECTS/slug/'management'/'STAFF.json').read_bytes(),raw)
    def test_two_gunnars_never_merged(self):
        self.enable()
        ids=[p['studio_id'] for p in w.preview(self.s)['people'] if p['name']=='Gunnar']
        self.assertEqual(len(set(ids)),2)
        for i,g in enumerate(ids):w.assign(self.s,{'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27','studio_id':g,'target_project':'pussel'},self.raw)
        self.assertEqual(len(self.s.staff_read('pussel')),2)
        self.assertEqual(len({p['id'] for p in self.s.staff_read('pussel')}),2)
    def test_active_job_and_order_block_move(self):
        self.enable();g=uid('hackertoolkit','codex-1')
        payload={'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27','studio_id':g,'target_project':'pussel'}
        self.s.JOBS['j']={'project':'hackertoolkit','agent_id':'codex-1','state':'running'}
        with self.assertRaisesRegex(ValueError,'pågående'):w.assign(self.s,payload,self.raw)
        self.s.JOBS={};self.s.orders['hackertoolkit']=[{'agent_id':'codex-1','status':'running'}]
        with self.assertRaisesRegex(ValueError,'pågående'):w.assign(self.s,payload,self.raw)
    def test_activation_blocked_with_active_jobs(self):
        self.s.JOBS['j']={'project':'hackertoolkit','agent_id':'codex-1','state':'queued'}
        with self.assertRaisesRegex(ValueError,'pågående'):self.enable()
        self.assertFalse(w.workforce_file(self.s).exists())
    def test_profile_and_station_changes_persist_globally_only(self):
        self.enable();roster=self.s.staff_read('hackertoolkit')
        roster[0]['station']='qa';roster[0]['name']='Gunnar III'
        self.s.staff_write('hackertoolkit',roster)
        self.assertEqual(self.s.staff_read('hackertoolkit')[0]['station'],'qa')
        self.assertEqual(self.s.staff_read('hackertoolkit')[0]['name'],'Gunnar III')
        self.assertEqual((self.s.PROJECTS/'hackertoolkit'/'management'/'STAFF.json').read_bytes(),self.original['hackertoolkit'])
    def test_no_silent_dismiss_through_staff_write(self):
        self.enable();roster=self.s.staff_read('hackertoolkit')
        with self.assertRaisesRegex(ValueError,'Avskedning'):self.s.staff_write('hackertoolkit',roster[:-1])
        self.assertEqual(w.preview(self.s)['count'],3)
    def test_explicit_dismiss_preserves_history(self):
        self.enable();result=self.s.dismiss_staff('hackertoolkit',{'approval':'DISMISS_STAFF','agent_id':'codex-1'})
        self.assertTrue(result['history_preserved']);self.assertEqual(w.preview(self.s)['count'],2)
        self.assertEqual(len(self.s.staff_read('hackertoolkit')),1)
        self.assertEqual((self.s.PROJECTS/'hackertoolkit'/'management'/'STAFF.json').read_bytes(),self.original['hackertoolkit'])
    def test_global_skills_follow_person_across_games(self):
        self.enable();g=uid('hackertoolkit','codex-1')
        self.assertEqual(self.s.get_skill_settings('hackertoolkit')['codex-1']['coding']['level'],4)
        w.assign(self.s,{'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27','studio_id':g,'target_project':'pussel'},self.raw)
        alias=self.s.staff_read('pussel')[0]['id']
        self.assertEqual(self.s.get_skill_settings('pussel')[alias]['coding']['level'],4)
        self.s.save_skill_setting('pussel',{'agent_id':alias,'skill':'coding','level':5,
            'instruction':'Implementera spelets mekanik och dokumentera riktiga tester.'})
        w.assign(self.s,{'approval':'ASSIGN_GLOBAL_EMPLOYEE_V27','studio_id':g,'target_project':'hackertoolkit'},self.raw)
        self.assertEqual(self.s.get_skill_settings('hackertoolkit')['codex-1']['coding']['level'],5)
        self.assertEqual((self.s.PROJECTS/'pussel'/'management'/'SKILL_SETTINGS.json').read_text(),'{}')

    def test_manual_delete_plus_hire_same_count_is_not_allowed(self):
        self.enable();members=self.s.staff_read('hackertoolkit')
        members[0]={'id':'new-11','name':'Replacerare','provider':'codex','station':'cafe'}
        with self.assertRaisesRegex(ValueError,'Avskedning'):
            self.s.staff_write('hackertoolkit',members)
        self.assertEqual(w.preview(self.s)['count'],3)

    def test_old_transfer_route_uses_canonical_assign(self):
        self.enable();g=uid('hackertoolkit','codex-1')
        response=self.v13.transfer(self.s,{'studio_id':g,'target_project':'pussel','approval':'ASSIGN_STUDIO_EMPLOYEE_V013'})
        self.assertTrue(response['moved']);self.assertEqual(self.s.staff_read('pussel')[0]['studio_id'],g)
    def test_hire_creates_canonical_person(self):
        self.enable();members=self.s.staff_read('pussel')
        members.append({'id':'fresh-11','name':'Nya','provider':'codex','role_type':'qa','station':'cafe'})
        self.s.staff_write('pussel',members)
        self.assertEqual(w.preview(self.s)['count'],4)
        self.assertTrue(self.s.staff_read('pussel')[0]['studio_id'].startswith('pw-'))
        self.assertEqual(self.s.rosters['pussel'],[])

if __name__=='__main__':unittest.main()
