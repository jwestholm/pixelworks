"""Pixel Works 3.5.2 - browser checks with simulated people and zero AI calls."""
import sys, tempfile, threading, unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
import pw_recruitment_v3 as staff

class PersonnelUITests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();srv=type('Fake',(),{})();srv.ROOT=Path(cls.temp.name);srv.LOCK=threading.RLock();srv.JOBS={}
  staff.activate(srv,{'approval':staff.APPROVAL})
  staff.hire(srv,{'approval':'HIRE_PERSON_V3','revision':1,'candidate_id':'mira','role':'programmer'})
  staff.hire(srv,{'approval':'HIRE_PERSON_V3','revision':2,'candidate_id':'joppe','role':'artist'})
  cls.crew=staff.state(srv)
  cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.temp.cleanup()
 def setUp(self):
  self.ctx=self.browser.new_context(viewport={'width':1150,'height':850});self.page=self.ctx.new_page()
  self.page.set_content('<!doctype html><html><head></head><body><nav id="gameDock"></nav><div id="officeStage" style="position:relative;height:500px"></div></body></html>')
  self.page.evaluate('''crew=>{window.calls=[];window.pixelWorksApi=async(u,p)=>{window.calls.push([u,p]);if(u==='/api/pw-v3/crew')return structuredClone(crew);throw Error('No API call '+u)};window.confirm=()=>true;}''',self.crew)
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v3-recruit.js'))
  self.page.add_style_tag(path=str(ROOT/'src'/'pw-v352-personnel.css'))
  self.page.locator('#pw3Open').click();self.page.locator('.pw352-team-grid').wait_for()
 def tearDown(self):self.ctx.close()
 def test_unique_team_cards_and_roles(self):
  self.assertEqual(self.page.locator('.pw352-person-card').count(),3)
  self.assertEqual(self.page.locator('.pw352-person-card[data-person-id="pw3-chef"]').count(),1)
  mira=self.page.locator('.pw352-person-card[data-person-id="pw3-mira"]')
  self.assertEqual(mira.count(),1)
  self.assertIn('Pixelgrafiker',mira.locator('.pw352-best').inner_text())
  self.assertIn('Programmerare',mira.locator('.pw352-kicker').first.inner_text())
  self.assertNotIn('pw3-',mira.inner_text())
  self.assertGreater(self.page.locator('.pw352-avatar svg').count(),0)
 def test_profile_critical_controls_still_present(self):
  self.page.locator('[data-staff="pw3-mira"]').click()
  self.assertEqual(self.page.locator('#pw3StaffRole').input_value(),'programmer')
  self.page.locator('#pw3WorkDescription').fill('Skriv alltid testresultat och kontrollera varje bild.')
  self.assertTrue(self.page.locator('#pw3SaveStaff').is_visible())
  self.assertTrue(self.page.locator('#pw33ProfileStart').is_visible())
  self.assertIn('Mira',self.page.locator('.pw352-profile-hero').inner_text())
  self.page.locator('#pw3Back').click();self.assertEqual(self.page.locator('.pw352-person-card').count(),3)
 def test_mobile_single_scroll(self):
  self.page.set_viewport_size({'width':390,'height':844})
  self.assertEqual(self.page.locator('.pw352-team-grid').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length'),1)
  bounds=self.page.locator('#pw3Dialog').bounding_box()
  self.assertLessEqual(bounds['width'],390)
  self.assertEqual(self.page.locator('#pw3Dialog').evaluate('el=>getComputedStyle(el).overflowY'),'auto')
 def test_one_return_to_office_in_shared_nav(self):
  # The navigation layer is also present in the installed game (V3.5.1).
  self.page.add_style_tag(path=str(ROOT/'src'/'pw-v351-dialogs.css'))
  self.page.add_script_tag(path=str(ROOT/'src'/'pw-v351-dialogs.js'))
  self.page.wait_for_function("!!document.querySelector('#pw3Dialog .pw351-navigation')")
  self.assertTrue(self.page.locator('#pw3Dialog .pw351-home').is_hidden())
  self.assertTrue(self.page.locator('#pw3Dialog .pw351-back').is_visible())

 def test_open_does_not_start_ai(self):
  calls=self.page.evaluate('window.calls');self.assertEqual({x[0] for x in calls},{'/api/pw-v3/crew'})
 def test_recruitment_still_works(self):
  self.page.locator('#pw3GoRecruit').click()
  self.assertTrue(self.page.locator('#pw3Hire').is_visible())
  self.assertTrue(self.page.locator('#pw3Interview').is_visible())
  self.page.locator('#pw3Team').click();self.assertEqual(self.page.locator('.pw352-person-card').count(),3)

if __name__=='__main__':unittest.main()
