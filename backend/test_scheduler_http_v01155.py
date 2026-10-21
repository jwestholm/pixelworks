"""Regression: an isolated queued job must not be mistaken for a direct writer."""
import json, tempfile, threading, unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from unittest.mock import patch
import server as s

class SchedulerHttpRegression(unittest.TestCase):
 def test_scheduler_style_post_creates_isolated_tree(self):
  with tempfile.TemporaryDirectory() as temp:
   old_root,old_projects=s.ROOT,s.PROJECTS
   s.ROOT=Path(temp);s.PROJECTS=s.ROOT/'projects'
   server=None
   try:
    s.create_project({'slug':'minesweeper','name':'Minesweeper','idea':'Test','genre':'Pussel','platform':'Webbläsare'})
    worker=s.hire_codex('minesweeper',{'name':'QA','approval':'HIRE_CODEX_FOR_PROJECT'})
    staff=s.staff_read('minesweeper');staff[0]['allowed_stations']=['qa'];staff[0]['station']='qa';s.staff_write('minesweeper',staff)
    order=s.order_action('minesweeper',{'station':'qa','instruction':'Undersök problemen i mitt spel och testa dem','priority':1})['item']
    s.set_project_mandate('minesweeper',{'approval':'ALLOW_CODEX_WORKSPACE_WRITE','enabled':True})
    server=ThreadingHTTPServer(('127.0.0.1',0),s.Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    payload={'project':'minesweeper','station':'qa','agent_id':worker['id'],'instruction':order['instruction'],'order_id':order['id'],'attachment_ids':[],'isolated':True,'approval':'PROJECT_MANDATE'}
    req=Request('http://127.0.0.1:%d/api/jobs'%server.server_port,data=json.dumps(payload).encode(),method='POST',headers={'Content-Type':'application/json','Origin':'http://127.0.0.1:%d'%server.server_port,'X-Pixelworks-Token':s.TOKEN})
    with patch.object(s,'status',return_value={'execution_enabled':True}),patch.object(s,'run_codex'):
     with urlopen(req,timeout=10) as response: data=json.load(response)
    self.assertEqual(data['state'],'queued')
    self.assertTrue(Path(s.JOBS[data['job_id']]['worktree']).is_dir())
    self.assertFalse(s.JOBS[data['job_id']]['worktree'].endswith('/work'))
   finally:
    if server:server.shutdown();server.server_close()
    s.JOBS.clear();s.ROOT,s.PROJECTS=old_root,old_projects
if __name__=='__main__':unittest.main()
