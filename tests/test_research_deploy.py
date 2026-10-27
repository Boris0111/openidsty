"""deploy --commit: merged commits only, the target version's script takes over, initialize before any
replacement, smoke results recorded and never an automatic rollback (design D6). No Docker needed."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import lab, deployment_dir, deploy_record, target_info, services, OLD, NEW, CHAIN  # noqa: E402

TOKEN = 'f' * 32
SMOKE_OK = {name: {'ok': True} for name in ('health', 'release', 'next', 'containers', 'alembic', 'working_dir')}


class ParentTests(unittest.TestCase):
    """Steps 1-3 run in the deployed version's script."""
    def setUp(self):
        self.root = deployment_dir(self)
        lab.append_record(deploy_record())
        self.calls, self.head, self.first_parent = [], OLD, [NEW, OLD]
        for name, value in (('guard_problems', []), ('exclusion_conflicts', []), ('running_containers', {}),
                            ('listening_ports', set())):
            patcher = mock.patch.object(lab, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for name, fake in (('run', self.fake_run), ('subprocess', mock.Mock(run=self.fake_child))):
            patcher = mock.patch.object(lab, name, fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.child_result = 0

    def fake_run(self, args, **kwargs):
        self.calls.append(args)
        if args[:2] == ['git', 'fetch']:
            return b''
        if args[:2] == ['git', 'rev-parse'] and args[-1] == 'HEAD':
            return self.head + '\n'
        if args[:2] == ['git', 'rev-parse']:
            return NEW + '\n'
        if args[:2] == ['git', 'rev-list']:
            self.assertEqual(args, ['git', 'rev-list', '--first-parent', 'origin/main'])
            return '\n'.join(self.first_parent) + '\n'
        if args[:2] == ['git', 'checkout']:
            self.head = args[-1]
            return b''
        raise AssertionError(f'unexpected command {args}')

    def fake_child(self, args, cwd):
        self.calls.append(('child', args, lab.HANDOVER.read_text(encoding='utf-8'), self.head))
        if self.child_result == 0:
            lab.append_record(deploy_record(NEW))
        return subprocess.CompletedProcess(args, self.child_result)

    def test_commit_off_the_first_parent_chain_is_refused(self):
        self.first_parent = [OLD]  # NEW is reachable from main only through a merged PR's side branch
        with self.assertRaisesRegex(lab.Refused, 'not on the first-parent chain of origin/main'):
            lab.deploy(NEW)
        self.assertFalse(any(c[0] == 'child' or c[:2] == ['git', 'checkout'] for c in self.calls))
        self.assertFalse(lab.HANDOVER.exists())

    def test_target_version_script_takes_over(self):
        lab.deploy(NEW, force=True)
        checkout = self.calls.index(['git', 'checkout', '--quiet', '--detach', NEW])
        [child] = [c for c in self.calls if c[0] == 'child']
        self.assertGreater(self.calls.index(child), checkout, 'the target is checked out before its script runs')
        _, args, token, head = child
        self.assertEqual(head, NEW)
        self.assertEqual(args[:5], [sys.executable, str(self.root / 'scripts' / 'research_lab.py'), 'deploy', '--commit', NEW])
        self.assertEqual(args[5:7], ['--handover', token])
        self.assertIn('--force', args)
        self.assertFalse(lab.HANDOVER.exists(), 'the handover token is removed afterwards')
        self.assertEqual(self.head, NEW)

    def test_failed_target_leaves_the_serving_commit_checked_out(self):
        self.child_result = 3
        with self.assertRaises(SystemExit) as caught:
            lab.deploy(NEW)
        self.assertEqual(caught.exception.code, 3)
        self.assertEqual(self.head, OLD)
        self.assertEqual(self.calls[-1], ['git', 'checkout', '--quiet', '--detach', OLD])

    def test_guard_and_exclusion_refuse_before_fetching(self):
        lab.guard_problems.return_value = ['HEAD bbbbbbbbbbbb is not the deployed commit aaaaaaaaaaaa']
        with self.assertRaisesRegex(lab.Refused, 'HEAD bbbbbbbbbbbb'):
            lab.deploy(NEW)
        lab.guard_problems.return_value = []
        lab.exclusion_conflicts.return_value = ['Original service still running: industryflow-web-1']
        with self.assertRaisesRegex(lab.Refused, 'Original service'):
            lab.deploy(NEW)
        self.assertEqual(self.calls, [])


class TargetHarness(unittest.TestCase):
    """Steps 4-10 run in the target version's script while the parent holds the lock."""
    db_version = '0017'
    busy = []
    target = target_info(NEW)

    def setUp(self):
        self.root = deployment_dir(self)
        self.current = lab.append_record(deploy_record())
        lab.HANDOVER.write_text(TOKEN, encoding='utf-8')
        self.calls, self.running = [], services(self.current)
        self.smoke = (True, SMOKE_OK)
        self.initialize_error = None
        fakes = {'guard_problems': lambda **kw: self.log('guard', kw) or [],
                 'commit_info': lambda commit: self.target,
                 'running_services': lambda project: self.running,
                 'alembic_version': lambda container: self.db_version,
                 'prefect_runs': lambda: self.busy,
                 'validate': lambda tag: self.log('validate', tag) or {},
                 'backup': lambda secondary, **kw: self.log('backup', secondary, kw) or {'backup': '/b/20261028T010000Z'},
                 'build_images': lambda commit: self.log('build', commit) or (commit[:12], ['api', 'web']),
                 'image_ids': lambda tag: {'api': 'sha256:api-new', 'web': 'sha256:web-new'},
                 'compose': self.compose,
                 'smoke_checks': lambda *a, **kw: self.log('smoke', a[3], a[4]) or self.smoke}
        for name, fake in fakes.items():
            patcher = mock.patch.object(lab, name, side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        lock = lab.deployment_lock()
        lock.__enter__()
        self.addCleanup(lock.__exit__, None, None, None)

    def log(self, *entry):
        self.calls.append(entry)

    def compose(self, *args, tag, input=None):
        self.calls.append(('compose', tag, *args))
        if 'initialize' in args and self.initialize_error:
            raise RuntimeError(self.initialize_error)
        return b''

    def deploy(self, **flags):
        return lab.deploy_target(NEW, TOKEN, **flags)

    def names(self):
        return [c[0] if c[0] != 'compose' else 'up' if 'up' in c else 'initialize' if 'initialize' in c else 'compose'
                for c in self.calls if c[0] not in ('guard', 'validate')]

    def ups(self):
        return [c[2:] for c in self.calls if c[0] == 'compose' and 'up' in c]

    def ledger(self):
        return lab.read_ledger()


class RefusalTests(TargetHarness):
    def assert_refused(self, pattern, **flags):
        with self.assertRaisesRegex(lab.Refused, pattern):
            self.deploy(**flags)
        self.assertEqual(self.names(), [], 'nothing ran before the refusal')
        self.assertEqual(len(self.ledger()), 1, 'a refusal is not a deployment')

    def test_handover_is_internal(self):
        with self.assertRaisesRegex(lab.Refused, 'internal to deploy'):
            lab.deploy_target(NEW, 'wrong-token')

    def test_handover_needs_the_parent_lock(self):
        with mock.patch.object(lab, 'lock_held', return_value=False), self.assertRaisesRegex(lab.Refused, 'internal'):
            self.deploy()

    def test_guard_expects_the_target_head(self):
        self.deploy()
        self.assertIn(('guard', {'expect_head': NEW}), self.calls)

    def test_database_not_on_the_target_chain(self):
        self.db_version = '0018'  # a migration the target does not know: withdrawn or rewritten
        self.assert_refused('not on the migration chain')

    def test_busy_prefect_without_force(self):
        self.running = services(self.current, scheduler=True)
        self.busy = ['official-information/hourly-run']
        self.assert_refused('Prefect has 1 running flow run')
        self.deploy(force=True)
        self.assertEqual(self.ledger()[-1]['outcome'], 'succeeded')

    def test_contract_migration_without_allow_contract(self):
        self.target = target_info(NEW, chain=[*CHAIN, '0018'], contracts=('0009', '0017', '0018'))
        self.assert_refused(r'Contract migration\(s\) 0018 would be applied')

    def test_db_created_from_another_directory(self):
        self.running['db']['working_dir'] = r'C:\Users\User\openspec_pjt'
        self.assert_refused('--recreate-db')


class SequenceTests(TargetHarness):
    def test_backup_build_initialize_replace_smoke(self):
        record = self.deploy()
        self.assertEqual(self.names(), ['backup', 'build', 'initialize', 'up', 'smoke'])
        backup = next(c for c in self.calls if c[0] == 'backup')
        self.assertEqual(backup[2], {'tag': OLD[:12], 'boundary': []}, 'the backup runs on the serving image')
        initialize = next(c for c in self.calls if c[0] == 'compose' and 'initialize' in c)
        self.assertEqual(initialize[1:], (NEW[:12], 'run', '--rm', '--no-deps', '-T', 'initialize'))
        self.assertEqual(self.ups(), [('up', '-d', '--no-deps', '--wait', 'api', 'web')])
        self.assertEqual(record['outcome'], 'succeeded')
        self.assertEqual(record['seq'], 2)
        self.assertEqual((record['commit'], record['tag'], record['backup']), (NEW, NEW[:12], '20261028T010000Z'))
        self.assertEqual((record['alembic_before'], record['alembic_after'], record['alembic_head']), ('0017', '0017', '0017'))
        self.assertEqual(record['smoke'], SMOKE_OK)
        self.assertTrue(record['replaced'])

    def test_scheduler_and_reader_are_replaced_in_order(self):
        self.running = services(self.current, scheduler=True, reader=True)
        self.deploy()
        steps = [c[2:] for c in self.calls if c[0] == 'compose']
        self.assertEqual(steps[1:], [
            ('up', '-d', '--no-deps', '--wait', 'api', 'web'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'prefect'),
            ('--profile', 'scheduler', 'run', '--rm', '--no-deps', 'deploy'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'worker'),
            ('--profile', 'reader', 'up', '-d', '--no-deps', '--wait', 'reader')])

    def test_db_is_never_in_a_routine_up(self):
        self.running = services(self.current, scheduler=True, reader=True)
        self.deploy()
        for up in self.ups():
            self.assertNotIn('db', up)

    def test_recreate_db_only_when_asked_and_after_initialize(self):
        self.running['db']['working_dir'] = r'C:\Users\User\openspec_pjt'
        self.deploy(recreate_db=True)
        self.assertEqual(self.ups()[0], ('up', '-d', '--no-deps', '--force-recreate', '--wait', 'db'))
        self.assertLess(self.names().index('initialize'), self.names().index('up'))

    def test_contract_deploy_marks_the_boundary_backup(self):
        self.target = target_info(NEW, chain=[*CHAIN, '0018'], contracts=('0009', '0017', '0018'))
        record = self.deploy(allow_contract=True)
        backup = next(c for c in self.calls if c[0] == 'backup')
        self.assertEqual(backup[2]['boundary'], ['0018'])
        self.assertTrue(record['contract_boundary'])

    def test_initialize_failure_replaces_nothing(self):
        self.initialize_error = 'import_map failed: theme change_reason missing'
        with self.assertRaisesRegex(RuntimeError, 'import_map failed'):
            self.deploy()
        self.assertEqual(self.ups(), [])
        record = self.ledger()[-1]
        self.assertEqual((record['outcome'], record['replaced']), ('failed', False))
        self.assertIn('import_map failed', record['error'])
        self.assertEqual(lab.current_record(self.ledger())['seq'], 1, 'the old deployment still serves')

    def test_smoke_failure_is_recorded_with_a_rollback_command_and_no_rollback(self):
        lab.LEDGER.unlink()
        lab.append_record(deploy_record('c' * 40))
        self.current = lab.append_record(deploy_record())
        self.smoke = (False, {**SMOKE_OK, 'next': {'ok': False, 'status': 500}})
        with self.assertRaises(RuntimeError) as caught:
            self.deploy()
        record = self.ledger()[-1]
        self.assertEqual((record['outcome'], record['replaced']), ('failed', True))
        self.assertEqual(record['fallback'], 'python scripts/research_lab.py rollback --to 2')
        self.assertIn('Smoke check failed: next', record['error'])
        self.assertIn('nothing was rolled back automatically', str(caught.exception))
        self.assertIn('rollback --to 2', str(caught.exception))
        self.assertEqual(len(self.ups()), 1, 'no second replacement')

    def test_smoke_failure_after_a_contract_points_to_the_backup(self):
        self.target = target_info(NEW, chain=[*CHAIN, '0018'], contracts=('0009', '0017', '0018'))
        self.smoke = (False, {**SMOKE_OK, 'health': {'ok': False, 'status': 502}})
        self.db_version = '0017'
        with mock.patch.object(lab, 'alembic_version', side_effect=['0017', '0018']), self.assertRaises(RuntimeError):
            self.deploy(allow_contract=True)
        fallback = self.ledger()[-1]['fallback']
        self.assertIn('Rollback is refused', fallback)
        self.assertIn('0018', fallback)
        self.assertIn('20261028T010000Z', fallback)

    def test_record_fields_are_documented(self):
        record = self.deploy()
        doc = (ROOT / 'docs/research-deployment.md').read_text(encoding='utf-8')
        table = doc.split('## 部署紀錄欄位', 1)[1].split('\n## ', 1)[0]
        documented = set(re.findall(r'^\| ([^|]+) \|', table, re.M)[1:])
        documented = {name for cell in documented for name in re.findall(r'`([a-z_]+)`', cell)}
        self.assertLessEqual(set(record), documented)


class RefusalRuleTests(unittest.TestCase):
    def test_deploy_rules(self):
        target = target_info(NEW, chain=[*CHAIN, '0018'], contracts=('0017', '0018'))
        self.assertEqual(lab.deploy_refusals(target, '0018', []), ([], []))
        self.assertEqual(lab.deploy_refusals(target, '0017', [], allow_contract=True), ([], ['0018']))
        refusals, added = lab.deploy_refusals(target, '0016', ['a', 'b'])
        self.assertEqual(added, ['0017', '0018'])
        self.assertEqual(len(refusals), 2)
        self.assertEqual(lab.deploy_refusals(target, None, []), ([], []), 'an empty database has nothing to break')


if __name__ == '__main__':
    unittest.main()
