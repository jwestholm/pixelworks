"""A small-screen check using the same mocked, offline project data."""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
base=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('hubtest',base/'tests/browser_dialog_hub.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':375,'height':760},device_scale_factor=1)
    page.set_content(mod.PAGE)
    page.evaluate('window.wavBase64='+repr(mod.SAMPLE))
    page.evaluate('() => {'+mod.BOOT+'}')
    page.add_script_tag(path=str(base/'src/pw-media-review.js'))
    page.add_script_tag(path=str(base/'src/pw-dialog-hub.js'))
    page.locator('#pw138Cafe .pwd-context button').evaluate('(el)=>el.click()')
    page.wait_for_function("() => document.querySelector('#pwReviewDlg [data-pwr-id]') !== null")
    box=page.evaluate('''() => {let e=document.querySelector('#pwReviewDlg');let b=e.getBoundingClientRect();return {left:b.left,right:b.right,scroll:e.querySelector('.pwr-body').scrollHeight,client:e.querySelector('.pwr-body').clientHeight}}''')
    assert box['left']>=0 and box['right']<=375,box
    assert page.locator('#pwReviewDlg [data-pwr-category="audio"]').is_visible()
    assert page.locator('#pwReviewDlg [data-pwr-load]').is_visible()
    page.screenshot(path=str(base/'dialog-v18-mobile.png'))
    print('PASS mobile:',box)
    browser.close()
