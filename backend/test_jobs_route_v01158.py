import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer

spec=importlib.util.spec_from_file_location('pixelworks_jobs_fix',Path(__file__).with_name('server.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class JobsRouteTests(unittest.TestCase):
    def test_jobs_route_is_not_misread_as_project_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_root,old_projects=mod.ROOT,mod.PROJECTS
            mod.ROOT=Path(tmp);mod.PROJECTS=Path(tmp)/'projects'
            try:
                mod.create_project({'name':'Minesweeper','slug':'minesweeper','idea':'Minesweeper'})
                with ThreadingHTTPServer(('127.0.0.1',0),mod.Handler) as server:
                    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                    try:
                        url='http://127.0.0.1:%s/api/projects/minesweeper/jobs'%server.server_port
                        request=Request(url,headers={'X-Pixelworks-Token':mod.TOKEN})
                        with urlopen(request,timeout=5) as response:
                            data=json.load(response)
                            self.assertEqual(response.status,200)
                            self.assertEqual(data,{'jobs':[]})
                    finally:
                        server.shutdown();thread.join(timeout=5)
            finally:
                mod.ROOT,mod.PROJECTS=old_root,old_projects
