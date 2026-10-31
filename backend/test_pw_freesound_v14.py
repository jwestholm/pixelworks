"""Offline regression tests for Freesound unfiltered private-use results and fallback.

No external network or AI calls. Covers the 2026-10-29 screen recording bug.
"""
import json
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
import pw_freesound as f

KEY='privateFreesoundKey123456789'

def snd(sid,license='Creative Commons 0',preview='https://cdn.freesound.org/previews/1/1-hq.mp3', low=None):
    return {'id':sid,'name':'Rabbit squeak '+str(sid),'username':'rabbitman',
            'license':license,'previews':{'preview-hq-mp3':preview,'preview-lq-mp3':low},
            'duration':1.5,'tags':['rabbit','squeak'],'description':'Small rabbit squeak'}

class Resp:
    status=200
    def __init__(self,payload):self.payload=payload
    def read(self,_):return json.dumps(self.payload).encode()
    def __enter__(self):return self
    def __exit__(self,*args):return False

class TestSchema(unittest.TestCase):
    def test_current_freesound_text_licenses(self):
        self.assertEqual(f.license_name('Creative Commons 0'),'CC0')
        self.assertEqual(f.license_name('Attribution'),'CC BY')
        self.assertEqual(f.license_name('Attribution NonCommercial'),'CC BY-NC')
        self.assertEqual(f.license_name('Attribution NonCommercial NoDerivatives'),'CC BY-NC-ND')
        self.assertEqual(f.license_name('https://creativecommons.org/licenses/by/4.0/'),'CC BY')
        self.assertEqual(f.license_name('http://creativecommons.org/publicdomain/zero/1.0/'),'CC0')
        self.assertEqual(f.license_name('https://creativecommons.org/licenses/by-nc/4.0/'),'CC BY-NC')
        self.assertNotEqual(f.license_name('https://creativecommons.org.evil.com/licenses/by/4.0/'),'CC BY')
        self.assertEqual(f.license_name('Some personal use license'), 'Some personal use license')
        self.assertEqual(f.license_name(None), 'Ej angiven')
    def test_sound_schema_previews_and_license(self):
        good=f.normalize(snd(7))
        self.assertEqual(good['license'],'CC0')
        self.assertEqual(good['id'],7)
        self.assertEqual(good['license_url'],'')
        nc = f.normalize(snd(8,'Attribution NonCommercial'))
        self.assertEqual(nc['license'],'CC BY-NC')
        fallback=f.normalize(snd(9,'Attribution',preview=None, low='https://cdn.freesound.org/previews/9/9-lq.mp3'))
        self.assertEqual(fallback['license'],'CC BY')
        self.assertTrue(fallback['preview'].endswith('lq.mp3'))
        self.assertIsNone(f.normalize(snd(10,preview='https://evil.com/x.mp3')))
        self.assertIsNone(f.normalize(snd(11,preview='http://cdn.freesound.org/11.mp3')))
    def test_api_search_keeps_all_licenses_and_counts(self):
        class Opener:
            def open(self,req,timeout):
                self_outer=self
                p=urlparse(req.full_url)
                assert p.path=='/apiv2/search/'
                assert 'license' in parse_qs(p.query)['fields'][0]
                assert 'previews' in parse_qs(p.query)['fields'][0]
                assert req.get_header('Authorization')=='Token '+KEY
                return Resp({'count':3,'results':[snd(3),snd(4,'Attribution'),snd(5,'Attribution NonCommercial')]})
        with patch.object(f,'build_opener',return_value=Opener()):
            result=f.search_freesound(KEY,'rabbit squeak')
        self.assertEqual([x['id'] for x in result],[3,4,5])
        self.assertEqual([x['license'] for x in result],['CC0','CC BY','CC BY-NC'])
        self.assertNotIn('license_rejected', f.SEARCH_AUDIT.last)
        self.assertEqual(f.SEARCH_AUDIT.last['raw_count'],3)
        self.assertEqual(f.SEARCH_AUDIT.last['result_count'],3)
    def test_bounded_query_fallbacks(self):
        self.assertEqual(f.fallback_queries('hare rabbit animal sound'),['hare','rabbit'])
        self.assertEqual(f.fallback_queries('cat'),[])
        self.assertEqual(f.fallback_queries('gentle soft animal sound'),[])

