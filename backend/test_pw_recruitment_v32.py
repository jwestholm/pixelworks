"""V3.2 – fixed persona settings, role fit and character-atlas contract.
Never calls a real AI provider or writes into legacy projects."""
import sys, tempfile, threading, unittest
from pathlib import Path
import struct
sys.path.insert(0,str(Path(__file__).parent))
import pw_recruitment_v3 as v3

class Core:
    def __init__(self,root):self.ROOT=Path(root);self.LOCK=threading.RLock();self.JOBS={}

class Contract(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.core=Core(tmp.name)
    def test_role_fit_visible_and_is_game_score(self):
        state=v3.state(self.core)
        self.assertFalse(state['enabled'])
        for c in state['candidates']:
            rank=c['role_recommendations']
            self.assertEqual(len(rank),7)
            self.assertEqual(rank[0]['role'],c['recommended_role'])
            self.assertGreaterEqual(rank[0]['score'],3)
            self.assertEqual(c['persona_config']['status'][:9],'FÖRBEREDD')
            for tag in ('career_highlight','office_rumour','office_habit','speech_sample'):
                self.assertGreater(len(c[tag]),12,(c['id'],tag))
        mira=next(x for x in state['candidates'] if x['id']=='mira')
        self.assertEqual(mira['role_recommendations'][0]['score'],5)
    def test_persona_immutable_and_company_role_editable(self):
        v3.activate(self.core,{'approval':v3.APPROVAL})
        created=v3.hire(self.core,{'approval':'HIRE_PERSON_V3','candidate_id':'mira','role':'programmer','revision':1})
        p=created['people'][-1]
        original=p['persona_config']['traits']
        prompt=p['prompt_preview'];self.assertIn('FÖRETAGETS ROLL: Programmerare',prompt)
        changed=v3.profile(self.core,{'person_id':p['person_id'],'role':'artist', 'work_description':'Visa två paletter för beslut.','revision':2,
                                      'traits':{'careful':1},'character_id':'joppe'})
        new=changed['people'][-1]
        self.assertEqual(new['persona_config']['traits'],original)
        self.assertEqual(new['character_id'],'mira')
        self.assertEqual(new['role'],'artist')
        self.assertIn('Visa två paletter för beslut.',new['prompt_preview'])
        self.assertIn('FÖRETAGETS ROLL: Pixelgrafiker',new['prompt_preview'])
        self.assertFalse(new['engine']['can_execute'])
        self.assertEqual(new['worker']['id'],'pw3-mira')
    def test_28_sprite_pngs_rgba_and_different_identities(self):
        root=Path(__file__).resolve().parent.parent/'assets'/'characters'
        hashes=set()
        for person in ['chef','joppe','siv','nisse','mira','vera','lova']:
            for mode in ['idle','walk','working','cafe']:
                path=root/person/(person+'-'+mode+'.png')
                raw=path.read_bytes()
                self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack('>II',raw[16:24]),(192,68))
                self.assertEqual(raw[25],6)  # RGBA, alpha channel present
            hashes.add((root/person/(person+'-idle.png')).read_bytes())
        self.assertEqual(len(hashes),7)

if __name__=='__main__': unittest.main()
