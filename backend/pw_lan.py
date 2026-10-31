"""Pixel Works opt-in LAN: additional private-interface listeners, optional Basic login.

The original 127.0.0.1 listeners and safe project-preview origin are preserved.
No LAN login or address configuration is persisted, and AI child processes do not
inherit the LAN password. Use only on a trusted home network (HTTP is not TLS).
"""
import base64
import binascii
import ipaddress
import os
import re
import secrets
import sys
import threading
from urllib.parse import urlparse

_LOGIN = 'pixelworks'
_PREVIEW_API = re.compile(r'^/api/projects/[a-z0-9-]+/preview$')


def _config():
    lan_ip = os.environ.get('PIXEL_WORKS_LAN_IP', '').strip()
    # Remove immediately: Codex subprocesses inherit os.environ in the core.
    password = os.environ.pop('PIXEL_WORKS_LAN_PASSWORD', None)
    trusted = os.environ.pop('PIXEL_WORKS_LAN_TRUSTED', '') == '1'
    if not lan_ip:
        return None
    try:
        address = ipaddress.ip_address(lan_ip)
    except ValueError as error:
        raise ValueError('PIXEL_WORKS_LAN_IP måste vara en IPv4-adress på ditt hemnät') from error
    if not isinstance(address, ipaddress.IPv4Address) or not address.is_private or address.is_loopback or address.is_link_local or address.is_unspecified or address.is_reserved or address.is_multicast:
        raise ValueError('LAN-läge kräver en privat IPv4-adress, t.ex. 192.168.0.8')
    if password is None or password == '':
        if not trusted:
            raise ValueError('LAN-läge kräver lösenord eller uttryckligt PIXEL_WORKS_LAN_TRUSTED=1')
        password = None  # Voluntary home-LAN mode: trusted subnet, no login.
    elif len(password) < 12 or len(password) > 256 or any(c in password for c in '\r\n\x00'):
        raise ValueError('Sätt PIXEL_WORKS_LAN_PASSWORD till ett lösenord med minst 12 tecken')
    try:
        subnet = ipaddress.ip_network(os.environ.get('PIXEL_WORKS_LAN_CIDR', lan_ip+'/24'), strict=False)
    except ValueError as error:
        raise ValueError('Ogiltigt PIXEL_WORKS_LAN_CIDR') from error
    if not isinstance(subnet, ipaddress.IPv4Network) or address not in subnet or subnet.prefixlen < 16:
        raise ValueError('LAN-nätet måste omfatta serveradressen och får inte vara större än /16')
    return lan_ip, subnet, password


def _peer_allowed(handler, subnet):
    try:
        client = ipaddress.ip_address(handler.client_address[0])
    except (ValueError, IndexError, TypeError):
        return False
    return client.is_loopback or client in subnet


def _local_peer(handler):
    try:
        return ipaddress.ip_address(handler.client_address[0]).is_loopback
    except (ValueError, IndexError, TypeError):
        return False


def _host_allowed(handler, lan_ip, subnet):
    port = int(handler.server.server_port)
    host = (handler.headers.get('Host') or '').lower().strip()
    expected = {'127.0.0.1:'+str(port), 'localhost:'+str(port), lan_ip+':'+str(port)}
    return host in expected and _peer_allowed(handler, subnet)


def _basic_ok(handler, password):
    if password is None:
        return True  # Passwordless LAN must have been explicitly enabled at boot.
    if _local_peer(handler):
        return True  # Preserve localhost behavior and the private scheduler.
    header = (handler.headers.get('Authorization') or '')
    if not header.startswith('Basic ') or len(header) > 1000:
        return False
    try:
        credentials = base64.b64decode(header[6:].strip(), validate=True)
    except (binascii.Error, ValueError):
        return False
    expected = (_LOGIN+':'+password).encode('utf-8')
    return secrets.compare_digest(credentials, expected)


def _challenge(handler):
    handler.send_response(401)
    handler.send_header('WWW-Authenticate', 'Basic realm="Pixel Works hemnät"')
    handler.send_header('Content-Type', 'text/plain; charset=utf-8')
    handler.send_header('Cache-Control', 'no-store')
    handler.send_header('Content-Length', '0')
    handler.end_headers()


def _forbid(handler):
    handler.send_response(403)
    handler.send_header('Content-Length', '0')
    handler.end_headers()


