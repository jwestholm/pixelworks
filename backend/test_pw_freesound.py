import contextlib
import io
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pw_freesound as fs

class FakeSrv:
    SKILL_STATIONS=('music','voice')
    def __init__(self, root):
        self.ROOT=Path(root)
        self.LOCK=threading.RLock()
        self.JOBS={}
        self.employee={'id':'a1','name':'Boris','station':'music','provider':'codex','work_mode':'specialist'}
        for slug in ('test','another'):
            (self.ROOT/'projects'/slug/'management').mkdir(parents=True)
    def validate_slug(self,slug):
        if slug not in ('test','another'):raise ValueError('bad slug')
        return slug
    def verify_project(self,slug):self.validate_slug(slug)
    def path_for(self,slug):return self.ROOT/'projects'/slug
    def staff_read(self,slug):return [self.employee]

class FreesoundTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.srv=FakeSrv(self.temp.name)
        fs.ACTIVE.clear()
    def tearDown(self):
        fs.ACTIVE.clear();self.temp.cleanup()
    def test_secret_storage_and_project_isolation(self):
        self.assertFalse(fs.status(self.srv)['connected'])
        fs.set_key(self.srv,'ThisIsATestKey1234')
        self.assertEqual(fs.get_key(self.srv),'ThisIsATestKey1234')
        self.assertEqual(fs.key_path(self.srv).stat().st_mode & 0o777,0o600)
        self.assertNotIn('ThisIsATestKey1234',json.dumps(fs.status(self.srv)))
        rec={'id':'a'*16,'project':'test','status':'done','suggestions':[]}
        fs.save(self.srv,'test',rec)
        self.assertEqual(fs.read(self.srv,'test','a'*16)['status'],'done')
        with self.assertRaises(ValueError):fs.read(self.srv,'another','a'*16)
    def test_license_and_preview_validation(self):
        self.assertEqual(fs.license_name('http://creativecommons.org/publicdomain/zero/1.0/'),'CC0')
        self.assertEqual(fs.license_name('http://creativecommons.org/licenses/by/4.0/'),'CC BY')
        self.assertIsNone(fs.license_name('https://creativecommons.org/licenses/by-nc/4.0/'))
        self.assertIsNone(fs.safe_preview('https://evil.com/bad.mp3'))
        self.assertIsNone(fs.safe_preview('http://cdn.freesound.org/a.mp3'))
        self.assertIsNone(fs.safe_preview('https://cdn.freesound.org/a.wav'))
        self.assertEqual(fs.safe_preview('https://cdn.freesound.org/previews/123/abc.mp3'),'https://cdn.freesound.org/previews/123/abc.mp3')
    def test_real_agent_curation_with_fake_provider_and_catalog(self):
        fs.set_key(self.srv,'ThisIsATestKey1234')
        real_reply=fs.real_reply
        search=fs.search_freesound
        employee=fs.employee
        fs.employee=lambda srv,slug,uid:self.srv.employee
        calls=[]
        def fake_reply(srv,slug,agent,prompt):
            calls.append(prompt)
            if len(calls)==1:return json.dumps({'query':'soft puzzle success chime'})
            return json.dumps({'picks':[{'id':1,'reason':'Mjuk klang som passar pusselidén.'},
                                        {'id':2,'reason':'Ett lugnt kort alternativ.'},
                                        {'id':3,'reason':'Lite mer lekfull feedback.'}]})
        fs.real_reply=fake_reply
        fs.search_freesound=lambda token,q:[{'id':i,'name':f'fx{i}','license':'CC0','url':'https://freesound.org/'+str(i),
                                'username':'p','preview':'https://cdn.freesound.org/a.mp3','duration':1.1,
                                'tags':['puzzle'],'description':'nice','license_url':'https://creativecommons.org/publicdomain/zero/1.0/'} for i in (1,2,3)]
        try:
            job=fs.begin(self.srv,{'project':'test','brief':'Mjukt framgångsljud för pusselbitar',
                                    'employee_id':'a1','approval':'START_FREESOUND_AGENT_SEARCH'})['job']
            for _ in range(70):
                item=fs.read(self.srv,'test',job['id'])
                if item['status']!='running':break
                time.sleep(.02)
            self.assertEqual(item['status'],'done',item.get('error'))
            self.assertEqual(len(item['suggestions']),3)
            self.assertEqual(len(calls),2)
            self.assertNotIn('ThisIsATestKey1234',json.dumps(item))
            self.assertFalse(self.srv.JOBS)
        finally:
            fs.employee=employee;fs.real_reply=real_reply;fs.search_freesound=search
    def test_no_approval_no_download(self):
        fs.set_key(self.srv,'ThisIsATestKey1234')
        item={'id':'b'*16,'project':'test','status':'done','suggestions':[{'id':21,'name':'loop','license':'CC0',
                        'license_url':'https://creativecommons.org/publicdomain/zero/1.0/','username':'abc',
                        'url':'https://freesound.org/people/abc/sounds/21/',
                        'preview':'https://cdn.freesound.org/x.mp3'}],'approved':[]}
        fs.save(self.srv,'test',item)
        with self.assertRaises(ValueError): fs.approve(self.srv,{'project':'test','job_id':'b'*16,'sound_id':21})
        self.assertFalse(fs.library_path(self.srv,'test').exists())
    def test_approved_import_is_project_bound_and_idempotent(self):
        original=fs.build_opener
        class FakeResponse:
            status=200
            headers={'Content-Type':'audio/mpeg'}
            def read(self,limit):return b'ID3'+b'\0'*100
            def __enter__(self):return self
            def __exit__(self,*args):pass
        class FakeOpener:
            def open(self,req,timeout=None):
                self_url=req.full_url
                assert self_url=='https://cdn.freesound.org/previews/test.mp3'
                return FakeResponse()
        fs.build_opener=lambda *args: FakeOpener()
        try:
            fs.save(self.srv,'test',{'id':'c'*16,'project':'test','status':'done','approved':[],
                     'suggestions':[{'id':99,'name':'Test Chime','license':'CC BY',
                       'license_url':'http://creativecommons.org/licenses/by/4.0/',
                       'username':'tester','url':'https://freesound.org/people/tester/sounds/99/',
                       'preview':'https://cdn.freesound.org/previews/test.mp3'}]})
            args={'project':'test','job_id':'c'*16,'sound_id':99,'approval':'APPROVE_FREESOUND_PREVIEW'}
            with self.assertRaises(ValueError):fs.approve(self.srv,{**args,'project':'another'})
            result=fs.approve(self.srv,args)
            self.assertTrue(result['imported'])
            self.assertTrue((fs.library_path(self.srv,'test')/result['asset']['filename']).is_file())
            self.assertEqual(result['asset']['license'],'CC BY')
            self.assertFalse(fs.approve(self.srv,args)['imported'])
            self.assertEqual(len(fs.overview(self.srv,'test')['library']),1)
            self.assertEqual(len(fs.overview(self.srv,'another')['library']),0)
        finally:fs.build_opener=original

    def test_route_security(self):
        class Handler:
            def allowed(self):return True
            def auth(self):return False
            def same_origin(self):return True
            def reply(self,status,payload):return status,payload
            def do_GET(self):return ('old-get',{})
            def do_POST(self):return ('old-post',{})
        self.srv.Handler=Handler
        fs.install(self.srv)
        h=Handler();h.path='/api/pw-tools/audio/status'
        self.assertEqual(h.do_GET()[0],403)
        h.path='/api/other';self.assertEqual(h.do_GET()[0],'old-get')

if __name__=='__main__':unittest.main(verbosity=2)
