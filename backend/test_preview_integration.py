"""Regression: web preview API must return URL without AttributeError."""
import importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import urlopen
import json

spec=importlib.util.spec_from_file_location('pwpreview',Path(__file__).with_name('server.py'))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class PreviewIntegration(unittest.TestCase):
    def test_preview_endpoint_and_content(self):
        with tempfile.TemporaryDirectory() as directory:
            oldroot, oldprojects = mod.ROOT, mod.PROJECTS
            try:
                mod.ROOT=Path(directory)
                mod.PROJECTS=mod.ROOT/'projects'
                mod.create_project({'name':'Minesweeper','slug':'minesweeper','idea':'Test', 'genre':'Puzzle', 'platform':'Webbläsare','priority':'Kvalitet'})
                work=mod.PROJECTS/'minesweeper'/'work'
                (work/'index.html').write_text('<h1>Preview fungerar</h1>',encoding='utf-8')
                api=ThreadingHTTPServer(('127.0.0.1',0),mod.Handler)
                preview=ThreadingHTTPServer(('127.0.0.1',0),mod.PreviewHandler)
                api.preview_port=preview.server_port
                threads=[threading.Thread(target=s.serve_forever,daemon=True) for s in (api,preview)]
                for t in threads:t.start()
                try:
                    with urlopen(f'http://127.0.0.1:{api.server_port}/api/projects/minesweeper/preview') as resp:
                        data=json.load(resp)
                    self.assertTrue(data['ready'])
                    self.assertIn(f':{preview.server_port}/preview/minesweeper/',data['url'])
                    with urlopen(data['url']) as resp:
                        self.assertIn('Preview fungerar',resp.read().decode())
                    with urlopen(f'http://127.0.0.1:{preview.server_port}/health') as resp:
                        self.assertIn('pixel-works-preview-ready',resp.read().decode())
                finally:
                    for s in (api,preview):s.shutdown();s.server_close()
                    for t in threads:t.join(timeout=2)
            finally:
                mod.ROOT,mod.PROJECTS=oldroot,oldprojects
if __name__=='__main__':unittest.main()