def install(srv):
    if getattr(srv, '_PW_LAN_INSTALLED', False):
        return
    # Service-control commands must work without setting a LAN password.
    action = next((word for word in sys.argv[1:] if word in ('stop', 'status')), None)
    if action:
        os.environ.pop('PIXEL_WORKS_LAN_PASSWORD', None)
        os.environ.pop('PIXEL_WORKS_LAN_TRUSTED', None)
        return
    config = _config()
    if config is None:
        return
    lan_ip, subnet, password = config
    srv._PW_LAN_INSTALLED = True

    original_server = srv.ThreadingHTTPServer
    class DualInterfaceServer(original_server):
        """Bind the existing loopback socket PLUS the selected LAN interface.

        Do not bind to 0.0.0.0 or other interfaces such as VPN/WAN.
        The existing process lifecycle closes both sockets together.
        """
        def __init__(self, address, handler_cls, *args, **kwargs):
            super().__init__(address, handler_cls, *args, **kwargs)
            self._pw_sidecar = None
            if address[0] == '127.0.0.1':
                try:
                    sidecar = original_server((lan_ip, self.server_port), handler_cls)
                    sidecar.daemon_threads = True
                    self._pw_sidecar = sidecar
                    thread = threading.Thread(target=sidecar.serve_forever, daemon=True,
                                              name='pixelworks-lan-'+str(self.server_port))
                    thread.start()
                except Exception:
                    super().server_close()
                    raise
        def server_close(self):
            if self._pw_sidecar is not None:
                self._pw_sidecar.shutdown()
                self._pw_sidecar.server_close()
                self._pw_sidecar = None
            super().server_close()
    srv.ThreadingHTTPServer = DualInterfaceServer

    handler = srv.Handler
    original_get = handler.do_GET
    original_post = handler.do_POST
    original_reply = handler.reply

    def allowed(self):
        return _host_allowed(self, lan_ip, subnet)
    def same_origin(self):
        # Explicit same-origin check prevents cross-site LAN POSTs and DNS rebinding.
        host = (self.headers.get('Host') or '').lower().strip()
        return (self.allowed() and self.headers.get('Origin', '') == 'http://'+host)
    def guard(self):
        if not self.allowed():
            _forbid(self)
            return False
        if not _basic_ok(self, password):
            _challenge(self)
            return False
        return True
    def do_GET(self):
        if not guard(self): return
        return original_get(self)
    def do_POST(self):
        if not guard(self): return
        return original_post(self)
    def reply(self, status, data):
        # Play project's static preview in a different LAN origin (:8766), not
        # the privileged app origin (:8765). Only rewrite our trusted core URL.
        path = urlparse(self.path).path
        if (status == 200 and _PREVIEW_API.fullmatch(path)
                and (self.headers.get('Host') or '').lower() == lan_ip+':'+str(self.server.server_port)
                and isinstance(data, dict) and data.get('ready') is True):
            prefix = 'http://127.0.0.1:'
            url = data.get('url', '')
            if isinstance(url, str) and url.startswith(prefix):
                data = dict(data, url='http://'+lan_ip+':'+url[len(prefix):])
        return original_reply(self, status, data)
    handler.allowed = allowed
    handler.same_origin = same_origin
    handler.do_GET = do_GET
    handler.do_POST = do_POST
    handler.reply = reply
    # Original SimpleHTTPRequestHandler.do_HEAD bypasses Pixel Works' safe
    # GET path allowlist! Disable it rather than leaking repository files.
    handler.do_HEAD = lambda self: self.send_error(405, 'HEAD stöds inte')

    preview = srv.PreviewHandler
    preview_get = preview.do_GET
    def preview_GET(self):
        if not _host_allowed(self, lan_ip, subnet):
            return _forbid(self)
        if not _basic_ok(self, password):
            return _challenge(self)
        return preview_get(self)
    preview.do_GET = preview_GET
    preview.do_HEAD = lambda self: self.send_error(405, 'HEAD stöds inte')

    original_run_server = srv.run_server
    def run_server(port):
        label = 'lösenordsskyddat' if password is not None else 'utan inloggning (betrott hemnät)'
        print('LAN-läge '+label+': http://'+lan_ip+':'+str(port), flush=True)
        print('Spelpreview (separat port, separat inloggning): http://'+lan_ip+':'+str(port+1), flush=True)
        print('Endast localhost och '+str(subnet)+' tillåts; ingen WAN/publicering.', flush=True)
        return original_run_server(port)
    srv.run_server = run_server
