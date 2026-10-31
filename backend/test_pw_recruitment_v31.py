"""V3.1 narrative recruitment regression; no external API or project writes."""
import sys,unittest,tempfile,threading,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as v3

class Core:
    def __init__(self,path):
        self.ROOT=Path(path);self.LOCK=threading.RLock();self.JOBS={}

class V31Recruitment(unittest.TestCase):
    def setUp(self):
        self.root=tempfile.TemporaryDirectory();self.addCleanup(self.root.cleanup)
        self.s=Core(self.root.name)
        self.legacy=self.s.ROOT/'projects'/'hackertoolkit'/'management'/'STAFF.json'
        self.legacy.parent.mkdir(parents=True)
        self.legacy.write_bytes(b'OLD STAFF - PLEASE KEEP ME')
    def test_all_six_are_unique_characters_with_complete_bios(self):
        a=v3.state(self.s)
        self.assertEqual(len(a['candidates']),6)
        self.assertEqual(len({c['id'] for c in a['candidates']}),6)
        self.assertEqual(len(a['interview_tasks']),len(a['roles']))
        for p in [v3.CATALOG['chef']]+a['candidates']:
            for k in ('age','gender','pronouns','experience_years','former_job','background','favorite','portrait'):
                self.assertTrue(p[k],(p['id'],k))
            self.assertGreaterEqual(p['age'],18)
            self.assertLessEqual(p['experience_years'],p['age']-16)
            self.assertGreaterEqual(len(p['background']),35)
        self.assertFalse((self.s.ROOT/'studio-v3').exists())
    def test_interview_two_distinct_questions_same_persona_distinct_answers(self):
        v3.activate(self.s,{'approval':v3.APPROVAL})
        a=v3.interview(self.s,{'candidate_id':'mira','role':'artist','test_id':'gorilla','revision':1})
        b=v3.interview(self.s,{'candidate_id':'mira','role':'artist','test_id':'button','revision':2})
        self.assertEqual(a['interview']['source'],'DEMO')
        self.assertIn('gorilla',a['interview']['question'])
        self.assertNotEqual(a['interview']['text'],b['interview']['text'])
        self.assertEqual(b['interview']['test_id'],'button')
        self.assertEqual(v3.state(self.s)['interviews']['mira']['test_id'],'button')
        self.assertEqual(self.legacy.read_bytes(),b'OLD STAFF - PLEASE KEEP ME')
    def test_no_arbitrary_interview_prompts_or_unknown_roles(self):
        v3.activate(self.s,{'approval':v3.APPROVAL})
        for tid in ('../../secrets','execute arbitrary code',123,False):
            with self.assertRaises(ValueError):
                v3.interview(self.s,{'candidate_id':'siv','role':'qa','test_id':tid,'revision':1})
        self.assertEqual(v3.state(self.s)['revision'],1)
    def test_profiles_cannot_mutate_fixed_identity(self):
        v3.activate(self.s,{'approval':v3.APPROVAL})
        d=v3.hire(self.s,{'approval':'HIRE_PERSON_V3','candidate_id':'joppe','role':'qa','revision':1})
        p=d['people'][-1]
        orig=p['character'].copy()
        changed=v3.profile(self.s,{'person_id':p['person_id'],'role':'programmer','work_description':'Gör små ändringar med QA','age':99,'gender':'Annat','background':'OVERRIDE','revision':2})
        self.assertEqual(changed['people'][-1]['character'],orig)
        self.assertEqual(changed['people'][-1]['role'],'programmer')
        self.assertEqual(changed['people'][-1]['work_description'],'Gör små ändringar med QA')
        self.assertEqual(changed['people'][-1]['worker']['id'],p['person_id'])
        self.assertFalse(changed['people'][-1]['engine']['can_execute'])
        self.assertEqual(self.legacy.read_bytes(),b'OLD STAFF - PLEASE KEEP ME')
    def test_no_ai_or_file_actions_during_read(self):
        _=v3.state(self.s)
        self.assertEqual([p.name for p in self.s.ROOT.iterdir()],['projects'])

if __name__=='__main__':unittest.main()
