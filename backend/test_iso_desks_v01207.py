"""Regression tests for v0.12.0.7 isometric station sprites (stdlib only)."""
import struct
import unittest
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'office-v2'
TYPES = ('lead','code','qa','research','art','docs','voice','music','meeting','cafe')

class IsometricFurnitureTest(unittest.TestCase):
    def test_ten_independent_rgba_pngs(self):
        hashes = []
        for typ in TYPES:
            with self.subTest(typ=typ):
                contents = (ASSETS / ('desk-'+typ+'.png')).read_bytes()
                self.assertTrue(contents.startswith(b'\x89PNG\r\n\x1a\n'))
                width,height,depth,colortype = struct.unpack('>IIBB', contents[16:26])
                self.assertEqual((width,height), (320,248))
                self.assertEqual((depth,colortype), (8,6)) # 8-bit RGBA; transparent cutouts
                self.assertGreater(len(contents), 1000)
                hashes.append(__import__('hashlib').sha256(contents).hexdigest())
        self.assertEqual(len(set(hashes)),len(TYPES), 'workstations must not be duplicate sprites')

    def test_css_can_address_each_desks_sprite(self):
        css=(ASSETS.parent.parent / 'visual-v2.css').read_text()
        for typ in TYPES:
            self.assertIn('desk-'+typ+'.png', css)

if __name__=='__main__': unittest.main()
