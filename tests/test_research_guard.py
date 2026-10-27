"""Production actions run only from the deployment directory, clean and matching the record (design D2)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import lab, deployment_dir, deploy_record, services, OLD, NEW  # noqa: E402
from test_research_lab_config import config  # noqa: E402


class GitFake:
    def __init__(self, status='', head=OLD, volumes=()):
        self.status, self.head, self.volumes, self.calls = status, head, list(volumes), []

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if args[:2] == ['git', 'status']:
            return self.status
        if args[:2] == ['git', 'rev-parse']:
            return self.head + '\n'
        if args[:3] == ['docker', 'volume', 'ls']:
            return '\n'.join(self.volumes) + '\n'
        raise AssertionError(f'unexpected command {args}')


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        self.record = lab.append_record(deploy_record())
        self.git = GitFake()
        self.running = services(self.record)
        for name, fake in (('run', self.git), ('running_services', lambda project: self.running)):
            patcher = mock.patch.object(lab, name, side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_matching_deployment_has_no_problems(self):
        self.assertEqual(lab.guard_problems(), [])

    def test_missing_marker(self):
        lab.HOME_FILE.unlink()
        self.assertIn('No deployments/home.json', lab.guard_problems()[0])

    def test_marker_names_another_directory(self):
        lab.HOME_FILE.write_text(json.dumps({'path': str(self.root.parent)}), encoding='utf-8')
        self.assertIn('not this checkout', lab.guard_problems()[0])

    def test_uncommitted_changes(self):
        self.git.status = ' M scripts/research_lab.py\n'
        self.assertEqual(lab.guard_problems(), ['Uncommitted changes or untracked files: scripts/research_lab.py'])

    def test_untracked_files(self):
        self.git.status = '?? notes.txt\n'
        self.assertEqual(lab.guard_problems(), ['Uncommitted changes or untracked files: notes.txt'])

    def test_head_drift(self):
        self.git.head = NEW
        self.assertEqual(lab.guard_problems(), ['HEAD bbbbbbbbbbbb is not the deployed commit aaaaaaaaaaaa'])

    def test_container_revision_drift(self):
        self.running['api']['revision'] = NEW
        [problem] = lab.guard_problems()
        self.assertIn('api runs bbbbbbbbbbbb', problem)
        self.assertIn('the record has aaaaaaaaaaaa', problem)

    def test_container_image_drift(self):
        self.running['web']['image_id'] = 'sha256:rebuilt-elsewhere'
        self.assertIn('web runs', lab.guard_problems()[0])

    def test_db_image_is_not_compared(self):
        self.running['db']['image_id'] = 'sha256:postgres-patch'
        self.assertEqual(lab.guard_problems(), [])

    def test_adopt_record_compares_image_ids(self):
        lab.LEDGER.unlink()
        lab.append_record({'kind': 'adopt', 'outcome': 'succeeded', 'replaced': True, 'commit': OLD, 'tag': lab.PRE_LEDGER,
                           'images': {'api': 'sha256:api-aaaa', 'web': 'sha256:web-aaaa'},
                           'services': {name: {'image_id': info['image_id']} for name, info in self.running.items()}})
        for info in self.running.values():
            info['revision'] = None
        self.assertEqual(lab.guard_problems(), [])
        self.running['api']['image_id'] = 'sha256:other'
        self.assertIn('adopt record', lab.guard_problems()[0])

    def test_every_problem_is_listed_and_the_action_refused(self):
        self.git.status, self.git.head = '?? x\n', NEW
        self.running['api']['revision'] = NEW
        with self.assertRaises(lab.Refused) as caught, mock.patch.object(lab, 'validate') as validate:
            with lab.production('start'):
                self.fail('the action ran')
        message = str(caught.exception)
        self.assertTrue(message.startswith('Refusing to start:'))
        for text in ('untracked', 'HEAD bbbbbbbbbbbb', 'api runs'):
            self.assertIn(text, message)
        validate.assert_not_called()

    def test_failed_deploy_that_replaced_services_is_what_runs(self):
        # After a failed smoke check the new services stay; the guard expects them so rollback can run.
        failed = lab.append_record(deploy_record(NEW, outcome='failed', replaced=True))
        self.running, self.git.head = services(failed), NEW
        self.assertEqual(lab.guard_problems(), [])

    def test_failed_deploy_before_replacement_changes_nothing(self):
        lab.append_record(deploy_record(NEW, outcome='failed', replaced=False))
        self.assertEqual(lab.guard_problems(), [])

    def test_check_reports_without_refusing(self):
        self.git.head = NEW
        lab.ENV_FILE.write_text(''.join(f'{key}={"a" * 64}\n' for key in lab.SECRET_KEYS), encoding='utf-8')
        with mock.patch.object(lab, 'compose', return_value=json.dumps(config(OLD[:12])).encode()):
            report = lab.check()
        self.assertEqual(report['problems'], ['HEAD bbbbbbbbbbbb is not the deployed commit aaaaaaaaaaaa'])
        self.assertEqual(report['tag'], OLD[:12])


class NoMarkerTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self, marked=False)

    def test_refused_before_any_state_changes(self):
        with mock.patch.object(lab, 'run', side_effect=AssertionError('nothing may run')):
            for action in ('start', 'backup', 'public-snapshot'):
                with self.subTest(action=action), self.assertRaisesRegex(lab.Refused, 'deployment directory'):
                    with lab.production(action):
                        self.fail('the action ran')
            with self.assertRaisesRegex(lab.Refused, 'deployment directory'):
                lab.deploy(NEW)
            with self.assertRaisesRegex(lab.Refused, 'deployment directory'):
                lab.rollback(1)
        self.assertFalse(lab.DEPLOYMENTS.exists(), 'no deployments/ folder or lock file in a development checkout')


class LockTests(unittest.TestCase):
    def setUp(self):
        deployment_dir(self)

    def test_second_writer_is_refused(self):
        with lab.deployment_lock():
            self.assertTrue(lab.lock_held())
            with self.assertRaisesRegex(lab.Refused, 'holds deployments/.lock'):
                with lab.deployment_lock():
                    self.fail('two writers')
        self.assertFalse(lab.lock_held())
        with lab.deployment_lock():
            pass

    def test_waiting_writer_gives_up_after_the_deadline(self):
        with lab.deployment_lock(), mock.patch.object(lab.time, 'sleep') as sleep:
            with self.assertRaises(lab.Refused):
                with lab.deployment_lock(wait_seconds=0.05):
                    self.fail('two writers')
        self.assertTrue(sleep.called)

    def test_backup_waits_and_other_actions_do_not(self):
        waits = []

        class Recorder:
            def __init__(self, wait_seconds=0):
                waits.append(wait_seconds)

            def __enter__(self):
                raise lab.Refused('stop here')

            def __exit__(self, *exc):
                return False
        with mock.patch.object(lab, 'deployment_lock', Recorder):
            for action in ('backup', 'start'):
                with self.assertRaises(lab.Refused), lab.production(action):
                    pass
        self.assertEqual(waits, [3600, 0])

    def child(self, code):
        script = textwrap.dedent(f'''
            import sys; from pathlib import Path
            sys.path.insert(0, {str(ROOT / "scripts")!r})
            import research_lab as lab
            lab.LOCK = Path({str(lab.LOCK)!r})
        ''') + textwrap.dedent(code)
        return subprocess.Popen([sys.executable, '-c', script], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def test_a_writer_in_another_process_holds_the_lock(self):
        child = self.child('''
            with lab.deployment_lock():
                print('held', flush=True)
                sys.stdin.readline()
        ''')
        try:
            self.assertEqual(child.stdout.readline().strip(), 'held')
            self.assertTrue(lab.lock_held())
            with self.assertRaises(lab.Refused):
                with lab.deployment_lock():
                    self.fail('two writers')
        finally:
            child.communicate('\n')
        self.assertFalse(lab.lock_held())

    def test_the_os_releases_the_lock_of_a_crashed_writer(self):
        child = self.child('''
            import os
            with lab.deployment_lock():
                print('held', flush=True)
                os._exit(1)
        ''')
        self.assertEqual(child.stdout.readline().strip(), 'held')
        child.wait()
        child.stdout.close()
        child.stdin.close()
        self.assertFalse(lab.lock_held())


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self, marked=False)

    def test_refused_next_to_an_existing_database_volume(self):
        with mock.patch.object(lab, 'run', GitFake(volumes=['industryflow-research_pg-data'])):
            with self.assertRaisesRegex(lab.Refused, 'industryflow-research_pg-data already exists'):
                lab.setup()
        self.assertFalse(lab.ENV_FILE.exists())

    def test_no_appending_next_to_an_existing_database_volume(self):
        lab.ENV_FILE.write_text('RESEARCH_POSTGRES_PASSWORD=' + 'a' * 64 + '\n', encoding='utf-8')
        before = lab.ENV_FILE.read_bytes()
        with mock.patch.object(lab, 'run', GitFake(volumes=['industryflow-research_pg-data'])):
            with self.assertRaises(lab.Refused):
                lab.setup()
        self.assertEqual(lab.ENV_FILE.read_bytes(), before)

    def test_new_secrets_without_a_database(self):
        with mock.patch.object(lab, 'run', GitFake(volumes=['industryflow-research-drill_pg-data'])):
            lab.setup()
        pairs = lab.env_pairs()
        self.assertEqual(set(pairs), set(lab.SECRET_KEYS))
        self.assertEqual(len(set(pairs.values())), 4)

    def test_complete_file_needs_no_docker(self):
        lab.ENV_FILE.write_text(''.join(f'{key}={os.urandom(32).hex()}\n' for key in lab.SECRET_KEYS), encoding='utf-8')
        with mock.patch.object(lab, 'run', side_effect=AssertionError('no docker call')):
            lab.setup()

    def test_tombstone_is_refused_and_preserved(self):
        tombstone = ('# Production secrets moved to the deployment directory (docs/research-deployment.md).\n'
                     'RESEARCH_POSTGRES_PASSWORD=moved-to-the-deployment-directory\n')
        lab.ENV_FILE.write_text(tombstone, encoding='utf-8')
        with mock.patch.object(lab, 'run', side_effect=AssertionError('no docker call')):
            with self.assertRaisesRegex(ValueError, 'Invalid research environment'):
                lab.setup()
            with self.assertRaisesRegex(ValueError, 'Invalid research environment'):
                lab.check()
        self.assertEqual(lab.ENV_FILE.read_text(encoding='utf-8'), tombstone)

    def test_check_never_creates_secrets(self):
        with mock.patch.object(lab, 'run', side_effect=AssertionError('no docker call')):
            with self.assertRaisesRegex(lab.Refused, 'No .env.research'):
                lab.check()
        self.assertFalse(lab.ENV_FILE.exists())

    def test_check_never_appends_secrets(self):
        lab.ENV_FILE.write_text('RESEARCH_POSTGRES_PASSWORD=' + 'a' * 64 + '\n', encoding='utf-8')
        before = lab.ENV_FILE.read_bytes()
        with mock.patch.object(lab, 'compose', return_value=json.dumps(config(lab.PLACEHOLDER_TAG)).encode()), \
                mock.patch.object(lab, 'run', GitFake()), mock.patch.object(lab, 'running_services', return_value={}):
            report = lab.check()
        self.assertEqual(lab.ENV_FILE.read_bytes(), before)
        self.assertIn('No deployments/home.json', report['problems'][0])


class InitHomeTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self, marked=False)

    def test_refused_in_a_worktree_or_on_a_branch(self):
        with self.assertRaisesRegex(lab.Refused, 'own git clone'):
            lab.init_home()
        (self.root / '.git').mkdir()
        with mock.patch.object(lab.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            with self.assertRaisesRegex(lab.Refused, 'detached'):
                lab.init_home()
        self.assertFalse(lab.HOME_FILE.exists())

    def test_marker_records_the_path_once(self):
        (self.root / '.git').mkdir()
        with mock.patch.object(lab.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1)):
            marker = lab.init_home('D:\\backups\\industryflow-research')
            self.assertEqual(json.loads(lab.HOME_FILE.read_text(encoding='utf-8')), marker)
            self.assertEqual(marker['path'], str(self.root))
            self.assertIsNone(lab.home_problem())
            with self.assertRaisesRegex(lab.Refused, 'already exists'):
                lab.init_home()


if __name__ == '__main__':
    unittest.main()
