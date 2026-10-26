"""Pure offline planner regression tests – never start AI or touch real projects."""
import threading,unittest
from types import SimpleNamespace
import pw_v0121115 as patch
import pw_v0121111 as staffplan

def person(id,name,role,provider,allowed,skills):
    return {'id':id,'name':name,'role_type':role,'provider':provider,
            'allowed_stations':allowed,'home_station':allowed[0],
            '_levels':skills,'station':'lead' if role=='lead' else 'cafe'}

class TestParallel(unittest.TestCase):
    def setUp(self):
        self.staff=[person('chef','Chefen','lead','codex',['lead'],{}),
            person('greta','Greta','writer','gemini',['docs','meeting'],{'documentation':5,'meeting':5}),
            person('gunnar','Gunnar','programmer','codex',['code','docs'],{'coding':5,'documentation':2}),
            person('anna','Anna','allround','codex',['code','docs'],{'coding':4,'documentation':3})]
        self.orders=[{'id':'a','station':'docs','status':'waiting','instruction':'Skapa en ny karaktär till spelet','priority':1},
                     {'id':'b','station':'code','status':'waiting','instruction':'Implementera en ny spelmekanik','priority':2}]
        self.jobs=[]
        self.ready=True
        self.srv=SimpleNamespace(LOCK=threading.RLock(),JOBS={},
            staff_read=lambda slug:self.staff,
            orders_read=lambda slug:self.orders,
            get_skill_settings=lambda slug:{p['id']:{k:{'level':v} for k,v in p['_levels'].items()} for p in self.staff},
            agent_authorized=lambda slug,p,station:station in p['allowed_stations'],
            isolated_ready=lambda slug:(self.ready,'Git saknas'))
    def plan(self):
        self.srv.JOBS={str(i):j for i,j in enumerate(self.jobs)}
        return patch.parallel_plan(self.srv,lambda slug:{'leader_active':True,'assignments':[],
                  'active_jobs':list(self.jobs),'blocked':[], 'waiting':len(self.orders)},staffplan,'demo')
    def test_parallel_adviser_and_coder(self):
        self.jobs=[{'agent_id':'greta','provider':'gemini','project':'demo','state':'running'}]
        p=self.plan()
        self.assertEqual([a['agent_name'] for a in p['assignments']],['Gunnar'])
        self.assertEqual(p['assignments'][0]['order_id'],'b')
    def test_adviser_stays_preferred_for_creative_task(self):
        p=self.plan()
        self.assertEqual(len(p['assignments']),1)
        self.assertEqual(p['assignments'][0]['agent_name'],'Gunnar')
        self.assertIn('Greta',p['blocked'][0]['reason'])
    def test_two_coders_can_run_parallel(self):
        self.orders=[{'id':'b','station':'code','status':'waiting','instruction':'Implementera spelmekanik','priority':1},
                     {'id':'c','station':'code','status':'waiting','instruction':'Fixa grafikmotorn','priority':2}]
        p=self.plan()
        self.assertEqual({a['agent_id'] for a in p['assignments']},{'gunnar','anna'})
    def test_second_coder_requires_safe_git(self):
        self.ready=False
        self.jobs=[{'agent_id':'gunnar','provider':'codex','project':'demo','state':'running'}]
        self.orders=[{'id':'c','station':'code','status':'waiting','instruction':'Fixa grafikmotorn','priority':1}]
        p=self.plan()
        self.assertEqual(p['assignments'],[])
        self.assertIn('Git',p['blocked'][0]['reason'])
    def test_busy_best_coder_can_use_free_coder(self):
        self.jobs=[{'agent_id':'gunnar','provider':'codex','project':'demo','state':'running'}]
        self.orders=[{'id':'b','station':'code','status':'waiting','instruction':'Implementera spelmekanik','priority':1}]
        p=self.plan()
        self.assertEqual(p['assignments'][0]['agent_name'],'Anna')
    def test_no_work_without_chief(self):
        p=patch.parallel_plan(self.srv,lambda slug:{'leader_active':False,'assignments':[],
                 'waiting':2},staffplan,'demo')
        self.assertEqual(p['assignments'],[])
    def test_adviser_job_is_read_only_and_non_writing(self):
        from pathlib import Path
        code=(Path(__file__).parent/'pw_v01210.py').read_text()
        self.assertIn("'isolated':True,'advisory_only':True",code)

if __name__=='__main__':unittest.main()
