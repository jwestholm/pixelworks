"""Pixel Works v3.4 Chief UI tests, isolated Chromium, stubbed APIs only."""
import unittest,sys,json,tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'backend'))
import pw_recruitment_v3 as crew
ROOT=Path(__file__).resolve().parent.parent
class Core:
 def __init__(self,folder):self.ROOT=Path(folder);self.LOCK=threading.RLock();self.JOBS={}
class UI(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();s=Core(cls.temp.name)
  crew.activate(s,{'approval':crew.APPROVAL})
  crew.hire(s,{'approval':'HIRE_PERSON_V3','revision':1,'candidate_id':'joppe','role':'programmer'})
  crew.hire(s,{'approval':'HIRE_PERSON_V3','revision':2,'candidate_id':'mira','role':'artist'})
  cls.people=crew.state(s)
  cls.pw=sync_playwright().start()
  cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.temp.cleanup()
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':1200,'height':850})
  self.page=self.context.new_page()
  self.page.set_content('<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><nav id="gameDock"></nav><div id="officeStage"></div></body></html>')
  self.page.evaluate('''data=>{
    window.fixture={people:structuredClone(data),projects:{projects:[{id:'hackertoolkit',name:'Hackertoolkit'},{id:'sjutbanan',name:'Skjutbanan'}]},jobs:{enabled:true,providers:{codex:{available:true,model:'Codex CLI',quota:'okänt'},gemini:{available:true,model:'gemini mock',quota:'okänt'}},jobs:[]}};
    window.calls=[];window.confirm=()=>true;
    window.pixelWorksApi=async(u,d)=>{
      window.calls.push({url:u,data:d===undefined?null:structuredClone(d)});
      if(u==='/api/projects')return window.fixture.projects;
      if(u==='/api/pw-v3/crew')return window.fixture.people;
      if(u==='/api/pw-v3/jobs')return window.fixture.jobs;
      if(u==='/api/pw-v3/chief/recommend'){
        const rank=[{person_id:'pw3-joppe',character_id:'joppe',name:'Joppe Nyström',role_name:'Programmerare',level:4,skill_name:'Kodning',fit:'🌟 Bäst lämpad',reason:'Joppe gillar programmering.',can_start:true,busy:false,blockers:[]},
        {person_id:'pw3-mira',character_id:'mira',name:'Mira Byte',role_name:'Pixelgrafiker',level:1,skill_name:'Kodning',fit:'⚠️ Svag matchning',reason:'Mira passar bättre för konst.',can_start:true,busy:false,blockers:[]}];
        return {schema:1,version:'3.4',project:d.project,category:d.category,provider:d.provider,instruction:d.instruction,engine_available:true,chief_message:'Jag hittade en specialist.',note:'Fiktiva skills, ingen AI körd.',hiring_recommended:d.category==='music',hiring_role:'musician',ranked:rank,available_people:2};
      }
      if(u==='/api/pw-v3/jobs/start'){
        window.fixture.jobs.jobs=[{id:'fa9900dd1201',person_id:d.person_id,name:'Joppe',project:d.project,provider:d.provider,model:'mock',task:d.instruction,state:'review',verified:false,integrated:false,note:'Testresultat',answer:'FIKTIVT RESULTAT'}];
        return {job:window.fixture.jobs.jobs[0]};
      }
      throw Error('unknown endpoint '+u);
    };
  }''',self.people)
  for f in ('pw-v3-recruit.js','pw-v3-jobs.js','pw-v3-chief.js'):self.page.add_script_tag(path=str(ROOT/'src'/f))
 def tearDown(self):self.context.close()
 def recommend(self):
  self.page.locator('#pw34Open').click()
  self.page.locator('#pw34Task').fill('Felsök spelsparning och skriv riktiga tester.')
  self.page.locator('#pw34Suggest').click()
  self.page.locator('[data-pw34-choose="pw3-joppe"]').wait_for()
 def test_chief_flow_to_real_manual_approval(self):
  self.recommend()
  calls=self.page.evaluate('window.calls')
  self.assertEqual(sum(x['url']=='/api/pw-v3/jobs/start' for x in calls),0)
  self.assertEqual(next(x['data']['category'] for x in calls if x['url'].endswith('recommend')),'coding')
  self.page.locator('[data-pw34-choose="pw3-joppe"]').click()
  self.assertTrue(self.page.locator('#pw33Dialog').evaluate('(e)=>e.open'))
  self.assertFalse(self.page.locator('#pw34Dialog').evaluate('(e)=>e.open'))
  self.assertEqual(self.page.locator('#pw33Person').input_value(),'pw3-joppe')
  self.assertEqual(self.page.locator('#pw33Project').input_value(),'hackertoolkit')
  self.assertEqual(self.page.locator('#pw33Instruction').input_value(),'Felsök spelsparning och skriv riktiga tester.')
  self.assertEqual(sum(x['url']=='/api/pw-v3/jobs/start' for x in self.page.evaluate('window.calls')),0)
  self.page.locator('#pw33Start').click()
  self.page.locator('[data-pw33-decision="approve"]').wait_for()
  starts=[x for x in self.page.evaluate('window.calls') if x['url']=='/api/pw-v3/jobs/start']
  self.assertEqual(len(starts),1);self.assertEqual(starts[0]['data']['approval'],'START_V3_REAL_JOB')
 def test_chief_recruiting_and_go_back(self):
  self.recommend()
  self.page.locator('#pw34Category').select_option('music')
  self.page.locator('#pw34Suggest').click()
  self.page.locator('#pw34Hire').wait_for()
  self.page.locator('#pw34Hire').click()
  self.assertFalse(self.page.locator('#pw34Dialog').evaluate('(e)=>e.open'))
  self.assertTrue(self.page.locator('#pw3Dialog').evaluate('(e)=>e.open'))
  self.assertTrue(self.page.get_by_text('Rekrytera (6 kandidater)').count())
 def test_changed_task_discards_stale_recommendation(self):
  self.recommend()
  self.page.locator('#pw34Task').fill('Nytt uppdrag: skriv tydliga tester innan kodändringar.')
  self.assertEqual(self.page.locator('[data-pw34-choose]').count(),0)
  self.page.locator('#pw34Suggest').click()
  self.page.locator('[data-pw34-choose="pw3-joppe"]').wait_for()
 def test_navigation_from_v33_and_escaped_result(self):
  self.page.locator('#pw33Open').click()
  self.page.locator('#pw33ChiefLink').click()
  self.assertTrue(self.page.locator('#pw34Dialog').evaluate('(e)=>e.open'))
  self.page.locator('#pw34Task').fill('<img src=x onerror="window.pwned=1"> Fixa ett fel i spelsparningen')
  self.page.locator('#pw34Suggest').click()
  self.page.locator('.pw34-card').first.wait_for()
  self.assertEqual(self.page.locator('#pw34Dialog img').count(),0)
  self.assertFalse(self.page.evaluate('window.pwned||false'))
 def test_mobile_single_scroll_and_select(self):
  self.page.set_viewport_size({'width':390,'height':750})
  self.recommend()
  self.assertEqual(self.page.locator('#pw34Dialog').evaluate('(d)=>Math.round(d.getBoundingClientRect().width)'),390)
  self.page.locator('[data-pw34-choose="pw3-joppe"]').scroll_into_view_if_needed()
  self.assertTrue(self.page.locator('[data-pw34-choose="pw3-joppe"]').is_enabled())
  self.page.locator('#pw34Close').click()
  self.assertFalse(self.page.locator('#pw34Dialog').evaluate('(e)=>e.open'))
 def test_chief_profile_opens_same_chief_desk(self):
  self.page.evaluate("window.pixelWorksRecruitV3.open('crew')")
  self.page.locator('[data-staff="pw3-chef"]').click()
  self.page.locator('#pw34ProfileChief').click()
  self.assertTrue(self.page.locator('#pw34Dialog').evaluate('(e)=>e.open'))
  self.assertFalse(self.page.locator('#pw3Dialog').evaluate('(e)=>e.open'))
 def test_employee_layer_survives_live_refresh_and_room_repaint(self):
  # Reproduce the reported F5 symptom: people appear, another component then
  # refreshes the room without changing the server-side crew revision.
  self.page.locator('#pw3OfficeAgents [data-person-id]').first.wait_for(timeout=5000)
  people=self.page.locator('#pw3OfficeAgents [data-person-id]')
  self.assertEqual(people.count(),3)
  self.page.evaluate("document.querySelector('#officeStage').replaceChildren()")
  self.assertEqual(self.page.locator('#pw3OfficeAgents [data-person-id]').count(),0)
  self.page.wait_for_function("document.querySelectorAll('#pw3OfficeAgents [data-person-id]').length===3",timeout=4500)
  self.assertEqual(self.page.locator('#pw3-count').inner_text(),'🏢 3 anställda · 1 studio')
  self.page.evaluate("window.dispatchEvent(new Event('pixelworks:v3-office-refresh'))")
  self.assertEqual(self.page.locator('#pw3OfficeAgents [data-person-id]').count(),3)
  self.page.locator('#pw3OfficeAgents [data-person-id="pw3-mira"]').click()
  self.assertTrue(self.page.locator('#pw3Dialog').evaluate('(d)=>d.open'))
 def test_hidden_legacy_agents_are_replaced_by_visible_v3_characters(self):
  self.page.evaluate("document.querySelector('#officeStage').innerHTML='<div id=agentLayer><button class=agent>Gammal agent</button></div>'")
  self.page.wait_for_function("document.body.classList.contains('pw3-active')&&document.querySelectorAll('#pw3OfficeAgents .pw3-person').length===3",timeout=4500)
  self.assertEqual(self.page.locator('#pw3OfficeAgents .pw3-person').count(),3)
  self.assertEqual(self.page.locator('#pw3OfficeAgents .pw3-person[data-character-id="mira"]').count(),1)
  self.assertTrue(self.page.locator('#pw3OfficeAgents').evaluate("e=>getComputedStyle(e).display!=='none'"))
 def test_missing_sprite_still_has_visible_fallback(self):
  self.page.locator('#pw3OfficeAgents .pw3-person').first.wait_for(timeout=5000)
  self.page.wait_for_function("[...document.querySelectorAll('#pw3OfficeAgents .pw3-person')].every(x=>x.classList.contains('pw3-sprite-missing'))",timeout=4000)
  self.assertEqual(self.page.locator('#pw3OfficeAgents .pw3-sprite-missing').count(),3)
  self.assertEqual(self.page.locator('#pw3OfficeAgents .pw3-sprite-missing[data-initial]').count(),3)
 def test_no_write_when_only_suggest(self):
  self.recommend()
  writes=[x for x in self.page.evaluate('window.calls') if x['url']=='/api/pw-v3/jobs/start']
  self.assertEqual(writes,[])
  self.assertIn('Fiktiva',self.page.locator('#pw34Dialog').inner_text())

if __name__=='__main__':unittest.main()
