"""CSP regression: the core header must allow local audio/image previews.

No AI, files outside temp dirs, network APIs or browser required.
"""
import unittest
from types import SimpleNamespace
import pw_media_review as review

CORE_CSP = ("default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; img-src 'self' data:; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'")


class FakeHandler:
    def __init__(self): self.headers_sent=[]
    def send_header(self,key,value): self.headers_sent.append((key,value))
    def do_GET(self):pass
    def do_POST(self):pass
    def end_headers(self):self.send_header('Content-Security-Policy', CORE_CSP)


class CSPTests(unittest.TestCase):
    def test_existing_core_blocks_blob_audio(self):
        self.assertNotIn('blob:', CORE_CSP)
        self.assertNotIn('media-src', CORE_CSP)
        self.assertIn("img-src 'self' data:", CORE_CSP)

    def test_only_img_and_media_are_relaxed(self):
        new=review._allow_local_media_previews(CORE_CSP)
        self.assertIn("img-src 'self' data: blob:", new)
        self.assertIn("media-src 'self' blob:", new)
        for directive in ("default-src 'self'", "style-src 'self' 'unsafe-inline'",
                          "script-src 'self'", "connect-src 'self'", "object-src 'none'",
                          "base-uri 'none'", "frame-ancestors 'none'"):
            self.assertIn(directive,new)
        self.assertNotIn("script-src 'self' blob:",new)
        self.assertNotIn("connect-src 'self' blob:",new)
        self.assertEqual(review._allow_local_media_previews(new),new)

    def test_installed_handler_rewrites_only_csp(self):
        srv=SimpleNamespace(Handler=type('OwnerHandler',(FakeHandler,),{}))
        review.install(srv)
        handler=srv.Handler()
        handler.send_header('Content-Type','text/html')
        handler.end_headers()
        self.assertEqual(handler.headers_sent[0],('Content-Type','text/html'))
        csp=[v for k,v in handler.headers_sent if k=='Content-Security-Policy']
        self.assertEqual(len(csp),1)  # two headers would INTERSECT, not merge
        self.assertIn("media-src 'self' blob:",csp[0])
        self.assertIn("img-src 'self' data: blob:",csp[0])
        self.assertEqual(csp[0].count('script-src'),1)

    def test_already_custom_policy_is_preserved(self):
        custom="default-src 'none'; img-src 'self' https://cdn.example; media-src 'self'"
        updated=review._allow_local_media_previews(custom)
        self.assertIn("default-src 'none'",updated)
        self.assertIn("img-src 'self' https://cdn.example blob:",updated)
        self.assertIn("media-src 'self' blob:",updated)
        self.assertEqual(updated.count('media-src'),1)

if __name__=='__main__':unittest.main()
