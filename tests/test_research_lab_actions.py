"""The remaining actions: none of them builds, every production action is guarded and uses the recorded tag."""
import ast
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import lab, deployment_dir, deploy_record, services, OLD  # noqa: E402

GUARDED = ['start', 'stop', 'scheduler-start', 'reader-start', 'reader-stop', 'seed-git', 'bootstrap', 'restore',
           'backup', 'public-snapshot']


def main(*argv):
    with mock.patch.object(sys, 'argv', ['research_lab.py', *argv]), mock.patch('builtins.print') as printed:
        lab.main()
    return json.loads(printed.call_args.args[0])


class NoBuildTests(unittest.TestCase):
    """Images come only from build_images(); nothing composes or builds from a working tree."""
    def setUp(self):
        self.tree = ast.parse((ROOT / 'scripts/research_lab.py').read_text(encoding='utf-8'))

    def test_compose_is_never_asked_to_build(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and getattr(node.func, 'id', '') in ('compose', 'compose_fn'):
                words = [a.value for a in node.args if isinstance(a, ast.Constant)]
                self.assertNotIn('build', words, ast.unparse(node))

    def test_docker_build_only_in_build_images(self):
        owners = set()
        for function in [n for n in ast.walk(self.tree) if isinstance(n, ast.FunctionDef)]:
            for node in ast.walk(function):
                if isinstance(node, ast.List) and [getattr(e, 'value', None) for e in node.elts[:2]] == ['docker', 'build']:
                    owners.add(function.name)
        self.assertEqual(owners, {'build_images'})


class GuardedActionTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        lab.append_record(deploy_record())
        self.compose = mock.patch.object(lab, 'compose', return_value=b'').start()
        self.addCleanup(mock.patch.stopall)

    def test_every_production_action_refuses_when_the_guard_fails(self):
        mock.patch.object(lab, 'guard_problems', return_value=['Uncommitted changes or untracked files: x']).start()
        for action in GUARDED:
            with self.subTest(action=action), self.assertRaisesRegex(lab.Refused, f'Refusing to {action}'):
                main(action)
        self.compose.assert_not_called()

    def test_routine_actions_use_the_recorded_tag_and_never_build(self):
        for name, value in (('guard_problems', []), ('validate', {}), ('protected_snapshot', {}), ('verify_protected', None),
                            ('exclusion_conflicts', []), ('running_containers', {}), ('listening_ports', set())):
            mock.patch.object(lab, name, return_value=value).start()
        build = mock.patch.object(lab, 'build_images', side_effect=AssertionError('built')).start()
        for action in ('start', 'stop', 'scheduler-start', 'reader-start', 'reader-stop'):
            self.compose.reset_mock()
            with self.subTest(action=action):
                main(action)
                self.assertTrue(self.compose.called)
                self.assertEqual({call.kwargs['tag'] for call in self.compose.call_args_list}, {OLD[:12]})
                self.assertFalse(any('build' in call.args for call in self.compose.call_args_list))
        build.assert_not_called()

    def test_scheduler_start_registers_deployments_between_prefect_and_worker(self):
        for name, value in (('guard_problems', []), ('validate', {}), ('protected_snapshot', {}), ('verify_protected', None)):
            mock.patch.object(lab, name, return_value=value).start()
        main('scheduler-start')
        self.assertEqual([call.args for call in self.compose.call_args_list], [
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'prefect'),
            ('--profile', 'scheduler', 'run', '--rm', '--no-deps', 'deploy'),
            ('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'worker')])


class CommandLineTests(unittest.TestCase):
    def test_help_lists_the_new_actions(self):
        text = lab.build_parser().format_help()
        for action in ('deploy', 'rollback', 'status', 'scheduler-start', 'adopt', 'init-home'):
            self.assertIn(action, text)
        for removed in ('pg-check', 'rebuild-check'):
            self.assertNotIn(removed, text)
            self.assertNotIn(removed, lab.ACTIONS)
        self.assertNotIn('--handover', text, 'the handover flag is internal')

    def test_up_points_to_deploy(self):
        with mock.patch.object(sys, 'argv', ['research_lab.py', 'up']), mock.patch.object(lab, 'compose') as compose:
            with self.assertRaises(SystemExit) as caught:
                lab.main()
        self.assertIn('deploy --commit <sha>', str(caught.exception.code))
        compose.assert_not_called()

    def test_deploy_and_rollback_need_their_target(self):
        for argv in (['deploy'], ['rollback']):
            with self.subTest(argv=argv), mock.patch.object(sys, 'argv', ['research_lab.py', *argv]), \
                    mock.patch('sys.stderr'), self.assertRaises(SystemExit) as caught:
                lab.main()
            self.assertEqual(caught.exception.code, 2)


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        mock.patch.object(lab, 'git_head', return_value=OLD).start()
        mock.patch.object(lab, 'run', return_value='').start()  # git status --porcelain: clean
        self.addCleanup(mock.patch.stopall)

    def test_empty_record(self):
        mock.patch.object(lab, 'running_services', return_value={}).start()
        report = lab.status()
        self.assertEqual(report['note'], 'No deployment record yet')
        self.assertIsNone(report['deployed'])
        self.assertIn('No deployment record yet; run adopt first', report['problems'][-1])

    def test_reports_running_versions_and_differences(self):
        record = lab.append_record(deploy_record())
        running = services(record, api={'revision': 'c' * 40})
        mock.patch.object(lab, 'running_services', return_value=running).start()
        mock.patch.object(lab, 'alembic_version', return_value='0017').start()
        report = lab.status()
        self.assertEqual(report['deployed']['commit'], OLD)
        self.assertEqual(report['alembic_version'], '0017')
        self.assertEqual(report['services']['web']['revision'], OLD)
        self.assertEqual(len(report['problems']), 1)
        self.assertIn('api runs cccccccccccc', report['problems'][0])


class AdoptTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        self.commands = []
        self.running = {'db': {'container': 'db1', 'image_id': 'sha256:pg', 'revision': None, 'working_dir': 'C:/dev'},
                        'api': {'container': 'api1', 'image_id': 'sha256:dev-api', 'revision': None, 'working_dir': 'C:/dev'},
                        'worker': {'container': 'w1', 'image_id': 'sha256:dev-api', 'revision': None, 'working_dir': 'C:/dev'},
                        'web': {'container': 'web1', 'image_id': 'sha256:dev-web', 'revision': None, 'working_dir': 'C:/dev'}}
        mock.patch.object(lab, 'running_services', side_effect=lambda project: self.running).start()
        mock.patch.object(lab, 'git_head', return_value=OLD).start()
        mock.patch.object(lab, 'alembic_version', return_value='0017').start()
        mock.patch.object(lab, 'run', side_effect=self.fake_run).start()
        self.addCleanup(mock.patch.stopall)

    def fake_run(self, args, **kwargs):
        self.commands.append(args)
        if args[:2] == ['git', 'status']:
            return ''
        if args[:2] == ['docker', 'exec']:
            return '3.8.8\n'
        if args[:2] == ['docker', 'tag']:
            return b''
        raise AssertionError(f'unexpected command {args}')

    def test_tags_running_images_and_records_them(self):
        record = lab.adopt()
        self.assertIn(['docker', 'tag', 'sha256:dev-api', 'industryflow-research-api:pre-ledger'], self.commands)
        self.assertIn(['docker', 'tag', 'sha256:dev-web', 'industryflow-research-web:pre-ledger'], self.commands)
        self.assertEqual((record['seq'], record['kind'], record['outcome'], record['tag']), (1, 'adopt', 'succeeded', 'pre-ledger'))
        self.assertEqual((record['commit'], record['alembic_after'], record['prefect_version']), (OLD, '0017', '3.8.8'))
        self.assertTrue(record['replaced'])
        self.assertEqual(lab.current_record(lab.read_ledger()), record)

    def test_only_an_empty_record_is_adopted(self):
        lab.append_record(deploy_record())
        with self.assertRaisesRegex(lab.Refused, 'already has entries'):
            lab.adopt()

    def test_mixed_images_are_refused(self):
        self.running['worker']['image_id'] = 'sha256:older'
        with self.assertRaisesRegex(lab.Refused, 'different images'):
            lab.adopt()
        self.assertFalse(lab.LEDGER.exists())


if __name__ == '__main__':
    unittest.main()
