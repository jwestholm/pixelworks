"""HTTP clients disconnecting during polling must not cause a second JSON write."""
import unittest
from backend import server

class TestDisconnectedClient(unittest.TestCase):
    def test_reply_does_not_retry_after_broken_pipe(self):
        class WriteFailure:
            def __init__(self):
                self.calls=0
            def write(self, data):
                self.calls += 1
                raise BrokenPipeError(32, 'Broken pipe')
        class FakeHandler:
            close_connection=False
            def __init__(self):
                self.wfile=WriteFailure()
                self.heads=[]
            def send_response(self, status): self.heads.append(status)
            def send_header(self, key, value):pass
            def end_headers(self):pass
        obj=FakeHandler()
        server.Handler.reply(obj,200,{'orders':[]})
        self.assertTrue(obj.close_connection)
        self.assertEqual(obj.wfile.calls,1)
        self.assertEqual(obj.heads,[200])
    def test_reply_does_not_hide_other_io_errors(self):
        class WriteFailure:
            def write(self, data):raise OSError(28,'No space left on device')
        class FakeHandler:
            close_connection=False
            wfile=WriteFailure()
            def send_response(self, status):pass
            def send_header(self, key, value):pass
            def end_headers(self):pass
        with self.assertRaises(OSError):
            server.Handler.reply(FakeHandler(),200,{})
