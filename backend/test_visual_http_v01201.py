"""v0.12.0.1 regression: browser-facing visual assets must have real MIME types."""
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError

from backend import server


class VisualHttpSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join(timeout=3)

    def get(self, path):
        with urlopen(f'http://127.0.0.1:{self.http.server_port}{path}', timeout=5) as response:
            return response.status, response.headers, response.read()

    def test_visual_stylesheet(self):
        status, headers, body = self.get('/visual-v2.css')
        self.assertEqual(status, 200)
        self.assertEqual(headers.get_content_type(), 'text/css')
        self.assertIn(b'office-stage', body)
        self.assertEqual(headers.get('X-Content-Type-Options'), 'nosniff')

    def test_visual_module(self):
        status, headers, body = self.get('/visual-v2.js')
        self.assertEqual(status, 200)
        self.assertIn(headers.get_content_type(), {'text/javascript','application/javascript'})
        self.assertIn(b'gameDock', body)

    def test_sprite_and_svg(self):
        status, headers, body = self.get('/assets/office-v2/desk-code.png')
        self.assertEqual(status, 200)
        self.assertEqual(headers.get_content_type(), 'image/png')
        self.assertTrue(body.startswith(b'\x89PNG\r\n\x1a\n'))
        status, headers, body = self.get('/assets/office-v2/office-backdrop.svg')
        self.assertEqual(status, 200)
        self.assertEqual(headers.get_content_type(), 'image/svg+xml')
        self.assertIn(b'<svg', body)

    def test_every_visual_asset_reference(self):
        import re
        from pathlib import Path
        css = (server.APP / 'visual-v2.css').read_text(encoding='utf-8')
        paths = sorted(set(re.findall(r"url\(['\"]?\./(assets/office-v2/[^)'\"]+)", css)))
        self.assertGreaterEqual(len(paths), 30)
        for path in paths:
            with self.subTest(path=path):
                status, headers, contents = self.get('/' + path)
                self.assertEqual(status, 200)
                self.assertTrue(headers.get_content_type().startswith('image/'))
                self.assertGreater(len(contents), 10)

    def test_existing_app_files_and_api_still_work(self):
        for path, mime in [('/', 'text/html'),('/src/main.js','text/javascript'),('/styles.css','text/css')]:
            status, headers, _ = self.get(path)
            self.assertEqual(status, 200)
            self.assertEqual(headers.get_content_type(), mime)
        status, headers, body = self.get('/api/bootstrap')
        self.assertEqual(status, 200)
        self.assertEqual(headers.get_content_type(), 'application/json')
        self.assertEqual(__import__('json').loads(body)['version'], server.APP_VERSION)

    def test_unlisted_assets_still_blocked(self):
        for path in ['/backend/server.py', '/assets/office-v2/CONCEPT_ATLAS_REFERENCE.png', '/assets/office-v2/secrets.env', '/assets/office-v2/../foo.png']:
            with self.assertRaises(HTTPError) as ctx:
                self.get(path)
            self.assertEqual(ctx.exception.code, 404)

if __name__ == '__main__':
    unittest.main()
