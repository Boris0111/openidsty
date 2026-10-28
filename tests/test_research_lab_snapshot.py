"""The public snapshot runs in a throwaway API container and never prints or ships secret values."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_lab as lab

TAG = '0123456789ab'
RELEASE = 'a5df290c-0b6d-5011-b842-ae73cd8a1f99'


class SnapshotCommandTests(unittest.TestCase):
    def test_command_mounts_only_the_output_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            command = lab.snapshot_command(folder, RELEASE)
        self.assertEqual(command[:6], ['run', '--rm', '--no-deps', '-T', '-v', Path(folder).resolve().as_posix() + ':/export'])
        self.assertEqual(command[6:], ['api', 'python', '-m', 'app.public_snapshot', '--out', '/export', '--release-id', RELEASE])
        self.assertNotIn('--service-ports', command)

    def test_release_id_must_be_a_full_uuid(self):
        for value in ('latest', 'a5df290c', RELEASE + ';rm'):
            with self.assertRaises(ValueError):
                lab.snapshot_command('.', value)

    def test_secret_in_export_fails_and_is_not_echoed(self):
        secret = 'f' * 64
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            env = root / '.env.research'
            env.write_text(f'RESEARCH_SESSION_SECRET={secret}\n', encoding='utf-8')
            folder = root / 'public-snapshot' / RELEASE
            folder.mkdir(parents=True)
            (folder / 'manifest.json').write_text(json.dumps({'note': secret}), encoding='utf-8')
            printed = json.dumps({'folder': RELEASE, 'published_at': '2026-10-20', 'counts': {}}).encode()
            with mock.patch.object(lab, 'ROOT', root), mock.patch.object(lab, 'ENV_FILE', env), mock.patch.object(lab, 'compose', return_value=printed):
                with self.assertRaises(RuntimeError) as caught:
                    lab.public_snapshot(tag=TAG)
            self.assertIn('manifest.json: secret value', str(caught.exception))
            self.assertNotIn(secret, str(caught.exception))

    def test_clean_export_reports_folder_and_counts(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            env = root / '.env.research'
            env.write_text('RESEARCH_SESSION_SECRET=' + 'f' * 64 + '\n', encoding='utf-8')
            (root / 'public-snapshot' / RELEASE).mkdir(parents=True)
            printed = b'log line\n' + json.dumps({'folder': RELEASE, 'published_at': '2026-10-20', 'counts': {'companies': 95}}).encode()
            with mock.patch.object(lab, 'ROOT', root), mock.patch.object(lab, 'ENV_FILE', env), mock.patch.object(lab, 'compose', return_value=printed):
                result = lab.public_snapshot(tag=TAG)
        self.assertEqual(result['counts'], {'companies': 95})
        self.assertTrue(result['folder'].endswith(RELEASE))


if __name__ == '__main__':
    unittest.main()
