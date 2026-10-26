"""Offline regression of continuous production; no real AI/network calls."""
import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pw_v0133
import pw_v0135

class ContinuousFlow(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name)
  self.people=[{'id':'chief','name':'Chefen','role_type':'lead','provider':'codex','station':'lead','allowed_stations':['lead']},
               {'id':'greta','name':'Greta','role_type':'creative','provider':'gemini','station':'docs','allowed_stations':['docs']},
               {'id':'gunnar','name':'Gunnar','role_type':'programmer','provider':'codex','station':'code','allowed_stations':['code','qa']}]
  self.orders=[];self.reports=[];self.jobs={}
  def write(slug,orders):self.orders=copy.deepcopy(orders)
  self.srv=SimpleNamespace(ROOT=root,project_mandate=lambda s:{'enabled':True},
    orders_read=lambda s:self.orders,orders_write=write,
    staff_read=lambda s:self.people,get_skill_settings=lambda s:{},list_reports=lambda s:self.reports,
    LOCK=threading.RLock(),JOBS=self.jobs,SKILL_STATIONS={'lead':'planning','docs':'writing','code':'coding','qa':'testing'},
    agent_authorized=lambda s,p,station:station in p['allowed_stations'])
  self.approved=patch('pw_v0135.authorized',return_value=True)
  self.approved.start();self.addCleanup(self.approved.stop)
  self.outline={'summary':'Gör ett pusselspel','tasks':[
   {'key':'design','station':'docs','title':'Speldesign','priority':1,
    'instruction':'Designa ett spelbart första pussel utifrån spelidén','depends_on':[]},
   {'key':'code','station':'code','title':'Spelkod','priority':2,
    'instruction':'Implementera ett spelbart pussel med dragbara bitar','depends_on':['design']},
   {'key':'qa','station':'qa','title':'Tester','priority':2,
    'instruction':'Verifiera att alla pusselbitarna fungerar rätt','depends_on':['code']}]}
  self.job={'id':'0123456789ab','station':'lead','instruction':'Gör en plan och starta utvecklingen'}
 def create(self):
  return pw_v0133.create_orders(self.srv,'pussel',self.job,self.outline)
 def test_drafts_are_released_without_click(self):
  rows,ok=self.create();self.assertTrue(ok)
  self.assertEqual(len(rows),3)
  self.assertFalse(rows[0]['plan_approved'])
  count=pw_v0135.release_pending(self.srv,'pussel')
  self.assertEqual(count,1)
  self.assertTrue(all(o['plan_approved'] for o in self.orders))
  self.assertEqual(pw_v0135.release_pending(self.srv,'pussel'),0)
  self.assertTrue(pw_v0133.ready(self.srv,'pussel',self.orders[0])[0])
  self.assertFalse(pw_v0133.ready(self.srv,'pussel',self.orders[1])[0])
 def test_revocation_does_not_release(self):
  self.create()
  with patch('pw_v0135.authorized',return_value=False):
   self.assertEqual(pw_v0135.release_pending(self.srv,'pussel'),0)
  self.assertFalse(self.orders[0]['plan_approved'])
 def test_bad_staff_cannot_create_or_auto_release(self):
  self.create();self.orders[0]['assigned_agent_id']='unknown'
  self.assertEqual(pw_v0135.release_pending(self.srv,'pussel'),0)
  self.assertFalse(self.orders[0]['plan_approved'])
 def test_advisory_report_unblocks_without_claiming_approval(self):
  self.create();pw_v0135.release_pending(self.srv,'pussel')
  self.assertFalse(pw_v0135.dependency_status(self.srv,'pussel',self.orders[1])[0])
  self.orders[0].update(status='review',job_id='aaaabbbbcccc')
  self.reports=[{'id':'aaaabbbbcccc','order_id':self.orders[0]['id'],
    'source':'gemini-api','state':'review','agent_id':'greta',
    'summary':'Förslaget beskriver en konkret spelbar tre-gånger-tre pusselplan med en dragfunktion.'}]
  result=pw_v0135.dependency_status(self.srv,'pussel',self.orders[1])
  self.assertEqual(result,(True,''))
  self.assertEqual(self.orders[0]['status'],'review')
  self.assertEqual(self.reports[0]['state'],'review')
  context=pw_v0135.reference_context(self.srv,'pussel',self.orders[1]);self.assertIn('tre-gånger-tre',context)
  self.assertIn('ej ägargodkänt',context)
 def test_forged_report_cannot_unblock(self):
  self.create();pw_v0135.release_pending(self.srv,'pussel')
  self.orders[0].update(status='review',job_id='aaaabbbbcccc')
  self.reports=[{'id':'xyzxyzxyzxyz','order_id':self.orders[0]['id'],
    'source':'gemini-api','state':'review','agent_id':'greta',
    'summary':'Vi har ett väldigt långt men felaktigt påstående här.'}]
  self.assertFalse(pw_v0135.dependency_status(self.srv,'pussel',self.orders[1])[0])
 def test_failed_or_unintegrated_code_still_blocks_qa(self):
  self.create();pw_v0135.release_pending(self.srv,'pussel')
  self.orders[1].update(status='done',job_id='111122223333')
  self.reports=[{'id':'111122223333','order_id':self.orders[1]['id'],'state':'done','integrated':False}]
  self.assertFalse(pw_v0135.dependency_status(self.srv,'pussel',self.orders[2])[0])
  self.reports[0]['integrated']=True
  self.assertTrue(pw_v0135.dependency_status(self.srv,'pussel',self.orders[2])[0])
 def test_wrong_project_or_missing_report_cannot_leak_context(self):
  self.create();pw_v0135.release_pending(self.srv,'pussel')
  self.assertEqual(pw_v0135.reference_context(self.srv,'pussel',self.orders[1]),'')
 def test_no_duplicate_orders_on_replan(self):
  self.create();pw_v0135.release_pending(self.srv,'pussel')
  old=copy.deepcopy(self.orders)
  new,ok=self.create()
  self.assertFalse(ok)
  self.assertEqual(old,self.orders)

