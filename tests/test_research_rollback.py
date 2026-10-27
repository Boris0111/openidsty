"""rollback --to <seq>: no initialize, refused across contract migrations or a Prefect change (design D7)."""
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import lab, deployment_dir, deploy_record, services, OLD, NEW, CHAIN  # noqa: E402

SMOKE_OK = {'health': {'ok': True}}


class RollbackHarness(unittest.TestCase):
    db_version = '0018'

    def setUp(self):
        self.root = deployment_dir(self)
        # seq 1: OLD at 0017; seq 2: NEW adds the expand-only 0018 and is serving.
        self.previous = lab.append_record(deploy_record(OLD))
        self.current = lab.append_record(deploy_record(NEW, chain=[*CHAIN, '0018']))
        self.calls, self.running, self.busy = [], services(self.current), []
        self.head, self.built, self.smoke = NEW, [], (True, SMOKE_OK)
        fakes = {'guard_problems': lambda **kw: self.log('guard', kw) or [],
                 'running_services': lambda project: self.running,
                 'alembic_version': lambda container: self.db_version,
                 'prefect_runs': lambda: self.busy,
                 'validate': lambda tag: {},
                 'backup': lambda secondary, **kw: self.log('backup', kw) or {'backup': '/b/20261028T020000Z'},
                 'build_images': lambda commit: self.log('build', commit) or (commit[:12], self.built),
                 'image_ids': lambda tag: {'api': 'sha256:api-' + tag[:4], 'web': 'sha256:web-' + tag[:4]},
                 'compose': self.compose, 'run': self.fake_run, 'git_head': lambda: self.head,
                 'smoke_checks': lambda *a, **kw: self.log('smoke', a[3], a[4]) or self.smoke}
        for name, fake in fakes.items():
            patcher = mock.patch.object(lab, name, side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def log(self, *entry):
        self.calls.append(entry)

    def compose(self, *args, tag, input=None):
        self.calls.append(('compose', tag, *args))
        return b''

    def fake_run(self, args, **kwargs):
        if args[:2] == ['git', 'checkout']:
            self.head = args[-1]
            self.calls.append(('checkout', args[-1]))
            return b''
        raise AssertionError(f'unexpected command {args}')

    def composed(self):
        return [c[2:] for c in self.calls if c[0] == 'compose']


class RefusalTests(RollbackHarness):
    def assert_refused(self, seq, pattern):
        before = lab.read_ledger()
        with self.assertRaisesRegex(lab.Refused, pattern):
            lab.rollback(seq)
        self.assertFalse([c for c in self.calls if c[0] in ('backup', 'build', 'compose', 'checkout')])
        self.assertEqual(lab.read_ledger(), before, 'a refusal is not recorded')

    def test_missing_or_failed_target(self):
        self.assert_refused(9, 'record 9 is not a successful deploy or rollback')
        lab.append_record(deploy_record('c' * 40, outcome='failed', replaced=False))
        self.assert_refused(3, 'record 3 is not a successful')

    def test_adopt_record_is_not_a_target(self):
        lab.LEDGER.unlink()
        lab.append_record({'kind': 'adopt', 'outcome': 'succeeded', 'replaced': True, 'commit': OLD, 'tag': lab.PRE_LEDGER,
                           'images': {}, 'services': {}})
        lab.append_record(self.current)
        self.assert_refused(1, 'record 1 is not a successful deploy or rollback')

    def test_target_newer_than_the_database(self):
        self.db_version = '0016'
        self.assert_refused(1, 'expects schema 0017, newer than the database at 0016')

    def test_contract_between_target_and_database(self):
        lab.LEDGER.unlink()
        lab.append_record(deploy_record(OLD))
        lab.append_record(deploy_record(NEW, chain=[*CHAIN, '0018'], contracts=('0009', '0017', '0018'),
                                        contract_boundary=True, backup='20261027T120000Z'))
        self.assert_refused(1, r'crosses contract migration\(s\) 0018; restore the rollback-boundary backup 20261027T120000Z')

    def test_contract_known_only_to_the_newer_record(self):
        # The older commit cannot see 0018; only the union of recorded chains shows it is a contract.
        self.assertEqual(lab.chain_union([self.previous, deploy_record(NEW, chain=[*CHAIN, '0018'], contracts=['0018'])]),
                         ([*CHAIN, '0018'], {'0009', '0017', '0018'}))

    def test_prefect_version_differs(self):
        lab.LEDGER.unlink()
        lab.append_record(deploy_record(OLD, prefect='3.8.7'))
        lab.append_record(self.current)
        self.assert_refused(1, 'Prefect would change from 3.8.8 to 3.8.7')

    def test_busy_prefect(self):
        self.running = services(self.current, scheduler=True)
        self.busy = ['publish-run']
        self.assert_refused(1, 'pending or running flow run')

    def test_disagreeing_chains(self):
        lab.LEDGER.unlink()
        lab.append_record(deploy_record(OLD))
        lab.append_record(deploy_record(NEW, chain=[*CHAIN[:-1], '0099']))
        self.db_version = '0099'
        self.assert_refused(1, 'merged migration was rewritten')


class SuccessTests(RollbackHarness):
    def test_no_initialize_and_up_no_deps(self):
        record = lab.rollback(1)
        self.assertFalse(any('initialize' in step for step in self.composed()))
        self.assertEqual(self.composed(), [('up', '-d', '--no-deps', '--wait', 'api', 'web')])
        self.assertEqual([c[0] for c in self.calls if c[0] != 'guard'], ['backup', 'build', 'checkout', 'compose', 'smoke'])
        self.assertEqual(self.head, OLD)
        self.assertEqual(('smoke', OLD, '0018'), next(c for c in self.calls if c[0] == 'smoke'),
                         'the schema stays where it was')
        self.assertEqual((record['kind'], record['outcome'], record['rolled_back_to']), ('rollback', 'succeeded', 1))
        self.assertEqual((record['commit'], record['tag'], record['alembic_head']), (OLD, OLD[:12], '0017'))
        self.assertEqual((record['alembic_before'], record['rebuilt']), ('0018', False))
        self.assertEqual(lab.current_record(lab.read_ledger())['seq'], 3)

    def test_guard_skips_container_drift_but_records_it(self):
        self.running['api']['revision'] = 'c' * 40
        record = lab.rollback(1)
        self.assertIn(('guard', {'containers': False}), self.calls)
        self.assertTrue(record['drift_before'][0].startswith('api runs cccccccccccc'))

    def test_scheduler_is_re_registered(self):
        self.running = services(self.current, scheduler=True)
        lab.rollback(1)
        self.assertEqual(self.composed(), [
            ('up', '-d', '--no-deps', '--wait', 'api', 'web'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'prefect'),
            ('--profile', 'scheduler', 'run', '--rm', '--no-deps', 'deploy'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'worker')])

    def test_pruned_image_is_rebuilt_and_marked(self):
        self.built = ['api', 'web']
        record = lab.rollback(1)
        self.assertTrue(record['rebuilt'])
        self.assertIn(('build', OLD), self.calls)

    def test_smoke_failure_is_recorded_without_another_attempt(self):
        self.smoke = (False, {'health': {'ok': False, 'status': 502}})
        with self.assertRaisesRegex(RuntimeError, 'Restore the pre-rollback backup 20261028T020000Z'):
            lab.rollback(1)
        record = lab.read_ledger()[-1]
        self.assertEqual((record['outcome'], record['replaced']), ('failed', True))
        self.assertEqual(len(self.composed()), 1)

    def test_build_failure_keeps_the_serving_checkout(self):
        with mock.patch.object(lab, 'build_images', side_effect=lab.Refused('labels differ')), self.assertRaises(lab.Refused):
            lab.rollback(1)
        self.assertEqual(self.head, NEW)
        self.assertEqual(self.composed(), [])
        record = lab.read_ledger()[-1]
        self.assertEqual((record['kind'], record['outcome'], record['replaced']), ('rollback', 'failed', False))


if __name__ == '__main__':
    unittest.main()
