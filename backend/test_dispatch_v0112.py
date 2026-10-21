import importlib.util
import tempfile
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pw_dispatch',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.previous=(s.ROOT,s.PROJECTS)
        s.ROOT=Path(self.tmp.name);s.PROJECTS=s.ROOT/'projects'
        s.create_project({'slug':'dispatch','name':'Dispatch','idea':'Ett spel för demo','genre':'Pussel','platform':'Webbläsare'})
        self.agent=s.hire_codex('dispatch',{'name':'Testare','approval':'HIRE_CODEX_FOR_PROJECT'})
        self.staff=s.staff_read('dispatch')
        self.agent=next(a for a in self.staff if a['id']==self.agent['id'])
        self.agent.update(work_mode='autonomous',allowed_stations=['qa','code'],home_station='qa')
        s.staff_write('dispatch',self.staff)
        self.order=s.order_action('dispatch',{'station':'qa','instruction':'Undersök buggen i huvudmenyn','priority':1})['item']
    def tearDown(self):
        s.JOBS.clear();s.ROOT,s.PROJECTS=self.previous;self.tmp.cleanup()
    def test_chooses_permitted_agent(self):
        plan=s.dispatch_plan('dispatch')
        self.assertEqual(plan['next']['agent_id'],self.agent['id'])
        self.assertEqual(plan['next']['order_id'],self.order['id'])
        self.assertEqual(s.orders_read('dispatch')[0]['status'],'waiting')
    def test_manual_agent_not_auto_assigned(self):
        staff=s.staff_read('dispatch');staff[-1]['work_mode']='manual';s.staff_write('dispatch',staff)
        self.assertIsNone(s.dispatch_plan('dispatch')['next'])
    def test_specialist_only_home_station(self):
        staff=s.staff_read('dispatch');staff[-1]['work_mode']='specialist';staff[-1]['home_station']='code';s.staff_write('dispatch',staff)
        self.assertIsNone(s.dispatch_plan('dispatch')['next'])
    def test_exclusive_station_respected(self):
        other=s.hire_codex('dispatch',{'name':'Annat team','approval':'HIRE_CODEX_FOR_PROJECT'})
        s.assignment_save('dispatch',{'station':'qa','mode':'exclusive','agent_ids':[other['id']]})
        self.assertIsNone(s.dispatch_plan('dispatch')['next'])
    def test_busy_workspace_not_dispatched(self):
        s.JOBS['other']={'project':'dispatch','state':'running','agent_id':'codex-1'}
        plan=s.dispatch_plan('dispatch')
        self.assertIsNone(plan['next']);self.assertTrue(plan['workspace_busy'])
    def test_priorities_ordered(self):
        earlier=s.order_action('dispatch',{'station':'code','instruction':'Rätta grafiken i startmenyn','priority':2})['item']
        later=s.order_action('dispatch',{'station':'code','instruction':'Rätta kraschen på startsidan','priority':1})['item']
        # same priority is sorted chronologically, so QA P1 first
        self.assertEqual(s.dispatch_plan('dispatch')['next']['order_id'],self.order['id'])
        self.assertEqual(len(s.orders_read('dispatch')),3)

if __name__=='__main__':unittest.main()
