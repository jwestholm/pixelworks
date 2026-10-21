import importlib.util
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('pw_creator',Path(__file__).with_name('server.py'))
s=importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class CreatorTests(unittest.TestCase):
    def test_creator_saved_with_animals_and_custom_categories(self):
        with tempfile.TemporaryDirectory() as td:
            old_root,old_projects=s.ROOT,s.PROJECTS
            try:
                s.ROOT=Path(td)/'.pixelworks';s.PROJECTS=s.ROOT/'projects'
                result=s.create_project({'slug':'piratgris','name':'Piratgris','idea':'Pussel på havet','genre':'Spel', 'platform':'Webbläsare','priority':'Spelkänsla','creator':{'gameGenre':['Pussel'],'themes':['Pirater'],'animals':['Gris','Bläckfisk','Flygande sjögris'],'animalRoles':['Huvudfigur'],'visualStyle':['Pixelart 16-bit']},'weights':{'Gameplay':5,'Ljud':2},'areas':['Grafik']})
                project=s.PROJECTS/'piratgris';bible=(project/'studio-bible/GAME_BIBLE.md').read_text()
                self.assertTrue(result['verified'])
                self.assertIn('Flygande sjögris',bible)
                self.assertIn('Gameplay: 5/5',bible)
                self.assertTrue((project/'management/FIRST_BIBLE_TASK.md').exists())
            finally:s.ROOT,s.PROJECTS=old_root,old_projects
    def test_reject_nonlist_creator(self):
        with tempfile.TemporaryDirectory() as td:
            old_root,old_projects=s.ROOT,s.PROJECTS
            try:
                s.ROOT=Path(td)/'.pixelworks';s.PROJECTS=s.ROOT/'projects'
                with self.assertRaises(ValueError):s.create_project({'slug':'test-project','name':'Test','idea':'Test','creator':{'animals':'gris'}})
            finally:s.ROOT,s.PROJECTS=old_root,old_projects
if __name__=='__main__':unittest.main()
