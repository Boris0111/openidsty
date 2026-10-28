"""rollback --to <seq> (design D7): the current script judges compatibility with the newest rules and takes the
backup; the target version's script takes over to rebuild, replace and check without initialize. No Docker."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import lab, deployment_dir, deploy_record, target_info, services, OLD, NEW, CHAIN  # noqa: E402

TOKEN = 'f' * 32
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
        self.infos = {OLD: target_info(OLD), NEW: target_info(NEW, chain=[*CHAIN, '0018'])}
        self.child_code, self.child_records = 0, True
        fakes = {'guard_problems': lambda **kw: self.log('guard', kw) or [],
                 'running_services': lambda project: self.running,
                 'alembic_version': lambda container: self.db_version,
                 'prefect_runs': self.prefect, 'commit_info': lambda commit: self.infos[commit],
                 'validate': lambda tag: self.log('validate', tag) or {},
                 'backup': lambda secondary, **kw: self.log('backup', kw) or {'backup': '/b/20261028T020000Z'},
                 'build_images': lambda commit: self.log('build', commit) or (commit[:12], self.built),
                 'image_ids': lambda tag: {'api': 'sha256:api-' + tag[:4], 'web': 'sha256:web-' + tag[:4]},
                 'compose': self.compose, 'run': self.fake_run, 'git_head': lambda: self.head,
                 'smoke_checks': lambda *a, **kw: self.log('smoke', a[3], a[4]) or self.smoke,
                 'wait_for_idle': lambda: self.log('wait') or []}
        for name, fake in fakes.items():
            patcher = mock.patch.object(lab, name, side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(lab, 'subprocess', mock.Mock(run=self.fake_child))
        patcher.start()
        self.addCleanup(patcher.stop)

    def log(self, *entry):
        self.calls.append(entry)

    def prefect(self):
        if isinstance(self.busy, Exception):
            raise self.busy
        return self.busy

    def compose(self, *args, tag, input=None):
        self.calls.append(('compose', tag, *args))
        return b''

    def fake_run(self, args, **kwargs):
        if args[:2] == ['git', 'checkout']:
            self.head = args[-1]
            self.calls.append(('checkout', args[-1]))
            return b''
        raise AssertionError(f'unexpected command {args}')

    def fake_child(self, args, cwd):
        self.calls.append(('child', args[2:], self.head))
        if self.child_records:
            lab.append_record(deploy_record(OLD, kind='rollback', rolled_back_to=1))
        return subprocess.CompletedProcess(args, self.child_code)

    def composed(self):
        return [c[2:] for c in self.calls if c[0] == 'compose']

    def names(self):
        return [c[0] for c in self.calls if c[0] not in ('guard', 'validate')]


class RefusalTests(RollbackHarness):
    def assert_refused(self, seq, pattern, **flags):
        before = lab.read_ledger()
        with self.assertRaisesRegex(lab.Refused, pattern):
            lab.rollback(seq, **flags)
        self.assertEqual(self.names(), [], 'nothing ran before the refusal')
        self.assertEqual(lab.read_ledger(), before, 'a refusal is not recorded')
        self.assertEqual(self.head, NEW)

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

    def test_contract_known_only_to_the_current_rules(self):
        # Both records were written under older rules that saw 0018 as expand; the current rules call it contract.
        self.infos[NEW] = target_info(NEW, chain=[*CHAIN, '0018'], contracts=('0009', '0017', '0018'))
        self.assert_refused(1, r'crosses contract migration\(s\) 0018')

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
        self.assert_refused(1, r'Prefect has 1 running flow run\(s\) \(publish-run\)')

    def test_unreachable_prefect_is_refused_unless_forced(self):
        self.running = services(self.current, scheduler=True)
        self.busy = OSError('connection refused')
        self.assert_refused(1, 'cannot tell whether a data update is running.*pass --force')
        lab.rollback(1, force=True)
        self.assertIn('--force', next(c for c in self.calls if c[0] == 'child')[1])

    def test_disagreeing_chains(self):
        lab.LEDGER.unlink()
        lab.append_record(deploy_record(OLD))
        lab.append_record(deploy_record(NEW, chain=[*CHAIN[:-1], '0099']))
        self.infos[NEW] = target_info(NEW, chain=[*CHAIN[:-1], '0099'])
        self.db_version = '0099'
        self.assert_refused(1, 'merged migration was rewritten')


class ParentTests(RollbackHarness):
    def test_backup_then_hand_over_to_the_target_script(self):
        lab.rollback(1)
        self.assertEqual(self.names(), ['backup', 'checkout', 'child'])
        self.assertIn(('guard', {'containers': False}), self.calls)
        backup = next(c for c in self.calls if c[0] == 'backup')
        self.assertEqual(backup[1], {'tag': NEW[:12]}, 'the backup runs on the serving image')
        _, args, head = next(c for c in self.calls if c[0] == 'child')
        self.assertEqual(head, OLD, 'the target is checked out before its script runs')
        self.assertEqual(args[:5], ['rollback', '--to', '1', '--handover-backup', '20261028T020000Z'])
        self.assertEqual(args[-2], '--handover')
        self.assertFalse(lab.HANDOVER.exists())
        self.assertEqual(self.composed(), [], 'the current script replaces nothing itself')

    def test_backup_failure_is_recorded_and_nothing_is_checked_out(self):
        lab.backup.side_effect = RuntimeError('pg_dump failed')
        with self.assertRaisesRegex(RuntimeError, 'pg_dump failed'):
            lab.rollback(1)
        record = lab.read_ledger()[-1]
        self.assertEqual((record['kind'], record['outcome'], record['replaced']), ('rollback', 'failed', False))
        self.assertNotIn('checkout', self.names())

    def test_target_script_without_a_record_is_recorded_from_the_containers(self):
        self.child_code, self.child_records = 9, False
        with self.assertRaises(SystemExit) as caught:
            lab.rollback(1)
        self.assertEqual(caught.exception.code, 9)
        record = lab.read_ledger()[-1]
        self.assertEqual((record['kind'], record['outcome'], record['replaced']), ('rollback', 'failed', False))
        self.assertIn('ended with exit 9', record['error'])
        self.assertEqual(self.head, NEW, 'nothing was replaced, so the serving commit is checked out again')

    def test_refusing_target_script_needs_no_record(self):
        self.child_code, self.child_records = lab.REFUSED_EXIT, False
        with self.assertRaises(SystemExit):
            lab.rollback(1)
        self.assertEqual(len(lab.read_ledger()), 2)
        self.assertEqual(self.head, NEW)


class TargetTests(RollbackHarness):
    """rollback --to <seq> --handover: the target version's own build, compose rules and smoke checks."""
    def setUp(self):
        super().setUp()
        self.head = OLD
        lab.HANDOVER.write_text(TOKEN, encoding='utf-8')
        lock = lab.deployment_lock()
        lock.__enter__()
        self.addCleanup(lock.__exit__, None, None, None)

    def target(self, **flags):
        return lab.rollback_target(1, TOKEN, '20261028T020000Z', **flags)

    def test_handover_is_internal(self):
        with self.assertRaisesRegex(lab.Refused, '--handover is internal'):
            lab.rollback_target(1, 'wrong', '20261028T020000Z')

    def test_no_initialize_and_up_no_deps(self):
        record = self.target()
        self.assertFalse(any('initialize' in step for step in self.composed()))
        self.assertEqual(self.composed(), [('up', '-d', '--no-deps', '--wait', 'api', 'web')])
        self.assertEqual(self.names(), ['build', 'compose', 'smoke'])
        self.assertIn(('guard', {'expect_head': OLD, 'containers': False}), self.calls)
        self.assertIn(('validate', OLD[:12]), self.calls, "the target's own compose rules")
        self.assertEqual(('smoke', OLD, '0018'), next(c for c in self.calls if c[0] == 'smoke'), 'the schema stays where it was')
        self.assertEqual((record['kind'], record['outcome'], record['rolled_back_to'], record['backup']),
                         ('rollback', 'succeeded', 1, '20261028T020000Z'))
        self.assertEqual((record['commit'], record['tag'], record['alembic_head']), (OLD, OLD[:12], '0017'))
        self.assertEqual((record['alembic_before'], record['rebuilt']), ('0018', False))
        self.assertEqual(lab.current_record(lab.read_ledger())['seq'], 3)

    def test_container_drift_is_recorded(self):
        self.running['api']['revision'] = 'c' * 40
        self.assertTrue(self.target()['drift_before'][0].startswith('api runs cccccccccccc'))

    def test_scheduler_is_re_registered_after_waiting_for_idle(self):
        self.running = services(self.current, scheduler=True)
        self.target()
        self.assertLess(self.calls.index(('wait',)), next(i for i, c in enumerate(self.calls) if c[0] == 'compose'))
        self.assertEqual(self.composed(), [
            ('up', '-d', '--no-deps', '--wait', 'api', 'web'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'prefect'),
            ('--profile', 'scheduler', 'run', '--rm', '--no-deps', 'deploy'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'worker')])

    def test_run_still_going_keeps_the_services(self):
        self.running = services(self.current, scheduler=True)
        lab.wait_for_idle.side_effect = lambda: ['hourly-run']
        with self.assertRaisesRegex(lab.Refused, 'hourly-run'):
            self.target()
        self.assertEqual(self.composed(), [])
        record = lab.read_ledger()[-1]
        self.assertEqual((record['outcome'], record['replaced']), ('failed', False))

    def test_pruned_image_is_rebuilt_and_marked(self):
        self.built = ['api', 'web']
        self.assertTrue(self.target()['rebuilt'])
        self.assertIn(('build', OLD), self.calls)

    def test_smoke_failure_is_recorded_without_another_attempt(self):
        self.smoke = (False, {'health': {'ok': False, 'status': 502}})
        with self.assertRaisesRegex(RuntimeError, 'Restore the pre-rollback backup 20261028T020000Z'):
            self.target()
        record = lab.read_ledger()[-1]
        self.assertEqual((record['outcome'], record['replaced']), ('failed', True))
        self.assertEqual(len(self.composed()), 1)

    def test_build_failure_is_recorded(self):
        lab.build_images.side_effect = lab.Refused('labels differ')
        with self.assertRaises(lab.Refused):
            self.target()
        self.assertEqual(self.composed(), [])
        record = lab.read_ledger()[-1]
        self.assertEqual((record['kind'], record['outcome'], record['replaced']), ('rollback', 'failed', False))

    def test_ctrl_c_during_replacement_is_recorded_then_raised(self):
        def interrupted(*args, tag, input=None):
            raise KeyboardInterrupt
        lab.compose.side_effect = interrupted
        with self.assertRaises(KeyboardInterrupt):
            self.target()
        record = lab.read_ledger()[-1]
        self.assertEqual((record['outcome'], record['replaced'], record['error']), ('failed', True, 'KeyboardInterrupt'))


if __name__ == '__main__':
    unittest.main()