# In-memory fake server: no existing test-file dependency, no real jobs.
import threading
from pathlib import Path
import pw_tool_registry as registry
class Fake:
    def __init__(self, root):
        self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={};self.orders={};self.calls=[]
        for slug in ('alpha','beta'):(self.ROOT/'projects'/slug/'management').mkdir(parents=True)
        class Handler:
            def do_GET(self):return 'old-get'
            def do_POST(self):return 'old-post'
        self.Handler=Handler
    def validate_slug(self,slug):
        if slug not in ('alpha','beta'):raise ValueError('Ogiltigt projekt')
        return slug
    def verify_project(self,slug):self.validate_slug(slug)
    def path_for(self,slug):return self.ROOT/'projects'/slug
    def staff_read(self,slug):return [{'id':'agent1','name':'Chefen','station':'music','provider':'codex','work_mode':'specialist'}]
    def orders_read(self,slug):return [dict(o) for o in self.orders.get(slug,[])]
    def orders_write(self,slug,orders):self.orders[slug]=[dict(o) for o in orders]
    def run_codex(self,jid,slug,instruction):
        self.calls.append((jid,slug,instruction))
        return {'passed':True}
    def approved(self,slug='alpha',id='c'*12):
        self.JOBS[id]={'id':id,'project':slug,'station':'music','agent_id':'agent1','state':'queued','order_id':'ord1'}
        self.orders[slug]=[{'id':'ord1','job_id':id,'station':'music','status':'running','instruction':'Hitta mjukt kattljud till pusselspelet'}]
        return id

