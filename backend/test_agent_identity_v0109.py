import unittest
from pathlib import Path
from unittest.mock import patch
import server

class AgentIdentityTests(unittest.TestCase):
    def test_report_includes_staff_identity(self):
        job={'id':'aaaaaaaaaaaa','project':'game','agent_id':'codex-2','agent_name':'Programmerarn','station':'code','order_id':'order001','state':'done','events':[], 'exit_code':0}
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with patch.object(server,'report_path',return_value=Path(d)/'aaaaaaaaaaaa.json'), patch.object(server,'validate_slug',return_value='game'):
                report=server.make_report(job)
        self.assertEqual(report['agent_id'],'codex-2')
        self.assertEqual(report['agent_name'],'Programmerarn')
        self.assertEqual(report['order_id'],'order001')
        self.assertIn('Programmerarn',report['title'])

    def test_agent_views_filter_by_employee(self):
        root=Path(__file__).resolve().parents[1]
        local=(root/'local.js').read_text()
        ui=(root/'src/ui.js').read_text()
        studio=(root/'src/studio.js').read_text()
        self.assertIn('j.agent_id===agentId',local)
        self.assertIn('this.model.activeProjectId,agent.id',ui)
        self.assertIn('this.model.activeProjectId,id',studio)
        self.assertIn("result.agent_name||'Okänd anställd'",local)

    def test_order_badges_and_log_title(self):
        local=(Path(__file__).resolve().parents[1]/'local.js').read_text()
        self.assertIn('station-order-badge',local)
        self.assertIn("o.status==='waiting'",local)
        self.assertIn('📜 AKTIVITETSLOGG',local)

if __name__=='__main__': unittest.main()