if __name__=='__main__':unittest.main()

class InstalledHooks(ContinuousFlow):
 def setUp(self):
  super().setUp()
  self.old_functions={name:getattr(pw_v0133,name) for name in ('ready','get_view','create_orders')}
  self.addCleanup(lambda:[setattr(pw_v0133,k,v) for k,v in self.old_functions.items()])
  self.run_calls=[]
  self.srv.reconcile_orders_from_reports=lambda slug:None
  self.srv.run_codex=lambda jid,slug,prompt:self.run_calls.append(prompt)
  self.srv._PW_V0135=False
  pw_v0135.install(self.srv)
 def create(self):
  return self.old_functions['create_orders'](self.srv,'pussel',self.job,self.outline)
 def test_manager_planning_releases_without_any_plan_click(self):
  created,committed=pw_v0133.create_orders(self.srv,'pussel',self.job,self.outline)
  self.assertTrue(committed)
  self.assertEqual(len(created),3)
  self.assertTrue(all(o['plan_approved'] for o in self.orders))
  self.assertEqual(pw_v0133.get_view(self.srv,'pussel')['draft_plans'],[])
  self.assertTrue(pw_v0133.ready(self.srv,'pussel',self.orders[0])[0])
 def test_existing_draft_released_on_normal_scheduler_poll(self):
  # Simulate a draft written by 0.13.4 before the new update.
  original=self.old_functions['create_orders']
  original(self.srv,'pussel',self.job,self.outline)
  self.assertFalse(self.orders[0]['plan_approved'])
  self.srv.reconcile_orders_from_reports('pussel')
  self.assertTrue(self.orders[0]['plan_approved'])
 def test_worker_receives_report_with_unapproved_marker(self):
  self.create()
  self.orders[0].update(status='review',job_id='aaaabbbbcccc')
  self.reports=[{'id':'aaaabbbbcccc','order_id':self.orders[0]['id'],
   'source':'gemini-api','state':'review','agent_id':'greta',
   'summary':'En välbeskriven spelidé med klickbara pusselbitar och två lägen för användaren.'}]
  self.srv.JOBS['worker123']={'id':'worker123','station':'code','order_id':self.orders[1]['id']}
  self.srv.run_codex('worker123','pussel','Implementera spelet.')
  self.assertEqual(len(self.run_calls),1)
  self.assertIn('klickbara pusselbitar',self.run_calls[0])
  self.assertIn('ej ägargodkänt',self.run_calls[0])
 def test_user_declines_permission_workflow_remains_draft(self):
  with patch('pw_v0135.authorized',return_value=False):
   pw_v0133.create_orders(self.srv,'pussel',self.job,self.outline)
  self.assertFalse(self.orders[0]['plan_approved'])
