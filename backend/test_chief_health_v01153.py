import unittest
from unittest.mock import patch
import server

class ChiefHealthTests(unittest.TestCase):
    def base(self,leader=True,waiting=1,assignments=None):
        return {'leader_active':leader,'waiting':waiting,'assignments':assignments if assignments is not None else [],'blocked':[],'active_jobs':[]}
    def check(self,plan,mandate=True,codex=True):
        with patch.object(server,'dispatch_plan',return_value=plan),patch.object(server,'project_mandate',return_value={'enabled':mandate}),patch.object(server,'status',return_value={'execution_enabled':codex}):
            return server.dispatch_health('game-demo')
    def test_no_chief_visible(self):self.assertEqual(self.check(self.base(leader=False))['state'],'no_chief')
    def test_mandate_visible(self):self.assertEqual(self.check(self.base(),mandate=False)['state'],'mandate_required')
    def test_codex_unavailable_visible(self):self.assertEqual(self.check(self.base(),codex=False)['state'],'codex_unavailable')
    def test_idle_visible(self):self.assertEqual(self.check(self.base(waiting=0))['state'],'idle')
    def test_ready_visible(self):self.assertEqual(self.check(self.base(assignments=[{'agent_id':'a'}]))['state'],'ready')
    def test_blocked_visible(self):self.assertEqual(self.check(self.base())['state'],'blocked')
