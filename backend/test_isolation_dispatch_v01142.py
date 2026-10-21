import unittest
from pathlib import Path

class IsolationDispatchContract(unittest.TestCase):
 def test_browser_dispatch_always_requests_isolation(self):
  js=(Path(__file__).parents[1]/'local.js').read_text()
  start=js.index('async function runStudioAuto(')
  end=js.index('async function studioAutoControls(',start)
  dispatch=js[start:end]
  self.assertIn('isolated:true,approval:',dispatch)
  self.assertNotIn('isolated:!!plan.parallel_ready',dispatch)
  self.assertIn('if(!plan.parallel_ready)',dispatch)
 def test_server_rejects_nonisolated_concurrent_job_before_registration(self):
  py=(Path(__file__).parent/'server.py').read_text()
  self.assertLess(py.index("if active and payload.get('isolated') is not True:"),py.index("jid=uuid.uuid4().hex[:12]",py.index('if active and payload.get(\'isolated\') is not True:')-500))
if __name__=='__main__': unittest.main()
