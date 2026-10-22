import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent

class TestBibleStartRegression(unittest.TestCase):
    def test_bible_initialized_before_use(self):
        s=(BASE/'backend/server.py').read_text()
        start=s.index('def run_codex(')
        end=s.index('        if bible.is_file():',start)
        self.assertIn("bible=path_for(slug)/'studio-bible'/'GAME_BIBLE.md'",s[start:end])

    def test_mission_board_gone(self):
        html=(BASE/'index.html').read_text()
        self.assertNotIn('id="taskList"',html)
        self.assertNotIn('Mission Board',html)
        self.assertIn('right-rail',html)

    def test_live_poll_syncs_order_badges(self):
        script=(BASE/'local.js').read_text()
        watch=script.split('async function watchServerJobs(){')[1].split('setTimeout(async()=>{await autoloadLive()')[0]
        self.assertIn('await refreshOrderBadges(slug)',watch)

if __name__=='__main__':unittest.main()
