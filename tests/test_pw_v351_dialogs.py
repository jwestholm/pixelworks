"""Pixel Works 3.5.1 -- real DOM transitions, simulated providers, no AI/network."""
import unittest,sys,tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
import pw_recruitment_v3 as recruitment

class Server:
 def __init__(self,dir):self.ROOT=Path(dir);self.LOCK=threading.RLock();self.JOBS={}

class DialogTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();srv=Server(cls.temp.name)
  recruitment.activate(srv,{'approval':recruitment.APPROVAL})
  recruitment.hire(srv,{'approval':'HIRE_PERSON_V3','revision':1,'candidate_id':'joppe','role':'programmer'})
  recruitment.hire(srv,{'approval':'HIRE_PERSON_V3','revision':2,'candidate_id':'mira','role':'artist'})
  cls.crew=recruitment.state(srv)
  cls.pw=sync_playwright().start()
  cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.temp.cleanup()
 def setUp(self):
  self.ctx=self.browser.new_context(viewport={'width':1150,'height':850});self.page=self.ctx.new_page()
  self.page.set_content((ROOT/'tests'/'pw35-fixture.html').read_text())
  self.page.evaluate('''crew=>{
    window.calls=[];window.confirm=()=>true;
    window.pixelWorksApi=async(u,p)=>{window.calls.push(u);
      if(u==='/api/pw-v3/crew')return structuredClone(crew);
      if(u==='/api/projects')return {projects:[{id:'hackertoolkit',name:'Hackertoolkit'}]};
      if(u==='/api/pw-v3/jobs')return {enabled:true,providers:{codex:{available:true,model:'test',quota:'okänt'},gemini:{available:true,model:'mock',quota:'okänt'}},jobs:[]};
      if(u==='/api/pw-v3/chief/recommend')return {ranked:[],chief_message:'Fiktivt förslag',note:'DEMO',hiring_recommended:false,engine_available:true};
      throw Error('unexpected '+u);
    };
    window.pixelWorksOpenDecisionContext=()=>{const d=document.querySelector('#pwReviewDlg');if(!d.open)d.showModal();return true};
    const d=document.createElement('dialog');d.id='pwReviewDlg';d.innerHTML='<div class="pwr-shell"><header class="pwr-head"><h2>Beslut</h2><button id="reviewExit" type="button">Stäng</button></header><div class="pwr-body"><audio id="reviewAudio" controls></audio><textarea id="reviewText"></textarea></div></div>';document.body.append(d);
    document.querySelector('#reviewExit').onclick=()=>d.close();
  }''',self.crew)
  for fn in ('pw-v3-recruit.js','pw-v3-jobs.js','pw-v3-chief.js'):
   self.page.add_script_tag(path=str(ROOT/'src'/fn))
  self.page.add_style_tag(path=str(ROOT/'src'/'pw-v351-dialogs.css'))
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v351-dialogs.js'))
  self.page.wait_for_function("!!window.pixelWorksGameDialog")
 def tearDown(self):self.ctx.close()
 def open(self):self.page.locator('#pw3Open').click();self.page.locator('#pw3Dialog .pw351-navigation').wait_for()
 def test_single_shared_nav_and_back(self):
  self.open()
  self.assertEqual(self.page.locator('dialog[open]').count(),1)
  self.page.locator('#pw3Dialog [data-pw351-to=chefen]').click()
  self.page.locator('#pw34Dialog .pw351-navigation').wait_for()
  self.assertEqual(self.page.locator('dialog[open]').count(),1)
  self.page.locator('#pw34Dialog [data-pw351-back]').click()
  self.page.locator('#pw3Dialog .pw351-navigation').wait_for()
  self.assertEqual(self.page.locator('dialog[open]').count(),1)
  self.assertTrue(self.page.locator('#pw3Dialog').evaluate('e=>e.open'))
 def test_refresh_does_not_duplicate_nav(self):
  self.open()
  self.page.locator('#pw3Candidates').click()
  self.page.locator('#pw3Team').click()
  self.assertEqual(self.page.locator('#pw3Dialog .pw351-navigation').count(),1)
 def test_jobs_and_chief_same_router(self):
  self.open()
  self.page.locator('#pw3Dialog [data-pw351-to=uppdrag]').click()
  self.page.locator('#pw33Dialog .pw351-navigation').wait_for()
  self.page.locator('#pw33Dialog [data-pw351-to=chefen]').click()
  self.page.locator('#pw34Dialog .pw351-navigation').wait_for()
  self.page.locator('#pw34Dialog [data-pw351-office]').click()
  self.assertEqual(self.page.locator('dialog[open]').count(),0)
  self.assertEqual(self.page.evaluate('pixelWorksGameDialog.history.length'),0)
 def test_review_media_dom_survives_navigation_mount(self):
  self.open()
  self.page.locator('#pw3Dialog [data-pw351-to=beslut]').click()
  self.page.locator('#pwReviewDlg .pw351-navigation').wait_for()
  self.page.locator('#reviewText').fill('Bevara mina anteckningar')
  self.page.evaluate('document.querySelector("#reviewAudio").dataset.probe="original"')
  self.page.wait_for_timeout(350)
  self.assertEqual(self.page.locator('#reviewText').input_value(),'Bevara mina anteckningar')
  self.assertEqual(self.page.locator('#reviewAudio').get_attribute('data-probe'),'original')
  self.assertEqual(self.page.locator('#pwReviewDlg .pw351-navigation').count(),1)
 def test_unsent_job_instruction_on_back(self):
  self.open()
  self.page.locator('#pw3Dialog [data-pw351-to=uppdrag]').click()
  self.page.locator('#pw33Instruction').fill('Skriv tester för det existerande sparflödet men starta ingenting ännu.')
  self.page.locator('#pw33Dialog [data-pw351-to=chefen]').click()
  self.page.locator('#pw34Dialog .pw351-navigation').wait_for()
  self.page.locator('#pw34Dialog [data-pw351-back]').click()
  self.page.wait_for_function("document.querySelector('#pw33Instruction')?.value.includes('Skriv tester')")
  self.assertEqual(sum(x.endswith('/start') for x in self.page.evaluate('calls')),0)
 def test_existing_chief_link_uses_same_router(self):
  self.open()
  self.page.locator('#pw3Dialog [data-pw351-to=uppdrag]').click()
  self.page.locator('#pw33ChiefLink').evaluate('e=>e.click()')
  self.page.locator('#pw34Dialog .pw351-navigation').wait_for()
  self.assertTrue(self.page.locator('#pw34Dialog').evaluate('e=>e.open'))
  self.page.locator('#pw34Dialog [data-pw351-back]').click()
  self.page.locator('#pw33Dialog .pw351-navigation').wait_for()
  self.assertEqual(self.page.locator('dialog[open]').count(),1)
 def test_no_provider_calls_on_navigation(self):
  self.open();self.page.locator('#pw3Dialog [data-pw351-to=uppdrag]').click()
  self.page.locator('#pw33Dialog .pw351-navigation').wait_for()
  self.assertEqual([x for x in self.page.evaluate('calls') if x.endswith(('/start','/decision'))],[])
 def test_unified_skin_and_accessibility(self):
  self.open()
  nav=self.page.locator('#pw3Dialog .pw351-navigation')
  self.assertEqual(nav.get_attribute('aria-label'),'Pixel Works huvudvyer')
  self.assertEqual(nav.locator('[aria-current="page"]').count(),1)
  self.assertEqual(nav.locator('[aria-current="page"]').inner_text(),'👥 Personal')
  bg=nav.evaluate('el=>getComputedStyle(el).backgroundColor')
  self.page.locator('[data-pw351-to=chefen]').click()
  self.page.locator('#pw34Dialog .pw351-navigation').wait_for()
  self.assertEqual(bg,self.page.locator('#pw34Dialog .pw351-navigation').evaluate('el=>getComputedStyle(el).backgroundColor'))
 def test_mobile_touch_size(self):
  self.page.set_viewport_size({'width':390,'height':800});self.open()
  self.assertEqual(self.page.locator('#pw3Dialog').evaluate('e=>Math.round(e.getBoundingClientRect().width)'),390)
  widths=self.page.locator('#pw3Dialog .pw351-menu button').evaluate_all('es=>es.map(e=>e.getBoundingClientRect().width)')
  self.assertTrue(all(x>65 for x in widths),widths)
  self.assertTrue(all(x>=44 for x in self.page.locator('#pw3Dialog .pw351-menu button').evaluate_all('es=>es.map(e=>e.getBoundingClientRect().height)')))
 def test_escape_returns_to_office(self):
  self.open();self.page.keyboard.press('Escape')
  self.page.wait_for_function("!document.querySelector('#pw3Dialog').open")
  self.assertEqual(self.page.locator('dialog[open]').count(),0)
if __name__=='__main__':unittest.main()
