"""LAN-only behavior regression: offline, local loopback sockets only."""
import base64
import http.client
import ipaddress
import json
import os
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import patch

import pw_lan

PASS='correct-horse-password'


class StubHandler(BaseHTTPRequestHandler):
    def allowed(self):return True
    def auth(self):return True
    def same_origin(self):return True
    def reply(self,status,data):
        body=json.dumps(data).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=='/api/bootstrap':return self.reply(200,{'token':'secret-server-token'})
        if self.path=='/api/projects/example/preview':
            return self.reply(200,{'ready':True,'url':'http://127.0.0.1:'+str(self.server.server_port+1)+'/preview/example/'})
        return self.reply(404,{'error':'No route'})
    def do_POST(self):
        if not self.same_origin():return self.reply(403,{'error':'csrf'})
        size=int(self.headers.get('Content-Length',0));self.rfile.read(size)
        return self.reply(200,{'ok':True})
    def log_message(self,*args):pass


class StubPreview(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'OK')
    def log_message(self,*args):pass


class LANTests(unittest.TestCase):
    def test_mode_off_and_secrets_unset(self):
        with patch.dict(os.environ,{'PIXEL_WORKS_LAN_PASSWORD':'temporary-secret'},clear=True):
            self.assertIsNone(pw_lan._config())
            self.assertNotIn('PIXEL_WORKS_LAN_PASSWORD',os.environ)

    def test_lan_requires_explicit_trust_or_password(self):
        with patch.dict(os.environ,{'PIXEL_WORKS_LAN_IP':'192.168.0.8'},clear=True):
            with self.assertRaisesRegex(ValueError,'PIXEL_WORKS_LAN_TRUSTED'):pw_lan._config()
        with patch.dict(os.environ,{'PIXEL_WORKS_LAN_IP':'192.168.0.8','PIXEL_WORKS_LAN_TRUSTED':'1'},clear=True):
            ip,net,pwd=pw_lan._config()
            self.assertEqual(ip,'192.168.0.8')
            self.assertIsNone(pwd)
            self.assertEqual(str(net),'192.168.0.0/24')
            self.assertNotIn('PIXEL_WORKS_LAN_TRUSTED',os.environ)
        with patch.dict(os.environ,{'PIXEL_WORKS_LAN_IP':'192.168.0.8','PIXEL_WORKS_LAN_PASSWORD':PASS},clear=True):
            ip,net,pwd=pw_lan._config()
            self.assertEqual(ip,'192.168.0.8')
            self.assertIn(ipaddress.ip_address('192.168.0.27'),net)
            self.assertNotIn('PIXEL_WORKS_LAN_PASSWORD',os.environ)
            self.assertEqual(pwd,PASS)

    def test_invalid_network_and_public_address_rejected(self):
        for ip in ('8.8.8.8','0.0.0.0','127.0.0.2','169.254.3.3'):
            with self.subTest(ip=ip),patch.dict(os.environ,{'PIXEL_WORKS_LAN_IP':ip,'PIXEL_WORKS_LAN_PASSWORD':PASS},clear=True):
                with self.assertRaises(ValueError):pw_lan._config()
        with patch.dict(os.environ,{'PIXEL_WORKS_LAN_IP':'192.168.0.8','PIXEL_WORKS_LAN_PASSWORD':PASS,'PIXEL_WORKS_LAN_CIDR':'0.0.0.0/0'},clear=True):
            with self.assertRaises(ValueError):pw_lan._config()

    def test_host_peer_and_basic(self):
        fake=SimpleNamespace(headers={'Host':'192.168.0.8:8765'},server=SimpleNamespace(server_port=8765),client_address=('192.168.0.34',33000))
        network=ipaddress.ip_network('192.168.0.0/24')
        self.assertTrue(pw_lan._host_allowed(fake,'192.168.0.8',network))
        self.assertFalse(pw_lan._basic_ok(fake,PASS))
        fake.headers['Authorization']='Basic '+base64.b64encode(b'pixelworks:'+PASS.encode()).decode()
        self.assertTrue(pw_lan._basic_ok(fake,PASS))
        fake.headers['Authorization']='Basic '+base64.b64encode(b'pixelworks:wrong').decode()
        self.assertFalse(pw_lan._basic_ok(fake,PASS))
        fake.headers['Host']='evil.site:8765'
        self.assertFalse(pw_lan._host_allowed(fake,'192.168.0.8',network))
        fake.headers['Host']='192.168.0.8:8765'
        fake.client_address=('192.168.1.200',55)
        self.assertFalse(pw_lan._host_allowed(fake,'192.168.0.8',network))

    def test_explicit_trusted_subnet_has_no_login_but_origin_is_checked(self):
        import threading
        srv=SimpleNamespace(ThreadingHTTPServer=ThreadingHTTPServer,Handler=type('Main',(StubHandler,),{}),
                            PreviewHandler=type('Preview',(StubPreview,),{}),run_server=lambda port:0)
        with patch.object(pw_lan,'_config',return_value=('127.0.0.2',ipaddress.ip_network('127.0.0.0/8'),None)):
            pw_lan.install(srv)
            main=srv.ThreadingHTTPServer(('127.0.0.1',0),srv.Handler)
            port=main.server_port
            thread=threading.Thread(target=main.serve_forever,daemon=True);thread.start()
            def request(host,method,path,origin=None,body=None,headers_extra=None):
                connection=http.client.HTTPConnection(host,port,timeout=3)
                headers={'Host':host+':'+str(port)}
                if origin:headers['Origin']=origin
                if headers_extra:headers.update(headers_extra)
                connection.request(method,path,body=body,headers=headers)
                response=connection.getresponse();status=response.status
                raw=response.read();connection.close()
                return status,raw
            try:
                self.assertEqual(request('127.0.0.2','GET','/api/bootstrap')[0],200)
                status,data=request('127.0.0.2','GET','/api/projects/example/preview')
                self.assertEqual(status,200)
                self.assertIn(('http://127.0.0.2:'+str(port+1)).encode(),data)
                self.assertEqual(request('127.0.0.2','POST','/api/jobs',origin='http://evil.local',body=b'{}')[0],403)
                self.assertEqual(request('127.0.0.2','POST','/api/jobs',origin='http://127.0.0.2:'+str(port),body=b'{}')[0],200)
                self.assertEqual(request('127.0.0.2','HEAD','/backend/server.py')[0],405)
                self.assertEqual(request('127.0.0.2','GET','/api/bootstrap',headers_extra={'Host':'evil.local:'+str(port)})[0],403)
                preview=srv.ThreadingHTTPServer(('127.0.0.1',0),srv.PreviewHandler)
                pt=threading.Thread(target=preview.serve_forever,daemon=True);pt.start()
                try:
                    c=http.client.HTTPConnection('127.0.0.2',preview.server_port,timeout=3)
                    c.request('GET','/preview/example/',headers={'Host':'127.0.0.2:'+str(preview.server_port)})
                    response=c.getresponse();self.assertEqual(response.status,200)
                    self.assertEqual(response.read(),b'OK');c.close()
                finally:preview.shutdown();preview.server_close();pt.join(timeout=3)
            finally:main.shutdown();main.server_close();thread.join(timeout=3)

    def test_two_interface_http_auth_preview_and_origin(self):
        srv=SimpleNamespace(ThreadingHTTPServer=ThreadingHTTPServer,Handler=type('Main',(StubHandler,),{}),
                            PreviewHandler=type('Preview',(StubPreview,),{}),run_server=lambda port:0)
        with patch.object(pw_lan,'_config',return_value=('127.0.0.2',ipaddress.ip_network('127.0.0.0/8'),PASS)), \
             patch.object(pw_lan,'_local_peer',side_effect=lambda h:(h.headers.get('Host') or '').startswith('127.0.0.1:')):
            pw_lan.install(srv)
            main=srv.ThreadingHTTPServer(('127.0.0.1',0),srv.Handler)
            port=main.server_port
            self.assertEqual(main._pw_sidecar.server_port,port)
            main.daemon_threads=True
            import threading
            thread=threading.Thread(target=main.serve_forever,daemon=True);thread.start()
            # 127.0.0.2 behaves like the LAN interface, but all sockets stay on loopback.
            def request(host,path='/',method='GET',origin=None,login=None,body=None):
                c=http.client.HTTPConnection(host,port,timeout=3)
                headers={'Host':host+':'+str(port)}
                if origin:headers['Origin']=origin
                if login:headers['Authorization']='Basic '+base64.b64encode(login.encode()).decode()
                if body is not None:headers['Content-Type']='application/json'
                c.request(method,path,body=body,headers=headers)
                response=c.getresponse();raw=response.read();code=response.status
                auth=response.getheader('WWW-Authenticate');c.close();return code,raw,auth
            try:
                status,body,_=request('127.0.0.1','/api/bootstrap')
                self.assertEqual(status,200)
                self.assertIn(b'secret-server-token',body)
                status,body,challenge=request('127.0.0.2','/api/bootstrap')
                self.assertEqual(status,401)
                self.assertNotIn(b'secret-server-token',body)
                self.assertIn('Basic',challenge)
                status,body,_=request('127.0.0.2','/api/bootstrap',login='pixelworks:'+PASS)
                self.assertEqual(status,200)
                self.assertIn(b'secret-server-token',body)
                status,body,_=request('127.0.0.2','/api/projects/example/preview',login='pixelworks:'+PASS)
                self.assertEqual(status,200)
                self.assertIn(('http://127.0.0.2:'+str(port+1)).encode(),body)
                status,_,_=request('127.0.0.2','/api/jobs','POST','http://untrusted.local',login='pixelworks:'+PASS,body=b'{}')
                self.assertEqual(status,403)
                status,body,_=request('127.0.0.2','/api/jobs','POST','http://127.0.0.2:'+str(port),login='pixelworks:'+PASS,body=b'{}')
                self.assertEqual(status,200)
                self.assertIn(b'"ok": true',body)
                status,_,_=request('127.0.0.2','/backend/server.py','HEAD',login='pixelworks:'+PASS)
                self.assertEqual(status,405)
                # Also protect the separate static game preview origin.
                preview=srv.ThreadingHTTPServer(('127.0.0.1',0),srv.PreviewHandler)
                pport=preview.server_port
                t=threading.Thread(target=preview.serve_forever,daemon=True);t.start()
                try:
                    def pget(auth):
                        c=http.client.HTTPConnection('127.0.0.2',pport,timeout=3)
                        headers={'Host':'127.0.0.2:'+str(pport)}
                        if auth:headers['Authorization']='Basic '+base64.b64encode(('pixelworks:'+PASS).encode()).decode()
                        c.request('GET','/preview/example/',headers=headers)
                        res=c.getresponse();code=res.status;content=res.read();c.close();return code,content
                    self.assertEqual(pget(False)[0],401)
                    self.assertEqual(pget(True),(200,b'OK'))
                finally:
                    preview.shutdown();preview.server_close();t.join(timeout=3)
            finally:
                main.shutdown();main.server_close();thread.join(timeout=3)


if __name__=='__main__': unittest.main()
