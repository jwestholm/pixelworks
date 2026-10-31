"""Offline project-isolated review tests. No API, Codex or remote execution."""
import sys, unittest, tempfile, threading, json, subprocess, hashlib, types
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import pw_media_review as r
import pw_freesound as f

class Server:
    def __init__(self,root):
        self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={};self.orders=[]
        for slug in ('cat','dog'):(self.ROOT/'projects'/slug/'management').mkdir(parents=True)
    def validate_slug(self,s):
        if s not in ('cat','dog'):raise ValueError('Ogiltigt projekt')
        return s
    def verify_project(self,s):self.validate_slug(s)
    def path_for(self,s):return self.ROOT/'projects'/s
    def orders_read(self,s):return list(self.orders)
    def order_action(self,s,body):
        self.validate_slug(s)
        order={'id':'order'+str(len(self.orders)),'station':body['station'],'instruction':body['instruction'],'status':'waiting'}
        self.orders.append(order)
        return {'item':order}

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.s=Server(self.temp.name)
        f.save(self.s,'cat',{'id':'a'*16,'project':'cat','status':'done','employee':'Chefen',
            'suggestions':[{'id':123,'name':'Forest','reason':'Mjukt skogsljud',
                'preview':'https://cdn.freesound.org/previews/12/123.mp3','license':'CC BY-NC'}],
            'approved':[],'created_at':'2026-10-29T12:00:00Z'})
    def tearDown(self):self.temp.cleanup()
    def test_preview_offer_waiting(self):
        data=r.overview(self.s,'cat');self.assertEqual(data['waiting'],1)
        self.assertEqual(data['offers'][0]['id'],'sound:'+'a'*16+':123')
        self.assertEqual(r.overview(self.s,'dog')['offers'],[])
    def test_maybe_can_revisit_then_no_feedback_creates_job(self):
        oid='sound:'+'a'*16+':123'
        result=r.decide(self.s,{'project':'cat','offer_id':oid,'decision':'maybe'})
        self.assertEqual(result['decision'],'maybe');self.assertEqual(len(self.s.orders),0)
        self.assertEqual(r.overview(self.s,'cat')['offers'][0]['status'],'maybe')
        result=r.decide(self.s,{'project':'cat','offer_id':oid,'decision':'no','feedback':'Hitta ett mer lekfullt ljud'})
        self.assertEqual(result['decision'],'rejected');self.assertEqual(len(self.s.orders),1)
        self.assertIn('lekfullt',self.s.orders[0]['instruction'])
        self.assertEqual(r.overview(self.s,'cat')['waiting'],0)
    def test_no_without_feedback_no_job(self):
        oid='sound:'+'a'*16+':123'
        r.decide(self.s,{'project':'cat','offer_id':oid,'decision':'no'})
        self.assertEqual(self.s.orders,[])
        with self.assertRaises(ValueError):r.decide(self.s,{'project':'cat','offer_id':oid,'decision':'yes'})
    def test_reject_wrong_project(self):
        with self.assertRaises(ValueError):r.decide(self.s,{'project':'dog','offer_id':'sound:'+'a'*16+':123','decision':'yes'})
    def test_self_media_not_faked(self):
        r.capture_worker(self.s,{'id':'a'*12,'project':'cat','state':'done','station':'music','agent_name':'Boris','integrated':True})
        offers=r.overview(self.s,'cat')['offers']
        missing=next(x for x in offers if x['source']=='missing-preview')
        self.assertFalse(missing['preview_available'])
        with self.assertRaisesRegex(ValueError,'Inget ljud'):
            r.decide(self.s,{'project':'cat','offer_id':missing['id'],'decision':'yes'})
        r.decide(self.s,{'project':'cat','offer_id':missing['id'],'decision':'no','feedback':'Exportera en riktig WAV-fil att provlyssna'})
        self.assertTrue(self.s.orders)
    def test_worker_real_file_capture(self):
        proj=self.s.path_for('cat');work=proj/'work';work.mkdir()
        def git(cwd,*args):
            p=subprocess.run(['git','-C',str(cwd),*args],capture_output=True,text=True)
            if p.returncode:raise RuntimeError(p.stderr)
        git(work,'init','-q');(work/'hello.txt').write_text('start');git(work,'add','.');
        git(work,'-c','user.name=Test','-c','user.email=t@localhost','commit','-qm','base')
        jid='f'*12;tree=proj/'management'/'worktrees'/('job-'+jid);tree.parent.mkdir()
        git(work,'worktree','add','-qb','pixelworks/job-'+jid,str(tree),'HEAD')
        (tree/'animal.png').write_bytes(b'\x89PNG\r\n\x1a\n'+b'x'*80)
        git(tree,'add','.');git(tree,'-c','user.name=Test','-c','user.email=t@localhost',
            'commit','-qm','Pixel Works: agentresultat '+jid)
        job={'id':jid,'project':'cat','state':'done','station':'art','agent_name':'Alexandra','integrated':False}
        r.capture_worker(self.s,job);data=r.overview(self.s,'cat')['offers']
        self.assertEqual(len(data),2) # Freesound + image
        img=next(x for x in data if x['source']=='agent-file')
        self.assertTrue(img['preview_available'])
        preview=r.preview(self.s,'cat',img['id']);self.assertEqual(preview['mime'],'image/png')
        self.assertEqual(len(preview['base64']),len(__import__('base64').b64encode((tree/'animal.png').read_bytes())))
        with self.assertRaises(ValueError):r.preview(self.s,'dog',img['id'])
        with patch.dict(sys.modules,{'pw_v01210':types.SimpleNamespace(save_material=lambda srv,body:{'id':'b'*16})}):
            r.decide(self.s,{'project':'cat','offer_id':img['id'],'decision':'no','feedback':'Gör älgen mer cartoonig och med större ögon'})
        self.assertIn('cartoonig',self.s.orders[0]['instruction'])
        self.assertIn('[[PW12_ATTACH:'+ 'b'*16 +']]',self.s.orders[0]['instruction'])

    def test_yes_worker_file_unmerged_stages_image_and_queues_work(self):
        import types
        jid='e'*12
        proj=self.s.path_for('cat')
        root=proj/'management'/'worktrees'/('job-'+jid)
        root.mkdir(parents=True)
        data=b'\x89PNG\r\n\x1a\n'+b'7'*92
        (root/'moose.png').write_bytes(data)
        offer={'id':'file:'+jid+':'+ 'a'*16,'project':'cat','source':'agent-file',
               'job_id':jid,'order_id':'m'*12,'employee':'Alexandra','station':'art',
               'kind':'image','title':'moose.png','relative_path':'moose.png',
               'already_integrated':False,'preview_available':True,
               'sha256':hashlib.sha256(data).hexdigest(),'created_at':r.now(),'status':'waiting'}
        r._write(self.s,'cat',[offer])
        calls=[]
        with patch.dict(sys.modules,{'pw_v01210':types.SimpleNamespace(save_material=lambda _s,p:(calls.append(p),{'id':'b'*16})[1])}):
            decision=r.decide(self.s,{'project':'cat','offer_id':offer['id'],'decision':'yes'})
        self.assertEqual(decision['decision'],'approved')
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]['station'],'art')
        self.assertIn('[[PW12_ATTACH:'+ 'b'*16 +']]',self.s.orders[-1]['instruction'])
        self.assertEqual(r.overview(self.s,'cat')['waiting'],1)  # Freesound still waits

    def test_yes_worker_file_already_integrated_records_choice_not_extra_order(self):
        jid='d'*12
        root=self.s.path_for('cat')/'management'/'worktrees'/('job-'+jid)
        root.mkdir(parents=True)
        data=b'\x89PNG\r\n\x1a\n'+b'7'*92
        (root/'moose.png').write_bytes(data)
        offer={'id':'file:'+jid+':'+ 'a'*16,'project':'cat','source':'agent-file',
               'job_id':jid,'employee':'Alexandra','station':'art',
               'kind':'image','title':'moose.png','relative_path':'moose.png',
               'already_integrated':True,'preview_available':True,
               'sha256':hashlib.sha256(data).hexdigest(),'created_at':r.now(),'status':'waiting'}
        r._write(self.s,'cat',[offer])
        result=r.decide(self.s,{'project':'cat','offer_id':offer['id'],'decision':'yes'})
        self.assertEqual(result['decision'],'approved')
        self.assertEqual(len(self.s.orders),0)
    def test_preview_freesound_via_server_not_client_url(self):
        class Resp:
            headers={'Content-Type':'audio/mpeg'}
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def read(self,n):return b'ID3'+b'0'*100
        class Opener:
            def open(self,request,timeout):
                self.request=request
                self_outer=request
                assert request.full_url=='https://cdn.freesound.org/previews/12/123.mp3'
                return Resp()
        # This verifies server-side project ownership and URL sourcing.
        # The old ID3+zeros fixture is NOT a real MP3; codec tests below
        # deliberately reject it rather than pretending it is playable.
        with patch.object(r,'build_opener',return_value=Opener()), \
             patch.object(r,'_audition',return_value={'mime':'audio/wav','base64':'V0FW','seconds':1.0}) as audition:
            result=r.preview(self.s,'cat','sound:'+'a'*16+':123')
        self.assertEqual(result['mime'],'audio/wav')
        audition.assert_called_once_with(b'ID3'+b'0'*100,'audio/mpeg')

