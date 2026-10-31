"""Visual-only v3.5 regression tests. Simulated crew; no AI or external calls."""
import json,unittest,tempfile,threading,sys,struct,zlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
import pw_recruitment_v3 as crew
class FakeServer:
 def __init__(self,folder):self.ROOT=Path(folder);self.LOCK=threading.RLock();self.JOBS={}
class V35Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();s=FakeServer(cls.temp.name)
  crew.activate(s,{'approval':crew.APPROVAL})
  crew.hire(s,{'approval':'HIRE_PERSON_V3','revision':1,'candidate_id':'mira','role':'programmer'})
  crew.hire(s,{'approval':'HIRE_PERSON_V3','revision':2,'candidate_id':'joppe','role':'qa'})
  cls.crew=crew.state(s)
  cls.playwright=sync_playwright().start()
  cls.browser=cls.playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.playwright.stop();cls.temp.cleanup()
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':1200,'height':850})
  self.page=self.context.new_page()
  self.page.set_content((ROOT/'tests'/'pw35-fixture.html').read_text(encoding='utf-8'))
  self.page.add_style_tag(path=str(ROOT/'src'/'pw-v35-world.css'))
  self.page.evaluate('''crew=>{
    window.calls=[];
    window.pixelWorksApi=async(u,d)=>{window.calls.push(u);if(u==='/api/pw-v3/crew')return structuredClone(crew);if(u==='/api/projects')return {projects:[]};if(u==='/api/pw-v3/jobs')return {enabled:true,providers:{},jobs:[]};throw Error('unexpected '+u)};
    window.confirm=()=>true;
  }''',self.crew)
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v3-recruit.js'))
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v3-jobs.js'))
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v3-chief.js'))
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v35-world.js'))
  self.page.wait_for_function("document.querySelectorAll('#pw3OfficeAgents .pw3-person').length===3",timeout=6500)
  self.page.wait_for_function("!!document.querySelector('#pw35-phase-button')")
 def tearDown(self):self.context.close()
 def test_day_night_and_visible_moon(self):
  self.page.evaluate("pixelWorksV35.preview('night')")
  self.assertEqual(self.page.locator('#officeStage').get_attribute('data-pw35-phase'),'night')
  self.assertIn('Natt',self.page.locator('#pw35-phase').inner_text())
  self.page.wait_for_function("parseFloat(getComputedStyle(document.querySelector('.pw35-moon')).opacity)>.95",timeout=3000)
  self.page.evaluate("pixelWorksV35.preview('day')")
  self.assertEqual(self.page.locator('#officeStage').get_attribute('data-pw35-phase'),'day')
  self.page.wait_for_function("parseFloat(getComputedStyle(document.querySelector('.pw35-sun')).opacity)>.95",timeout=3000)
  self.assertEqual(self.page.locator('#pw3OfficeAgents .pw3-person').count(),3)
 def test_clock_controls_and_no_provider_call(self):
  before=self.page.evaluate('window.calls.length')
  self.page.locator('#pw35-phase-button').click()
  self.assertEqual(self.page.evaluate('pixelWorksV35.mode'),'day')
  self.page.locator('#pw35-chatter-button').click()
  self.assertEqual(self.page.locator('#pw35-chatter-button').get_attribute('aria-pressed'),'false')
  self.page.locator('#pw35-motion-button').click()
  self.assertEqual(self.page.locator('#pw35-motion-button').get_attribute('aria-pressed'),'false')
  self.assertTrue(self.page.locator('#officeStage').evaluate("e=>e.classList.contains('pw35-motion-off')"))
  self.assertEqual(self.page.evaluate('window.calls.length'),before)
 def test_personal_sprites_use_character_identity(self):
  mira=self.page.locator('#pw3OfficeAgents [data-character-id=mira]')
  self.assertEqual(mira.count(),1)
  self.page.wait_for_function("!!document.querySelector('[data-character-id=mira][data-pw35-ready=true]')")
  self.assertIn('mira/mira-talk.png',mira.evaluate("e=>e.style.getPropertyValue('--pw35-talk')"))
  self.assertIn('mira/mira-celebrate.png',mira.evaluate("e=>e.style.getPropertyValue('--pw35-celebrate')"))
  self.assertIn('mira/mira-idle.png',mira.evaluate("e=>e.style.getPropertyValue('--pw3-idle')"))
 def test_stage_repaint_restores_light_and_employees(self):
  self.page.evaluate("document.querySelector('#officeStage').replaceChildren()")
  self.page.wait_for_function("document.querySelectorAll('#pw3OfficeAgents .pw3-person').length===3",timeout=5500)
  self.page.wait_for_function("!!document.querySelector('#pw35-atmosphere')",timeout=5500)
  self.page.locator('#pw35-phase-button').click()
  self.assertEqual(self.page.locator('#pw35-clock').count(),1)
 def test_shared_dialog_style_and_return_to_office(self):
  self.page.locator('#pw3Open').click()
  modal=self.page.locator('#pw3Dialog');self.assertTrue(modal.evaluate('e=>e.open'))
  bg=modal.evaluate('e=>getComputedStyle(e).backgroundColor')
  self.assertIn('255, 244, 220',bg)
  modal.locator('.pw3-head button').first.click()
  self.assertFalse(modal.evaluate('e=>e.open'))
  self.page.locator('#pw34Open').click()
  self.assertTrue(self.page.locator('#pw34Dialog').evaluate('e=>e.open'))
  self.assertEqual(self.page.locator('#pw34Dialog').evaluate('e=>getComputedStyle(e).backgroundColor'),bg)
 def test_mobile_clock_and_modal(self):
  self.page.set_viewport_size({'width':390,'height':770})
  self.page.locator('#pw3Open').click()
  self.assertEqual(self.page.locator('#pw3Dialog').evaluate('e=>Math.round(e.getBoundingClientRect().width)'),390)
  self.assertGreaterEqual(self.page.locator('#pw3Dialog button').first.evaluate('e=>Math.round(e.getBoundingClientRect().height)'),44)
 def test_reduced_motion_off(self):
  self.page.emulate_media(reduced_motion='reduce')
  self.page.evaluate("pixelWorksV35.preview('night')")
  self.assertEqual(self.page.locator('#officeStage').get_attribute('data-pw35-phase'),'night')
  self.assertEqual(self.page.locator('.pw35-clouds').evaluate('e=>getComputedStyle(e).animationName'),'none')
 def test_transparent_sheets_and_distinct_faces(self):
  sheets=set()
  for name in ('chef','joppe','siv','nisse','mira','vera','lova'):
   for kind in ('talk','celebrate'):
    buf=(ROOT/'assets'/'characters'/name/(name+'-'+kind+'.png')).read_bytes()
    self.assertEqual(buf[:8],b'\x89PNG\r\n\x1a\n')
    self.assertEqual(struct.unpack('>II',buf[16:24]),(192,68))
    self.assertEqual(buf[25],6) # PNG RGBA, transparent-background capable
    raw=b'';pos=8
    while pos<len(buf):
     length=struct.unpack('>I',buf[pos:pos+4])[0];name4=buf[pos+4:pos+8]
     if name4==b'IDAT':raw+=buf[pos+8:pos+8+length]
     pos+=12+length
    self.assertEqual(zlib.decompress(raw)[4],0) # alpha at pixel (0,0), regardless of row filter
   sheets.add((ROOT/'assets'/'characters'/name/(name+'-talk.png')).read_bytes())
  self.assertEqual(len(sheets),7)
if __name__=='__main__':unittest.main()