class TestWorker(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.s=Fake(self.tmp.name);f.ACTIVE.clear()
        f.set_key(self.s,KEY)
        with patch.object(f,'search_freesound',return_value=[]):f.test_connection(self.s)
        registry.install(self.s)
        self.original=f.real_reply
    def tearDown(self):
        f.real_reply=self.original;f.ACTIVE.clear();self.tmp.cleanup()
    def test_api_current_license_passes_full_agent_flow(self):
        self.s.approved();prompts=[]
        def reply(_srv,_slug,_agent,prompt):
            prompts.append(prompt)
            if len(prompts)==1:return json.dumps({'tool':'freesound','query':'rabbit squeak animal sound'})
            return json.dumps({'picks':[{'id':10,'reason':'Ett kort kaninljud för spelaren'}]})
        f.real_reply=reply
        calls=[]
        class Opener:
            def open(self,req,timeout):
                query=parse_qs(urlparse(req.full_url).query)['query'][0]
                calls.append(query)
                return Resp({'count':1,'results':[snd(10)]})
        with patch.object(f,'build_opener',return_value=Opener()):
            f.install(self.s)
            self.s.run_codex('c'*12,'alpha','Skapa kaninljud')
        self.assertEqual(calls,['rabbit squeak animal sound'])
        j=f.overview(self.s,'alpha')['jobs'][0]
        self.assertEqual(j['status'],'done');self.assertEqual(j['suggestions'][0]['id'],10)
        self.assertNotIn(KEY,self.s.calls[0][2]);self.assertIn('Rabbit squeak',self.s.calls[0][2])
        self.assertEqual([x['kind'] for x in j['tool_events']],['discovery','decision','request','response','curation'])
        self.assertEqual(j['tool_events'][3]['raw_count'],1)
    def test_empty_specific_search_then_broad_search_succeeds(self):
        self.s.approved()
        n=[0]
        def reply(_srv,_slug,_agent,prompt):
            n[0]+=1
            return json.dumps({'tool':'freesound','query':'hare rabbit animal sound'}) if n[0]==1 else json.dumps({'picks':[{'id':11,'reason':'En kanin passar här i spelet'}]})
        f.real_reply=reply
        calls=[]
        class Opener:
            def open(self,req,timeout):
                q=parse_qs(urlparse(req.full_url).query)['query'][0]
                calls.append(q)
                if q=='hare rabbit animal sound':return Resp({'count':0,'results':[]})
                return Resp({'count':1,'results':[snd(11)]})
        with patch.object(f,'build_opener',return_value=Opener()):
            f.install(self.s)
            self.s.run_codex('c'*12,'alpha','Hitta kaninljud')
        self.assertEqual(calls,['hare rabbit animal sound','hare'])
        row=f.overview(self.s,'alpha')['jobs'][0]
        self.assertEqual(row['status'],'done');self.assertEqual(row['query'],'hare')
        self.assertEqual(len(row['suggestions']),1)
    def test_no_matched_audio_has_meaningful_error_and_job_continues(self):
        self.s.approved()
        f.real_reply=lambda *_:json.dumps({'tool':'freesound','query':'hare rabbit animal sound'})
        calls=[]
        class Opener:
            def open(self,req,timeout):
                q=parse_qs(urlparse(req.full_url).query)['query'][0]
                calls.append(q)
                return Resp({'count':1,'results':[snd(14,license='Attribution NonCommercial', preview='https://unsafe.example/audio.mp3')]})
        with patch.object(f,'build_opener',return_value=Opener()):
            f.install(self.s)
            self.s.run_codex('c'*12,'alpha','Testa ljud')
        self.assertEqual(len(calls),3)
        row=f.overview(self.s,'alpha')['jobs'][0]
        self.assertEqual(row['status'],'failed');self.assertIn('förhandsprov',row['error'])
        self.assertEqual(len(self.s.calls),1)
        self.assertNotIn(KEY,self.s.calls[0][2]);self.assertIn('förhandsprov',self.s.calls[0][2])
    def test_noncommercial_sound_passes_real_worker_and_can_be_imported(self):
        self.s.approved()
        prompts=[]
        def reply(_srv,_slug,_agent,prompt):
            prompts.append(prompt)
            if len(prompts)==1:
                return json.dumps({'tool':'freesound','query':'rabbit ambience'})
            return json.dumps({'picks':[{'id':41,'reason':'Vänligt kaninljud som passar spelvärlden'}]})
        f.real_reply=reply
        class AudioResp:
            status=200
            headers={'Content-Type':'audio/mpeg'}
            def read(self,_):return b'ID3' + bytes(100)
            def __enter__(self):return self
            def __exit__(self,*args):return False
        class Opener:
            def open(self,req,timeout):
                if '/apiv2/search/' in req.full_url:
                    return Resp({'count':1,'results':[snd(41,license='Attribution NonCommercial')]})
                assert 'cdn.freesound.org/' in req.full_url
                return AudioResp()
        with patch.object(f,'build_opener',return_value=Opener()):
            f.install(self.s)
            self.s.run_codex('c'*12,'alpha','Hitta ljud från Freesound')
            row=f.overview(self.s,'alpha')['jobs'][0]
            self.assertEqual(row['status'],'done')
            self.assertEqual(row['suggestions'][0]['license'],'CC BY-NC')
            self.assertNotIn(KEY,self.s.calls[0][2])
            self.assertIn('CC BY-NC',self.s.calls[0][2])
            response=f.approve(self.s,{'project':'alpha','job_id':row['id'],'sound_id':41,
                                       'approval':'APPROVE_FREESOUND_PREVIEW'})
        self.assertTrue(response['imported'])
        self.assertEqual(response['asset']['license'],'CC BY-NC')
        self.assertTrue((self.s.path_for('alpha')/'management'/'freesound-library'/response['asset']['filename']).is_file())
        self.assertEqual(f.overview(self.s,'beta')['library'],[])

    def test_retry_does_not_happen_on_http_error(self):
        from urllib.error import HTTPError
        self.s.approved()
        f.real_reply=lambda *_:json.dumps({'tool':'freesound','query':'hare rabbit animal sound'})
        calls=[]
        class Opener:
            def open(self,req,timeout):
                calls.append(req.full_url)
                raise HTTPError(req.full_url,429,'Too many requests',{},None)
        with patch.object(f,'build_opener',return_value=Opener()):
            f.install(self.s)
            self.s.run_codex('c'*12,'alpha','Testa ljud')
        self.assertEqual(len(calls),1)
        self.assertIn('429',f.overview(self.s,'alpha')['jobs'][0]['error'])

if __name__=='__main__':unittest.main(verbosity=2)
