"""Chromium UX regression for v3.3; fake API, no provider network or cost."""
import json,sys,tempfile,threading,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'backend'))
import pw_recruitment_v3 as crew

ROOT=Path(__file__).resolve().parent.parent

class Core:
 def __init__(self,root):self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={}

class UI(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();core=Core(cls.temp.name)
  crew.activate(core,{'approval':crew.APPROVAL})
  crew.hire(core,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'programmer','revision':1})
  crew.hire(core,{'approval':'HIRE_PERSON_V3','candidate_id':'mira','role':'artist','revision':2})
  cls.crew=crew.state(core)
  cls.state={'enabled':True,'providers':{'gemini':{'available':True,'model':'gemini-test-model','quota':'okänt'},
                                        'codex':{'available':True,'model':'Codex CLI','quota':'okänt'}},'jobs':[]}
  cls.projects={'projects':[{'id':'hackertoolkit','name':'Hackertoolkit'},{'id':'sjutbanan','name':'Skjutbanan'}]}
  cls.pw=sync_playwright().start()
  cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.temp.cleanup()
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':1100,'height':880})
  self.page=self.context.new_page()
  self.page.set_content('<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><nav id="gameDock"></nav><div id="officeStage" style="position:relative;width:950px;height:600px"></div></body></html>')
  initial={'crew':self.crew,'projects':self.projects,'state':self.state}
  self.page.evaluate('''fixtures=>{
   window.fixture=structuredClone(fixtures);window.sent=[];window.confirm=()=>true;window.prompt=()=>"Gör texten roligare";
   window.pixelWorksApi=async(url,data)=>{
    if(data)window.sent.push({url,payload:structuredClone(data)});
    if(url==='/api/pw-v3/crew')return window.fixture.crew;
    if(url==='/api/projects')return window.fixture.projects;
    if(url==='/api/pw-v3/jobs')return window.fixture.state;
    if(url==='/api/pw-v3/jobs/start'){
      const person=window.fixture.crew.people.find(p=>p.person_id===data.person_id);
      window.fixture.state.jobs.unshift({id:'abcdef123456',person_id:person.person_id,name:person.name,project:data.project,
        provider:data.provider,model:'mock',task:data.instruction,source:'provider_reported',verified:false,integrated:false,
        state:'review',answer:'TEST-DUBBELSVAR, ej verifierat',note:'Inväntar beslut'});
      return {job:{id:'abcdef123456',state:'queued'}};
    }
    if(url==='/api/pw-v3/jobs/decision'){
       const j=window.fixture.state.jobs[0];j.state=data.action==='approve'?'done':data.action==='reject'?'rejected':'review';
       return {message:'Beslut sparat',job:j};
    }
    throw Error('Unexpected API: '+url);
   };
  }''',initial)
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v3-recruit.js'))
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v3-jobs.js'))
 def tearDown(self):self.context.close()
 def test_manual_start_and_review(self):
  self.page.locator('#pw33Open').click()
  self.page.locator('#pw33Person').select_option('pw3-joppe')
  self.page.locator('#pw33Provider').select_option('gemini')
  self.page.locator('#pw33Project').select_option('sjutbanan')
  self.assertIn('Joppe',self.page.locator('.pw33-summary').first.inner_text())
  self.assertEqual(self.page.evaluate('window.sent.length'),0)
  self.page.locator('#pw33Instruction').fill('Skriv en liten berättelse om ett hackarspel med humor.')
  self.page.locator('#pw33Start').click()
  self.page.locator('[data-pw33-decision="approve"]').wait_for(timeout=5000)
  sent=self.page.evaluate('window.sent')
  self.assertEqual(len(sent),1)
  self.assertEqual(sent[0]['payload']['person_id'],'pw3-joppe')
  self.assertEqual(sent[0]['payload']['project'],'sjutbanan')
  self.assertEqual(sent[0]['payload']['provider'],'gemini')
  self.assertEqual(sent[0]['payload']['approval'],'START_V3_REAL_JOB')
  self.assertIn('Inte oberoende verifierad',self.page.locator('.pw33-job').inner_text())
  self.page.locator('[data-pw33-decision="approve"]').click()
  self.page.get_by_text('Beslut sparat').wait_for()
  sent=self.page.evaluate('window.sent')
  self.assertEqual(sent[1]['payload']['approval'],'PLAYER_V3_REVIEW_DECISION')
  self.assertEqual(sent[1]['payload']['action'],'approve')
  self.assertFalse(self.page.locator('[data-pw33-decision="approve"]').count())
 def test_profile_deeplink_and_modal_close(self):
  self.page.evaluate("window.pixelWorksRecruitV3.open('crew')")
  self.page.locator('#pw3Dialog').wait_for(state='visible')
  self.page.locator('[data-staff="pw3-mira"]').click()
  self.page.locator('#pw33ProfileStart').click()
  self.assertFalse(self.page.locator('#pw3Dialog').evaluate('(e)=>e.open'))
  self.assertTrue(self.page.locator('#pw33Dialog').evaluate('(e)=>e.open'))
  self.assertEqual(self.page.locator('#pw33Person').input_value(),'pw3-mira')
  self.page.locator('#pw33Close').click()
  self.assertFalse(self.page.locator('#pw33Dialog').evaluate('(e)=>e.open'))
 def test_team_card_direct_start(self):
  self.page.evaluate("window.pixelWorksRecruitV3.open('crew')")
  self.page.locator('[data-pw33-assign="pw3-joppe"]').click()
  self.assertTrue(self.page.locator('#pw33Dialog').evaluate('(e)=>e.open'))
  self.assertEqual(self.page.locator('#pw33Person').input_value(),'pw3-joppe')
 def test_mobile_scrolling_and_buttons(self):
  self.page.set_viewport_size({'width':390,'height':750})
  self.page.locator('#pw33Open').click()
  self.assertEqual(self.page.locator('#pw33Dialog').evaluate('(e)=>Math.round(e.getBoundingClientRect().width)'),390)
  self.assertTrue(self.page.locator('#pw33Start').is_visible())
  self.page.locator('#pw33Provider').select_option('gemini')
  self.page.locator('#pw33Instruction').fill('Skriv en ordentlig men rolig saga med två hjältar.')
  self.page.locator('#pw33Start').scroll_into_view_if_needed()
  self.page.locator('#pw33Start').click()
  self.page.locator('[data-pw33-decision="later"]').wait_for()
  self.page.locator('[data-pw33-decision="later"]').click()
  self.page.get_by_text('Beslut sparat').wait_for()
 def test_persona_style_untrusted_answer_escaped(self):
  self.page.evaluate('''()=>window.fixture.state.jobs=[{id:'deadbeef1234',person_id:'pw3-mira',name:'Mira',
  project:'hackertoolkit',provider:'gemini',state:'review',model:'mock',task:'Arbeta',verified:false,
  integrated:false,answer:'<img src=x onerror=alert(1)>',note:'Behöver granskning'}]''')
  self.page.locator('#pw33Open').click()
  self.page.locator('#pw33JobsTab').click()
  self.page.locator('.pw33-job details').first.click()
  self.assertIn('<img src=x',self.page.locator('.pw33-result').inner_text())
  self.assertEqual(self.page.locator('.pw33-job img').count(),0)

if __name__=='__main__':unittest.main()
