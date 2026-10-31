"""Browser integration regression with REAL Pixel Works CSP on HTTP responses.

Run from project root (optional browser test):
  python3 tests/browser_media_csp.py
Requires playwright + Chromium. No third-party API calls.
"""
import base64
import io
import json
import math
import struct
import sys
import threading
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
import pw_media_review as review

FRONTEND = (ROOT / 'src' / 'pw-media-review.js').read_text(encoding='utf-8')

CORE_CSP = ("default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; img-src 'self' data:; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'")

wav = io.BytesIO()
with wave.open(wav, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
    samples = (struct.pack('<h', int(4800 * math.sin(math.tau * 440 * i/24000))) for i in range(24000))
    w.writeframes(b''.join(samples))
WAV = base64.b64encode(wav.getvalue()).decode('ascii')
# Tiny in-memory PNG with no external dependency.
PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL/kQAAAABJRU5ErkJggg=='

MOCK_JS = '''
  window.__PIXEL_WORKS_DEMO__ = {model:{activeProjectId:'cat'}};
  const offers = [
    {id:'sound:aaaaaaaaaaaaaaaa:123',kind:'audio',title:'Provljud',employee:'Chefen',description:'Riktigt ljud',source:'freesound',preview_available:true,status:'waiting'},
    {id:'file:ffffffffffff:abcd1234abcd1234',kind:'image',title:'Bildförslag',employee:'Gunnar',description:'Riktig bild',source:'agent-file',preview_available:true,status:'waiting'}
  ];
  window.pixelWorksApi = async (path) => {
    if(path.startsWith('/api/pw-tools/decisions'))return {cases:[],policy:{retry_git_conflict_once:true}};
    if(path.includes('/preview?'))return path.includes('sound%3A')?
      {mime:'audio/wav',base64:__WAV__,seconds:1,verified_decode:true}:
      {mime:'image/png',base64:__PNG__};
    if(path.startsWith('/api/pw-tools/review'))return {offers};
    throw Error('Okänd testväg '+path);
  };
'''.replace('__WAV__', json.dumps(WAV)).replace('__PNG__',json.dumps(PNG))

PAGE = '''<!DOCTYPE html><html lang="sv"><head><meta charset="utf-8"></head>
<body class="live-project"><select id="projectSelect"><option value="cat">Cat</option></select>
<div id="dockDialogContent">Inställningar &amp; diagnostik</div><dialog id="dockDialog"></dialog>
<script src="/fixture.js"></script><script src="/review.js"></script></body></html>'''


def server(fixed):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            resource = {'/': (PAGE,'text/html'),'/fixture.js': (MOCK_JS,'text/javascript'),
                        '/review.js': (FRONTEND,'text/javascript')}.get(self.path)
            if resource is None:
                self.send_error(404);return
            body,typ=resource
            body=body.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type',typ)
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Content-Security-Policy',review._allow_local_media_previews(CORE_CSP) if fixed else CORE_CSP)
            self.end_headers()
            self.wfile.write(body)
        def log_message(self,*args):pass
    http=ThreadingHTTPServer(('127.0.0.1',0), Handler)
    th=threading.Thread(target=http.serve_forever,daemon=True); th.start()
    return http, 'http://127.0.0.1:'+str(http.server_port)


def main():
    # Real CSP rules reproduced by the browser using a META policy. The
    # separate unittest also checks the actual HTTP handler header rewrite.
    from html import escape
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        for fixed in (False,True):
            page=browser.new_page(viewport={'width':1000,'height':850})
            csp=[]
            page.on('console',lambda msg: csp.append(msg.text) if 'Content Security Policy' in msg.text else None)
            policy=review._allow_local_media_previews(CORE_CSP) if fixed else CORE_CSP
            html='<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="'+escape(policy,quote=True)+'"></head><body class="live-project"><select id="projectSelect"><option value="cat">Cat</option></select><div id="dockDialogContent">Inställningar &amp; diagnostik</div><dialog id="dockDialog"></dialog></body></html>'
            page.set_content(html)
            # CDP evaluate can bootstrap this local offline fixture despite CSP
            # forbidding inline script tags. The app itself still runs normally.
            page.evaluate("(()=>{"+MOCK_JS+";return true;})()")
            page.evaluate(FRONTEND)
            page.locator('#pwReviewDlg').wait_for(state='visible',timeout=7000)
            sound=page.locator('.pwr-offer').filter(has_text='Provljud')
            sound.locator('[data-pwr-load]').click()
            if fixed:
                expect(sound.locator(".pwr-yes")).to_be_enabled(timeout=7000)
                sound.locator('[data-pwr-play]').click()
                page.wait_for_timeout(550)
                assert sound.locator("audio").evaluate("(el)=>el.currentTime") > 0.02
            else:
                sound.locator('text=Firefox kunde inte avkoda').wait_for(timeout=7000)
                assert not sound.locator('.pwr-yes').is_enabled()
                assert any('blob' in message for message in csp),csp
            picture=page.locator('.pwr-offer').filter(has_text='Bildförslag')
            picture.locator('[data-pwr-load]').click()
            if fixed:
                expect(picture.locator(".pwr-yes")).to_be_enabled(timeout=7000)
                assert picture.locator('img').count()==1
                print('PASS: patched CSP -> WAV plays and PNG loads, both review buttons work')
            else:
                picture.locator('text=Firefox kunde inte avkoda').wait_for(timeout=7000)
                assert not picture.locator('.pwr-yes').is_enabled()
                print('REPRODUCED: core CSP -> WAV and PNG blob URLs blocked')
            page.close()
        browser.close()

if __name__=='__main__':main()
