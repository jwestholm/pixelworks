import unittest
from pathlib import Path

class ManualDispatchContract(unittest.TestCase):
    def test_manual_queue_can_use_dispatch_without_placed_agent(self):
        js=Path(__file__).resolve().parent.parent.joinpath('local.js').read_text()
        launch=js.split('async function launchOrder(slug,order){',1)[1].split('async function startQueue(',1)[0]
        self.assertIn("'/dispatch'", launch)
        self.assertIn('assigned.agent_id',launch)
        self.assertIn('isolated:true',launch)
        self.assertNotIn('Placera exakt en behörig',launch)

if __name__=='__main__': unittest.main()