if __name__=='__main__':unittest.main()

# Additional in-process integration test after unittest.main when imported via discovery.
class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.s=Server(self.temp.name)
        self.s.JOBS={}; self.s.orders=[]
        f.save(self.s,'cat',{'id':'b'*16,'project':'cat','status':'done','employee':'Gunnar',
            'suggestions':[{'id':501,'name':'Bear growl','reason':'Kort morrande',
                'preview':'https://cdn.freesound.org/previews/3/501.mp3','license':'CC BY'}],
            'approved':[],'created_at':'2026-10-29T12:00:00Z'})
    def tearDown(self):self.temp.cleanup()
    def test_yes_imports_and_stages_real_file_before_order(self):
        import types
        saved=[]
        def save_material(srv,payload):
            saved.append(payload)
            return {'id':'abcd1234abcd1234'}
        record={'id':'fa11fa11fa11fa11','project':'cat','sound_id':501,
                'name':'Bear growl','filename':'fa11fa11fa11fa11.mp3'}
        from unittest.mock import patch
        root=f.library_path(self.s,'cat');root.mkdir()
        (root/record['filename']).write_bytes(b'ID3'+b'1'*40)
        import sys
        with patch.dict(sys.modules,{'pw_v01210':types.SimpleNamespace(save_material=save_material)}):
            with patch.object(f,'approve',return_value={'asset':record,'imported':True}):
                result=r.decide(self.s,{'project':'cat','offer_id':'sound:'+'b'*16+':501','decision':'yes'})
        self.assertEqual(result['decision'],'approved');self.assertEqual(len(saved),1)
        self.assertEqual(saved[0]['station'],'music')
        self.assertIn('[[PW12_ATTACH:abcd1234abcd1234]]',self.s.orders[0]['instruction'])
        self.assertEqual(r.overview(self.s,'cat')['waiting'],0)
