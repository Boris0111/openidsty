"""The drill runs from any checkout or worktree: its secrets live in INDUSTRYFLOW_DRILL_HOME, it never reads the
production secrets, and failure output hides both. No Docker needed."""
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_drill as drill
import research_lab as lab
import research_draft_bench as bench
import research_scale as scale


class DrillHomeTests(unittest.TestCase):
    def resolve(self, **env):
        environment = {k: v for k, v in os.environ.items() if k != 'INDUSTRYFLOW_DRILL_HOME'}
        environment.update(env)
        return subprocess.run([sys.executable, '-c', 'import research_drill; print(research_drill.ENV_FILE)'],
                              cwd=ROOT / 'scripts', env=environment, capture_output=True, text=True, check=True).stdout.strip()

    def test_env_file_follows_the_drill_home(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertEqual(Path(self.resolve(INDUSTRYFLOW_DRILL_HOME=home)), Path(home) / '.env.research-drill')

    def test_default_is_in_the_user_profile_not_the_checkout(self):
        path = Path(self.resolve())
        self.assertEqual(path, Path.home() / 'industryflow-drill' / '.env.research-drill')
        self.assertNotEqual(path.parent, ROOT)


class SetupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        home = self.root / 'drill-home'
        # A worktree: no production .env.research anywhere near it.
        for patcher in (mock.patch.multiple(drill, DRILL_HOME=home, ENV_FILE=home / '.env.research-drill'),
                        mock.patch.object(lab, 'ENV_FILE', self.root / 'worktree' / '.env.research')):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_setup_without_production_secrets(self):
        real_read = Path.read_text

        def guarded_read(path, *args, **kwargs):
            if path.name == '.env.research':
                raise AssertionError('production secrets were read')
            return real_read(path, *args, **kwargs)
        with mock.patch.object(Path, 'read_text', guarded_read):
            drill.setup('IndustryFlow research drill drill@example.invalid')
        values = drill.env_values()
        self.assertEqual(set(values), {*lab.SECRET_KEYS, 'DRILL_OWNER_PASSWORD', 'SEC_USER_AGENT'})
        self.assertEqual(values['SEC_USER_AGENT'], 'IndustryFlow research drill drill@example.invalid')
        self.assertTrue(all(len(values[key]) == 64 for key in lab.SECRET_KEYS))

    def test_sec_user_agent_is_optional(self):
        drill.setup()
        self.assertNotIn('SEC_USER_AGENT', drill.env_values())

    def test_existing_secrets_are_kept(self):
        drill.setup()
        before = drill.ENV_FILE.read_bytes()
        drill.setup('another contact')
        self.assertEqual(drill.ENV_FILE.read_bytes(), before)

    def test_multiline_agent_is_refused(self):
        with self.assertRaises(ValueError):
            drill.setup('contact\nRESEARCH_POSTGRES_PASSWORD=x')
        self.assertFalse(drill.ENV_FILE.exists())


class RedactionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.drill_secret, self.prod_secret = 'd' * 64, 'e' * 64
        (root / 'drill.env').write_text(f'RESEARCH_POSTGRES_PASSWORD={self.drill_secret}\n', encoding='utf-8')
        (root / 'prod.env').write_text(f'RESEARCH_SESSION_SECRET={self.prod_secret}\n', encoding='utf-8')
        for patcher in (mock.patch.object(drill, 'ENV_FILE', root / 'drill.env'),
                        mock.patch.object(lab, 'ENV_FILE', root / 'prod.env')):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_failed_command_output_hides_both_secrets(self):
        script = f'import sys; print("postgresql://industry:{self.drill_secret}@db"); print("{self.prod_secret}", file=sys.stderr); sys.exit(3)'
        with self.assertRaises(RuntimeError) as caught:
            drill.run([sys.executable, '-c', script])
        message = str(caught.exception)
        self.assertNotIn(self.drill_secret, message)
        self.assertNotIn(self.prod_secret, message)
        self.assertIn('postgresql://industry:[REDACTED]@db', message)

    def test_any_failure_leaves_main_without_secrets(self):
        # Errors raised inside shared research_lab code do not go through drill.run; main still redacts them.
        failing = mock.Mock(side_effect=RuntimeError(f'psql: password {self.drill_secret} rejected; {self.prod_secret}'))
        stderr = io.StringIO()
        with mock.patch.object(drill, 'down', failing), mock.patch.object(sys, 'argv', ['research_drill.py', 'down']), \
                mock.patch.object(sys, 'stderr', stderr), self.assertRaises(SystemExit) as caught:
            drill.main()
        self.assertEqual(caught.exception.code, 1)
        self.assertNotIn(self.drill_secret, stderr.getvalue())
        self.assertNotIn(self.prod_secret, stderr.getvalue())
        self.assertIn('psql: password [REDACTED] rejected', stderr.getvalue())


class SharedPathTests(unittest.TestCase):
    def test_bench_and_scale_use_the_drill_module(self):
        self.assertEqual(bench.default_env_file(), drill.ENV_FILE)
        self.assertIs(scale.drill_compose, drill.compose)
        self.assertIs(scale.env_values, drill.env_values)

    def test_no_other_script_names_the_drill_env_file(self):
        for path in (ROOT / 'scripts').glob('*.py'):
            if path.name != 'research_drill.py':
                with self.subTest(script=path.name):
                    self.assertNotIn('.env.research-drill', path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
