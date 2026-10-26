"""Pixel Works 0.12.11.18 – station menus and safe order creation UX.

Frontend-only layer. No migrations, no AI execution and no writes on load.
"""
VERSION='0.12.11.18'


def install(srv):
    if getattr(srv,'_PW_V0121118',False):
        return
    srv._PW_V0121118=True
    srv.APP_VERSION=VERSION
    previous=srv.Handler.do_GET
    def do_GET(self):
        if self.path.split('?',1)[0] not in ('/','/index.html'):
            return previous(self)
        if not self.allowed():
            return self.reply(403,{'error':'Ogiltig host'})
        content=(srv.APP/'index.html').read_text(encoding='utf-8')
        # Preserve every previously injected asset, adding this enhancement last.
        stack=('./src/pw-v01210.js','./src/pw-v01211.js',
               './src/pw-v012115.js','./src/pw-v012116.js',
               './src/pw-v012117.js','./src/pw-v012118.js',
               './src/pw-v0121111.js','./src/pw-v0121112.js',
               './src/pw-v0121117.js','./src/pw-v0121118.js',
               './src/pw-v013.js')
        for asset in stack:
            tag='<script defer src="'+asset+'"></script>'
            if tag not in content:
                content=content.replace('</body>','  '+tag+'\n</body>')
        data=content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    srv.Handler.do_GET=do_GET
