"""The scheduler must come back after a reboot without Docker being available to check it."""
import copy
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_lab as lab


class RestartPolicyTests(unittest.TestCase):
    def setUp(self):
        self.services = yaml.safe_load((ROOT / 'compose.research.yaml').read_text(encoding='utf-8'))['services']

    def test_committed_compose_restarts_scheduler(self):
        lab.validate_restart(self.services)
        self.assertEqual(self.services['prefect']['restart'], 'unless-stopped')
        self.assertEqual(self.services['worker']['restart'], 'unless-stopped')
        self.assertNotIn('restart', self.services['deploy'])

    def test_missing_restart_is_refused(self):
        for name in ('prefect', 'worker'):
            services = copy.deepcopy(self.services)
            del services[name]['restart']
            with self.assertRaisesRegex(ValueError, name):
                lab.validate_restart(services)

    def test_always_is_refused(self):
        # always would also revive a container stopped to hand the origin back.
        services = copy.deepcopy(self.services)
        services['worker']['restart'] = 'always'
        with self.assertRaisesRegex(ValueError, 'worker'):
            lab.validate_restart(services)

    def test_deploy_stays_one_shot(self):
        services = copy.deepcopy(self.services)
        services['deploy']['restart'] = 'unless-stopped'
        with self.assertRaisesRegex(ValueError, 'one-shot'):
            lab.validate_restart(services)
        services['deploy']['restart'] = 'no'
        lab.validate_restart(services)


if __name__ == '__main__':
    unittest.main()
