import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

sys.path.insert(0,str(Path(__file__).parent))
import pw_global_staff_v25 as globe


class FakeServer:
    def __init__(self,root):
        self.ROOT=Path(root)
        self.PROJECTS=self.ROOT/'projects'
        self.PROJECTS.mkdir()
        self.staff={}
        self.names={}
        self.Handler=type('FakeHandler',(),{
            'do_GET':lambda self:None,'do_POST':lambda self:None})
    def add(self,slug,name,agentid='codex-1',personname='Gunnar',uid=None):
        base=self.PROJECTS/slug/'management'
        base.mkdir(parents=True)
        (self.PROJECTS/slug/'project.json').write_text(json.dumps({'id':slug,'name':name}))
        people=[{'id':agentid,'name':personname,'provider':'codex','role':'Programmerare',
                 'role_type':'programmer','station':'code', **({'studio_id':uid} if uid else {})}]
        (base/'STAFF.json').write_text(json.dumps(people,ensure_ascii=False))
        (base/'SKILL_SETTINGS.json').write_text('{}')
        (base/'STATION_ASSIGNMENTS.json').write_text('{}')
        self.staff[slug]=people
        self.names[slug]=name


def inventory(srv):
    people=[]
    for slug,members in srv.staff.items():
        for p in members:
            uid=p.get('studio_id') or 'pw-'+hashlib.sha256((slug+'\0'+p['id']).encode()).hexdigest()[:20]
            people.append({'studio_id':uid,'agent_id':p['id'],'name':p['name'],
                           'role':p.get('role',''), 'role_type':p.get('role_type',''),
                           'project_id':slug,'project_name':srv.names[slug],'busy':False})
    ids=[p['studio_id'] for p in people]
    return {'projects':[{'id':k,'name':v} for k,v in srv.names.items()],
            'staff':people,'requires_attention':len(set(ids))!=len(ids)}


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.srv=FakeServer(self.temp.name)
        self.srv.add('hackertoolkit','Hackertoolkit')
        self.srv.add('sjutbanan','Sjutbanan')
        self.previous=sys.modules.get('pw_v013')
        sys.modules['pw_v013']=types.SimpleNamespace(inventory=inventory)
    def tearDown(self):
        if self.previous is None:sys.modules.pop('pw_v013',None)
        else:sys.modules['pw_v013']=self.previous
        self.temp.cleanup()
    def approve(self):
        ids=sorted(p['studio_id'] for p in inventory(self.srv)['staff'])
        return {'approval':globe.APPROVAL,'expected_ids':ids}
    def test_preview_does_not_write(self):
        result=globe.preview(self.srv)
        self.assertFalse(result['registered'])
        self.assertEqual(result['current_count'],2)
        self.assertFalse((self.srv.ROOT/'studio-v013').exists())
    def test_names_not_merged(self):
        result=globe.activate(self.srv,self.approve())
        self.assertTrue(result['created'])
        data=globe.read_registry(self.srv)
        self.assertEqual(len(data['people']),2)
        self.assertEqual(len({x['studio_id'] for x in data['people']}),2)
        self.assertEqual({x['name'] for x in data['people']},{'Gunnar'})
    def test_backup_exact_and_no_project_modifications(self):
        originals={p: (self.srv.PROJECTS/p/'management'/'STAFF.json').read_bytes()
                   for p in ('hackertoolkit','sjutbanan')}
        result=globe.activate(self.srv,self.approve())
        backup=self.srv.ROOT/result['backup_ref']
        self.assertTrue(backup.is_dir())
        for slug,original in originals.items():
            src=self.srv.PROJECTS/slug/'management'/'STAFF.json'
            self.assertEqual(src.read_bytes(),original)
            self.assertEqual((backup/slug/'STAFF.json').read_bytes(),original)
        manifest=json.loads((backup/'MANIFEST.json').read_text())
        self.assertEqual(len(manifest['source_files']),6)
    def test_explicit_approval_required(self):
        with self.assertRaises(ValueError):globe.activate(self.srv,{'expected_ids':[]})
        self.assertFalse(globe.registry_file(self.srv).exists())
    def test_stale_roster_fails_closed(self):
        request=self.approve()
        self.srv.add('pussel','Pussel')
        with self.assertRaisesRegex(ValueError,'ändrats'):globe.activate(self.srv,request)
        self.assertFalse(globe.registry_file(self.srv).exists())
    def test_second_activation_is_idempotent(self):
        globe.activate(self.srv,self.approve())
        before=globe.registry_file(self.srv).read_bytes()
        again=globe.activate(self.srv,self.approve())
        self.assertFalse(again['created'])
        self.assertEqual(globe.registry_file(self.srv).read_bytes(),before)
    def test_moved_identity_recognized(self):
        globe.activate(self.srv,self.approve())
        uid=inventory(self.srv)['staff'][0]['studio_id']
        self.srv.staff['hackertoolkit']=[]
        self.srv.staff['sjutbanan'].append({'id':'moved-1','name':'Gunnar','provider':'codex',
                                          'studio_id':uid,'role':'Programmerare'})
        observed=globe.preview(self.srv)
        self.assertEqual(observed['new_count'],0)
        self.assertTrue(observed['changed_assignments'])
        self.assertTrue(globe.read_registry(self.srv)['people'])
    def test_collision_rejected_without_writes(self):
        uid=inventory(self.srv)['staff'][0]['studio_id']
        self.srv.staff['sjutbanan'][0]['studio_id']=uid
        with self.assertRaisesRegex(ValueError,'kolliderar'):globe.activate(self.srv,self.approve())
        self.assertFalse(globe.registry_file(self.srv).exists())


if __name__=='__main__':unittest.main()
