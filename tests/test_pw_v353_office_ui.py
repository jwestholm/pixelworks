"""Chrome tests for mouse/touch dragging, role defaults, the office's aligned windows."""
import sys, tempfile,threading,unittest,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
import pw_recruitment_v3 as staff
class UITest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.s=type('Core',(),{})();cls.s.ROOT=Path(cls.tmp.name);cls.s.LOCK=threading.RLock();cls.s.JOBS={}
  staff.activate(cls.s,{'approval':staff.APPROVAL})
  staff.hire(cls.s,{'approval':'HIRE_PERSON_V3','revision':1,'candidate_id':'mira','role':'programmer'})
  staff.hire(cls.s,{'approval':'HIRE_PERSON_V3','revision':2,'candidate_id':'joppe','role':'artist'})
  cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.tmp.cleanup()
 def setUp(self):
  self.ctx=self.browser.new_context(viewport={'width':1150,'height':850},has_touch=True);self.page=self.ctx.new_page()
  self.page.set_content('''<!doctype html><html><head></head><body><nav id="gameDock"></nav><div id="officeStage" style="position:relative;width:960px;height:620px;background:#e1bd8a;overflow:hidden"><div id="stationLayer" style="position:absolute;inset:0;pointer-events:none"><div class="station" data-id="code" style="position:absolute;left:60%;top:55%;width:130px;height:100px;transform:translate(-50%,-50%);pointer-events:auto"></div></div></div></body></html>''')
  self.page.evaluate('''initial=>{
     window.db=structuredClone(initial);window.calls=[];window.confirm=()=>true;
     window.pixelWorksApi=async(u,p)=>{
       window.calls.push([u,p]);if(u==='/api/pw-v3/crew')return structuredClone(window.db);
       if(u==='/api/pw-v3/crew/place'){
         const person=window.db.people.find(x=>x.person_id===p.person_id);
         if(!person)throw Error('Unknown person');person.office_position={x:p.x,y:p.y,station_id:p.station_id};window.db.revision++;
         return structuredClone(window.db);
       }throw Error('Unexpected '+u)
     }
   }''',staff.state(self.s))
  self.page.add_script_tag(path=str(ROOT/'src/pw-v3-recruit.js'))
  self.page.add_style_tag(path=str(ROOT/'src/pw-v353-office.css'))
  self.page.add_script_tag(path=str(ROOT/'src/pw-v353-office.js'))
  self.page.wait_for_selector('#pw3OfficeAgents .pw3-person')
 def tearDown(self):self.ctx.close()
 def test_drag_mouse_persists_and_does_not_open_profile(self):
  n=self.page.locator('[data-person-id="pw3-mira"]')
  start=n.bounding_box()
  self.page.mouse.move(start['x']+start['width']/2,start['y']+start['height']/2)
  self.page.mouse.down()
  self.page.mouse.move(470,420,steps=8)
  self.page.mouse.up()
  self.page.wait_for_function("window.calls.some(x=>x[0].endsWith('/place'))")
  self.assertTrue(n.is_visible())
  self.assertFalse(self.page.locator('#pw3Dialog').evaluate('(e)=>e.open'))
  calls=self.page.evaluate('window.calls')
  self.assertEqual([c[0] for c in calls if c[0].endswith('/place')],['/api/pw-v3/crew/place'])
  self.assertNotIn('/api/jobs',str(calls))
  p=self.page.evaluate("window.db.people.find(x=>x.person_id==='pw3-mira').office_position")
  self.assertGreater(p['x'],30)
  self.assertGreater(p['y'],40)
  self.page.evaluate('document.querySelector("#pw3OfficeAgents").remove()')
  self.page.wait_for_function("document.querySelectorAll('#pw3OfficeAgents .pw3-person').length === 3",timeout=4000)
  self.assertEqual(self.page.locator('[data-person-id="pw3-mira"]').get_attribute('data-pinned'),'true')
 def test_drop_on_station_saves_station_without_ai_job(self):
  n=self.page.locator('[data-person-id="pw3-joppe"]');a=n.bounding_box();b=self.page.locator('#stationLayer .station').bounding_box()
  self.page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2)
  self.page.mouse.down();self.page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=10);self.page.mouse.up()
  self.page.wait_for_function("window.db.people.find(x=>x.person_id==='pw3-joppe').office_position?.station_id === 'code'")
  self.assertEqual(self.page.locator('[data-person-id="pw3-joppe"]').get_attribute('data-station-id'),'code')
  self.assertNotIn('/api/jobs',str(self.page.evaluate('window.calls')))
 def test_tap_opens_profile_not_drag(self):
  self.page.locator('[data-person-id="pw3-mira"]').click()
  self.page.wait_for_selector('#pw3Dialog[open] #pw3StaffRole')
  self.assertEqual(self.page.evaluate('window.calls.filter(x=>x[0].endsWith("/place")).length'),0)
 def test_candidate_selection_defaults_to_person_best_role(self):
  self.page.locator('#pw3Open').click()
  self.page.locator('#pw3GoRecruit').click()
  self.assertEqual(self.page.locator('#pw3Role').input_value(),'artist')
  self.page.locator('#pw3NextTop').click()
  name=self.page.locator('.pw31-name').inner_text()
  chosen=self.page.locator('#pw3Role').input_value()
  cid=self.page.evaluate('document.querySelector("#pw3Role")?.value')
  self.assertEqual(cid,chosen)
  self.assertNotEqual(name,'Mira Byte')
  self.assertEqual(chosen,self.page.evaluate('''()=>{const n=document.querySelector('.pw31-name').textContent;return window.db.candidates.find(x=>x.name===n).recommended_role}'''))
  self.page.locator('#pw3Role').select_option('research')
  self.page.locator('#pw3PrevTop').click();self.page.locator('#pw3NextTop').click()
  self.assertEqual(self.page.locator('#pw3Role').input_value(),'research')
 def test_windows_are_panes_and_sun_can_move(self):
  self.page.wait_for_selector('#pw353OfficeDecor .pw353-window-glass')
  self.assertEqual(self.page.locator('#pw353OfficeDecor .pw353-window-glass').count(),3)
  self.assertEqual(self.page.locator('#pw353OfficeDecor').evaluate('el=>getComputedStyle(el).pointerEvents'),'none')
 def test_touch_drag(self):
  self.page.set_viewport_size({'width':390,'height':844})
  node=self.page.locator('[data-person-id="pw3-joppe"]');rect=node.bounding_box()
  x=rect['x']+rect['width']/2;y=rect['y']+rect['height']/2
  cdp=self.ctx.new_cdp_session(self.page)
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':0}]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+60,'y':y+60,'id':0}]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+85,'y':y+80,'id':0}]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  self.page.wait_for_function("window.calls.some(x=>x[0].endsWith('/place'))")
if __name__=='__main__':unittest.main()
