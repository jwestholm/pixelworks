"""Static regression checks of the UI contract; not a visual browser test."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WizardContract(unittest.TestCase):
 def test_modal_does_not_close_on_backdrop_for_creator(self):
  js=(ROOT/'src/studio.js').read_text()
  self.assertIn('e.target===this.dialog&&!this.creatorActive',js)
  self.assertIn('if(this.creatorActive)e.preventDefault()',js)
 def test_animals_conditional(self):
  js=(ROOT/'src/studio.js').read_text()
  self.assertIn("f.id==='animals'&&(d.creator.characters||[]).includes('Djur')",js)
  self.assertIn('delete d.creator.animals',js)
 def test_guided_conflict_repair(self):
  js=(ROOT/'src/studio.js').read_text()
  self.assertIn('id="removeConflicts"',js)
  self.assertIn('id="editAudience"',js)
 def test_footer_layout(self):
  css=(ROOT/'styles.css').read_text()
  self.assertIn('.creator-dialog .menu-footer{flex-shrink:0',css)
  self.assertIn('overflow:hidden',css)
