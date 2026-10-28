"""Backup manifest records what actually runs; rollback boundaries survive pruning; refusals are logged."""
import calendar
import json
from pathlib import Path
import sys
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import lab, deployment_dir, deploy_record, OLD, NEW  # noqa: E402

TAG = OLD[:12]
INVENTORY = {'public.segments': '12:abc', 'research.research_releases': '4:def'}
HEAD = {'release_id': 'a5df290c-0b6d-5011-b842-ae73cd8a1f99', 'generation': '4', 'content_hash': 'f' * 64, 'git_commit': 'c' * 40}


class BackupManifestTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        self.tags = []
        api = {'container': 'api1', 'image_id': 'sha256:running-api', 'revision': OLD, 'working_dir': str(self.root)}
        for name, value in (('protected_snapshot', {}), ('verify_protected', None), ('db_inventory', (INVENTORY, HEAD)),
                            ('running_services', {'api': api}), ('alembic_version', '0017')):
            patcher = mock.patch.object(lab, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(lab, 'compose', side_effect=self.compose)
        patcher.start()
        self.addCleanup(patcher.stop)

    def compose(self, *args, tag, input=None):
        self.tags.append(tag)
        if args[:2] == ('ps', '-q'):
            return b'db1\n'
        if 'show-ref' in args:
            return b'1234 refs/research/releases/a5df290c\n'
        return ('content of ' + ' '.join(args)).encode()

    def manifest(self, result):
        return json.loads((Path(result['backup']) / 'manifest.json').read_text(encoding='utf-8'))

    def test_manifest_records_the_running_api_and_schema(self):
        manifest = self.manifest(lab.backup(tag=TAG))
        self.assertEqual(manifest['api_image'], 'sha256:running-api')
        self.assertEqual(manifest['api_revision'], OLD)
        self.assertEqual(manifest['alembic_version'], '0017')
        self.assertIs(manifest['rollback_boundary'], False)
        self.assertEqual(manifest['contract_revisions'], [])
        self.assertEqual(set(self.tags), {TAG}, 'every tool container uses the deployed image')

    def test_existing_fields_are_kept(self):
        manifest = self.manifest(lab.backup(tag=TAG))
        for key in ('created_at', 'duration_seconds', 'files', 'sizes', 'active_release', 'tables', 'git_refs', 'excluded'):
            self.assertIn(key, manifest)
        self.assertEqual(set(manifest['files']), {'database.dump', 'roles.sql', 'git.bundle', 'assets.tar'})
        self.assertEqual(manifest['active_release'], HEAD)
        self.assertEqual(manifest['tables'], INVENTORY)

    def test_contract_deploy_backup_is_a_boundary(self):
        manifest = self.manifest(lab.backup(tag=TAG, boundary=['0018']))
        self.assertIs(manifest['rollback_boundary'], True)
        self.assertEqual(manifest['contract_revisions'], ['0018'])

    def test_written_as_partial_and_renamed_when_complete(self):
        result = lab.backup(str(self.root / 'secondary'), tag=TAG)
        stamp = Path(result['backup']).name
        self.assertRegex(stamp, r'^\d{8}T\d{6}Z$')
        for root in (lab.BACKUP_ROOT, self.root / 'secondary'):
            self.assertEqual([p.name for p in root.iterdir() if p.is_dir()], [stamp])

    def test_leftover_partial_folders_are_removed(self):
        for root in (lab.BACKUP_ROOT, self.root / 'secondary'):
            leftover = root / '20261027T033000Z.partial'
            leftover.mkdir(parents=True)
            (leftover / 'database.dump').write_bytes(b'half a dump')
        result = lab.backup(str(self.root / 'secondary'), tag=TAG)
        self.assertEqual(sorted(result['removed_partial'].values()), [['20261027T033000Z.partial']] * 2)
        for root in (lab.BACKUP_ROOT, self.root / 'secondary'):
            self.assertFalse(list(root.glob('*.partial')))

    def test_failed_backup_leaves_no_folder(self):
        original = self.compose

        def failing(*args, tag, input=None):
            if 'show-ref' in args:
                raise RuntimeError('git show-ref failed')
            return original(*args, tag=tag, input=input)
        lab.compose.side_effect = failing
        with self.assertRaisesRegex(RuntimeError, 'show-ref'):
            lab.backup(tag=TAG)
        self.assertEqual([p.name for p in lab.BACKUP_ROOT.iterdir() if p.is_dir()], [])
        log = (lab.BACKUP_ROOT / 'backup-log.jsonl').read_text(encoding='utf-8')
        self.assertIn('failed: git show-ref failed', log)

    def test_secondary_copy_and_log(self):
        secondary = self.root / 'secondary'
        result = lab.backup(str(secondary), tag=TAG)
        stamp = Path(result['backup']).name
        self.assertEqual(sorted(p.name for p in (secondary / stamp).iterdir()),
                         ['assets.tar', 'database.dump', 'git.bundle', 'manifest.json', 'roles.sql'])
        log = [json.loads(line) for line in (lab.BACKUP_ROOT / 'backup-log.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(log[-1]['status'], 'ok')


class PruneTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        self.now = calendar.timegm(time.strptime('20261128T000000Z', '%Y%m%dT%H%M%SZ'))

    def folder(self, stamp, manifest):
        folder = lab.BACKUP_ROOT / stamp
        folder.mkdir(parents=True)
        if manifest is not None:
            (folder / 'manifest.json').write_text(manifest if isinstance(manifest, str) else json.dumps(manifest), encoding='utf-8')
        return folder

    def test_boundaries_survive_and_old_backups_go(self):
        self.folder('20261001T033000Z', {'rollback_boundary': False})
        self.folder('20261002T033000Z', {})  # manifests written before this change have no flag
        boundary = self.folder('20261003T033000Z', {'rollback_boundary': True, 'contract_revisions': ['0018']})
        unreadable = self.folder('20261004T033000Z', '{not json')
        incomplete = self.folder('20261005T033000Z', None)
        partial = self.folder('20261006T033000Z.partial', {})  # left for the next backup's cleanup, not for prune
        recent = self.folder('20261127T033000Z', {'rollback_boundary': False})
        removed = lab.prune(lab.BACKUP_ROOT, 30, self.now)
        self.assertEqual(removed, ['20261001T033000Z', '20261002T033000Z'])
        for kept in (boundary, unreadable, incomplete, recent, partial):
            self.assertTrue(kept.exists(), kept.name)


class BackupActionTests(unittest.TestCase):
    def setUp(self):
        self.root = deployment_dir(self)
        lab.append_record(deploy_record())

    def test_refused_backup_is_logged(self):
        with mock.patch.object(lab, 'guard_problems', return_value=['HEAD bbbbbbbbbbbb is not the deployed commit aaaaaaaaaaaa']), \
                mock.patch.object(sys, 'argv', ['research_lab.py', 'backup']):
            with self.assertRaises(lab.Refused):
                lab.main()
        [line] = (lab.BACKUP_ROOT / 'backup-log.jsonl').read_text(encoding='utf-8').splitlines()
        entry = json.loads(line)
        self.assertTrue(entry['status'].startswith('refused: Refusing to backup'))
        self.assertIn('HEAD bbbbbbbbbbbb', entry['status'])

    def test_backup_holds_the_lock(self):
        held = []
        with mock.patch.object(lab, 'guard_problems', return_value=[]), mock.patch.object(lab, 'validate', return_value={}), \
                mock.patch.object(lab, 'backup', side_effect=lambda *a, **k: held.append(lab.lock_held()) or {}), \
                mock.patch.object(sys, 'argv', ['research_lab.py', 'backup']), mock.patch('builtins.print'):
            lab.main()
        self.assertEqual(held, [True])
        self.assertFalse(lab.lock_held())

    def test_backup_while_a_deploy_holds_the_lock(self):
        with lab.deployment_lock(), mock.patch.object(lab.time, 'sleep'), \
                mock.patch.object(lab.time, 'time', side_effect=[0, 1000, 2000, 4000]):
            with self.assertRaisesRegex(lab.Refused, 'holds deployments/.lock'), lab.production('backup'):
                self.fail('backup ran while a deploy held the lock')


if __name__ == '__main__':
    unittest.main()
