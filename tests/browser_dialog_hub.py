"""Offline browser regression: one shared decision viewer from several office surfaces."""
from pathlib import Path
import base64, io, wave, math, struct
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent

def wav_sample():
    out=io.BytesIO()
    with wave.open(out,'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000)
        f.writeframes(b''.join(struct.pack('<h',int(9000*math.sin(2*math.pi*440*i/8000))) for i in range(8000)))
    return base64.b64encode(out.getvalue()).decode()

SAMPLE=wav_sample()
PAGE='''<!DOCTYPE html><html lang="sv"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'none'"> </head><body class="live-project">
<select id="projectSelect"><option value="sj">Sjutbanan</option></select>
<dialog id="pw138Cafe" open><div class="pw138-sheet"><header class="pw138-head">☕ Fikarummet</header><textarea id="pw139Owner">Vi måste diskutera ljud till banan</textarea></div></dialog>
<dialog id="pw18Desk"><div class="pw18-paper pw18-music"><header class="pw18-head">🎵 Musikstudion</header></div></dialog>
<dialog id="localStudioDialog"><div class="local-shell-body"><section class="pw-report-detail">Testresultat</section></div></dialog>
<aside id="agentDrawer"><div id="agentDrawerContent"><div class="agent-detail"><div class="agent-detail-head">Gunnar</div><p>Aktivt uppdrag</p></div></div></aside>
</body></html>'''

BOOT='''
window.__PIXEL_WORKS_DEMO__={model:{activeProjectId:'sj',project:{agents:[{id:'a1',name:'Gunnar'}]}},ui:{selectedAgentId:'a1'}};
window.calls=[];
window.offers=[
{id:'sound:0123456789abcdef:33',kind:'audio',title:'Tivoli',description:'Bakgrund',employee:'Chefen',station:'music',source:'freesound',status:'waiting',preview_available:true},
{id:'img:001',kind:'image',title:'Älgen',description:'Cartoon',employee:'Gunnar',station:'art',source:'agent-file',status:'waiting',preview_available:false}
];
window.pixelWorksApi=async function(path,data){
  calls.push({path,data});
  if(path.startsWith('/api/pw-tools/review/preview'))return {mime:'audio/wav',base64:window.wavBase64,seconds:1.0};
  if(path.startsWith('/api/pw-tools/review?'))return {offers:offers};
  if(path.startsWith('/api/pw-tools/decisions?'))return {cases:[],policy:{retry_git_conflict_once:true,auto_retry_transient_once:false}};
  if(path==='/api/pw-tools/review'&&data){
    const offer=offers.find(x=>x.id===data.offer_id);if(offer)offer.status={yes:'approved',no:'rejected',maybe:'maybe'}[data.decision];
    return {status:'ok'};
  }
  throw new Error('Unexpected API '+path);
};
'''

def test():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1100,'height':850})
        errs=[];page.on('pageerror',lambda x:errs.append(str(x)))
        page.set_content(PAGE)
        page.evaluate('window.wavBase64='+repr(SAMPLE))
        page.evaluate("() => {"+BOOT+"}")
        page.add_script_tag(path=str(ROOT/'src/pw-media-review.js'))
        page.add_script_tag(path=str(ROOT/'src/pw-dialog-hub.js'))
        page.wait_for_timeout(80)
        page.locator('#pw138Cafe .pwd-context').wait_for()
        assert page.locator('#pw18Desk .pwd-context').count()==1
        assert page.locator('#agentDrawerContent .pwd-context').count()==1
        assert page.locator('#localStudioDialog .pwd-context').count()==1
        # Delayed/staged dialog created later must also get the same entry.
        page.evaluate('''() => {let x=document.createElement('dialog');x.id='pw13Dialog';
          x.innerHTML='<div class="pw13-shell"><div>Studio</div></div>';document.body.append(x)}''')
        page.locator('#pw13Dialog .pwd-context').wait_for(timeout=3500,state='attached')
        # Two modals may coexist: source cafe is preserved behind review.
        page.locator('#pw138Cafe .pwd-context button').evaluate('(el)=>el.click()')
        page.wait_for_function("() => document.querySelector('#pwReviewDlg').open")
        assert page.locator('#pw138Cafe').evaluate('(x)=>x.open')
        assert page.locator('#pw139Owner').input_value()=='Vi måste diskutera ljud till banan'
        assert page.locator('#pwReviewDlg [data-pwr-category=audio]').get_attribute('aria-pressed')=='true'
        assert page.locator('#pwReviewDlg [data-pwr-id="sound:0123456789abcdef:33"]').count()==1
        assert page.locator('#pwReviewDlg [data-pwr-id="img:001"]').count()==0
        page.locator('#pwReviewDlg [data-pwr-load]').click()
        page.wait_for_function("() => !!document.querySelector('#pwReviewDlg audio') && document.querySelector('#pwReviewDlg audio').duration>0",timeout=9000)
        page.wait_for_function("() => !document.querySelector('#pwReviewDlg [data-pwr-decision=yes]').disabled",timeout=4000)
        page.locator('#pwReviewDlg [data-pwr-play]').click()
        page.wait_for_function("() => document.querySelector('#pwReviewDlg audio').currentTime>0",timeout=5000)
        # Search and category operate inside the same dialog, never spawning special UI.
        page.locator('#pwrSearch').fill('tivoli')
        assert page.locator('#pwReviewDlg [data-pwr-id="sound:0123456789abcdef:33"]').count()==1
        page.locator('#pwReviewDlg [data-pwr-category=image]').click()
        assert page.locator('#pwReviewDlg [data-pwr-id="img:001"]').count()==0
        page.locator('#pwReviewDlg [data-pwr-clear-context]').click()
        page.locator('#pwrSearch').fill('')
        assert page.locator('#pwReviewDlg [data-pwr-id="img:001"]').count()==1
        page.locator('#pwReviewDlg [data-pwr-category=audio]').click()
        page.locator('#pwReviewDlg [data-pwr-id="sound:0123456789abcdef:33"] textarea').fill('Spara för nästa sprint')
        page.locator('#pwReviewDlg [data-pwr-decision=maybe]').click()
        page.wait_for_function("() => window.calls.some(x=>x.data?.decision==='maybe')",timeout=4000)
        page.locator('#pwReviewDlg [data-pwr-close]').first.click()
        assert page.locator('#pw138Cafe').evaluate('(x)=>x.open')
        # Agent context uses the same route and focuses that employee's proposals.
        page.locator('#agentDrawerContent .pwd-context button').evaluate('(el)=>el.click()')
        assert 'Gunnar' in page.locator('#pwrContextLabel').inner_text()
        assert page.locator('#pwReviewDlg [data-pwr-id="img:001"]').count()==1
        assert page.locator('#pwReviewDlg [data-pwr-id="sound:0123456789abcdef:33"]').count()==0
        page.locator('#pwReviewDlg [data-pwr-clear-context]').click()
        assert page.locator('#pwReviewDlg [data-pwr-id="sound:0123456789abcdef:33"]').count()==1
        assert not errs,errs
        print('PASS: café, station, agent, rapport, delayed studio, media playback, filters, search, maybe, preserved draft')
        browser.close()

if __name__=='__main__':test()
