"""Pixel Works 0.12.11.17 – one active project, legible office and studio consent.

UI-only stabilization. No migrations, no AI calls or writes to game projects.
"""
VERSION='0.12.11.17'


def install(srv):
    if getattr(srv, '_PW_V0121117', False):
        return
    srv._PW_V0121117 = True
    srv.APP_VERSION = VERSION
    previous_get = srv.Handler.do_GET

    def do_GET(self):
        route=self.path.split('?',1)[0]
        if route not in ('/','/index.html'):
            return previous_get(self)
        if not self.allowed():
            return self.reply(403,{'error':'Ogiltig host'})
        content=(srv.APP/'index.html').read_text(encoding='utf-8')
        # Mirror the existing compatible script stack exactly. The v17 layer
        # only enhances visible controls; it does not override engine requests.
        for asset in ('./src/pw-v01210.js','./src/pw-v01211.js',
                      './src/pw-v012115.js','./src/pw-v012116.js',
                      './src/pw-v012117.js','./src/pw-v012118.js',
                      './src/pw-v0121111.js','./src/pw-v0121112.js',
                      './src/pw-v0121117.js'):
            tag='<script defer src="'+asset+'"></script>'
            if tag not in content:
                content=content.replace('</body>','  '+tag+'\n</body>')
        raw=content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    srv.Handler.do_GET=do_GET
