"""The research service and the original service must never hold the shared origin at the same time."""
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_lab as lab

PORTS = [3010, 8010, 4201, 3015]


class ExclusionTests(unittest.TestCase):
    def test_original_service_running_is_refused(self):
        containers = {'industryflow-web-1': ('industryflow', {3010}), 'industryflow-db-1': ('industryflow', set())}
        conflicts = lab.exclusion_conflicts(containers, {3010}, PORTS)
        self.assertIn('Original service still running: industryflow-db-1, industryflow-web-1', conflicts)
        self.assertIn('Port 3010 occupied by industryflow-web-1', conflicts)

    def test_port_held_by_another_program_is_refused(self):
        containers = {'valuflow-api-1': ('valuflow', {8000})}
        conflicts = lab.exclusion_conflicts(containers, {8010}, PORTS)
        self.assertEqual(conflicts, ['Port 8010 occupied by a non-Docker process'])

    def test_ports_held_by_own_project_are_allowed(self):
        containers = {'industryflow-research-web-1': ('industryflow-research', {3010}),
                      'industryflow-research-api-1': ('industryflow-research', {8010}),
                      'industryflow-research-drill-web-1': ('industryflow-research-drill', {3016})}
        self.assertEqual(lab.exclusion_conflicts(containers, {3010, 8010, 3016}, PORTS), [])

    def test_drill_project_is_not_mistaken_for_the_original(self):
        containers = {'industryflow-research-drill-db-1': ('industryflow-research-drill', set())}
        self.assertEqual(lab.exclusion_conflicts(containers, set(), PORTS), [])

    def test_docker_ps_ports_are_parsed(self):
        output = ('industryflow-web-1\tindustryflow\t127.0.0.1:3010->3010/tcp\n'
                  'industryflow-research-api-1\tindustryflow-research\t0.0.0.0:8010->8000/tcp, [::]:8010->8000/tcp\n'
                  'industryflow-research-db-1\tindustryflow-research\t5432/tcp\n')
        with mock.patch.object(lab, 'run', return_value=output):
            self.assertEqual(lab.running_containers(), {
                'industryflow-web-1': ('industryflow', {3010}),
                'industryflow-research-api-1': ('industryflow-research', {8010}),
                'industryflow-research-db-1': ('industryflow-research', set())})


if __name__ == '__main__':
    unittest.main()
