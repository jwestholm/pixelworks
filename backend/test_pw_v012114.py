"""Pixel Works v0.12.11.4: one-time, globally revocable studio authorization."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import pw_v01210 as ext


class StudioConsentTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.p=self.root/'projects'/'test-game'
        self.p.mkdir(parents=True)
        for part in ('work','management','studio-bible'): (self.p/part).mkdir()
        self.srv=SimpleNamespace(ROOT=self.root,path_for=lambda slug:self.p,
              validate_slug=lambda x:x, verify_project=lambda slug:True)

    def test_initial_state_is_not_authorized_and_no_files_created(self):
        with patch.object(ext,'urlopen',side_effect=AssertionError('Unexpected network')):
            self.assertEqual(ext.studio_access(self.srv)['decided'],False)
        self.assertEqual(list(self.root.rglob('*.json')),[])

    def test_allow_persists_across_process_like_reload(self):
        record=ext.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        self.assertTrue(record['enabled']);self.assertTrue(record['decided'])
        self.assertEqual(ext.studio_access(SimpleNamespace(ROOT=self.root))['enabled'],True)
        self.assertTrue(ext._studio_file(self.srv).exists())
        self.assertTrue(str(ext._studio_file(self.srv)).startswith(str(self.root/'secrets')))

    def test_decline_is_remembered_and_revocable(self):
        record=ext.set_studio_access(self.srv,{'enabled':False,'approval':'DISABLE_PIXELWORKS_STUDIO_WORK'})
        self.assertTrue(record['decided']);self.assertFalse(record['enabled'])
        self.assertFalse(ext.studio_access(SimpleNamespace(ROOT=self.root))['enabled'])
        ext.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        self.assertTrue(ext.studio_access(self.srv)['enabled'])
        ext.set_studio_access(self.srv,{'enabled':False,'approval':'DISABLE_PIXELWORKS_STUDIO_WORK'})
        self.assertFalse(ext.studio_access(self.srv)['enabled'])

    def test_requires_real_opt_in_marker(self):
        for payload in ({'enabled':True},{'enabled':1,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'},
                        {'enabled':True,'approval':'RUN_GEMINI_FREE_TIER'},
                        {'enabled':False,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'}):
            with self.assertRaises(ValueError):ext.set_studio_access(self.srv,payload)
        self.assertFalse(ext.studio_access(self.srv)['decided'])

    def test_symlink_secrets_root_is_rejected(self):
        outside=self.root/'outside';outside.mkdir()
        (self.root/'secrets').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError):ext.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})

    def test_inherited_mandate_is_scope_limited(self):
        # Mirrors the installer wrapper: project paths are still validated by the original engine.
        def underlying(slug):
            if slug!='test-game':raise ValueError('Wrong project')
            return {'enabled':True,'scope':'work-only'}
        def middleware(slug):
            underlying(slug)
            state=ext.studio_access(self.srv)
            return {'enabled':state['enabled'],'scope':'pixelworks-projects-only'}
        self.assertFalse(middleware('test-game')['enabled'])
        with self.assertRaises(ValueError):middleware('../other')
        ext.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        self.assertTrue(middleware('test-game')['enabled'])
        ext.set_studio_access(self.srv,{'enabled':False,'approval':'DISABLE_PIXELWORKS_STUDIO_WORK'})
        self.assertFalse(middleware('test-game')['enabled'])

    def test_auto_gemini_cannot_start_without_consent(self):
        with patch.object(ext,'reserve_gemini_call',side_effect=AssertionError('No API reserve')):
            self.assertIsNone(ext.start_auto_job(self.srv,'test-game',{'id':'x'},{'id':'gemini'}))

    def test_does_not_modify_projects_or_gemini_key(self):
        file=self.p/'project.json';file.write_text('{"name":"keep"}')
        token=self.root/'secrets'/'gemini.key';token.parent.mkdir(exist_ok=True)
        token.write_text('not-a-real-token')
        ext.set_studio_access(self.srv,{'enabled':True,'approval':'ALLOW_PIXELWORKS_STUDIO_WORK'})
        self.assertEqual(file.read_text(),'{"name":"keep"}')
        self.assertEqual(token.read_text(),'not-a-real-token')


if __name__=='__main__': unittest.main()
