"""Drill restore on the backup's baseline image, deploy and rollback rehearsals with production's rules, and the
branch's PostgreSQL checks confined to the drill. No Docker needed."""
import hashlib
import io
import json
import re
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from deploy_fixtures import target_info, CHAIN, OLD, NEW  # noqa: E402
import research_drill as drill  # noqa: E402
import research_lab as lab  # noqa: E402

THEMES = 'public.theme_assessment_versions'


class DrillDir(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        home = self.root / 'drill-home'
        home.mkdir()
        (home / '.env.research-drill').write_text(''.join(f'{k}={"d" * 64}\n' for k in lab.SECRET_KEYS), encoding='utf-8')
        patcher = mock.patch.multiple(drill, DRILL_HOME=home, ENV_FILE=home / '.env.research-drill',
                                      REPORTS=self.root / 'reports', PROD_BACKUPS=self.root / 'backups')
        patcher.start()
        self.addCleanup(patcher.stop)
        self.calls = []

    def patch(self, target, name, **kwargs):
        patcher = mock.patch.object(target, name, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()


class ComposeTests(DrillDir):
    def test_every_call_targets_the_drill_project(self):
        run = self.patch(drill, 'run', return_value=b'')
        drill.compose('ps', tag=OLD[:12])
        args = run.call_args.args[0]
        self.assertEqual(args[:4], ['docker', 'compose', '--project-name', 'industryflow-research-drill'])
        self.assertEqual(args[args.index('-f') + 1], str(ROOT / 'compose.research-drill.yaml'))
        self.assertEqual(args[args.index('--env-file') + 1], str(drill.ENV_FILE))
        self.assertEqual(run.call_args.kwargs['env']['RESEARCH_IMAGE_TAG'], OLD[:12])

    def test_tag_is_required(self):
        with self.assertRaises(ValueError):
            drill.compose('ps', tag=lab.PRE_LEDGER)


class LatestBackupTests(DrillDir):
    def folder(self, stamp, complete=True):
        folder = drill.PROD_BACKUPS / stamp
        folder.mkdir(parents=True)
        if complete:
            (folder / 'manifest.json').write_text('{}', encoding='utf-8')
        return folder

    def test_latest_is_the_newest_complete_backup(self):
        self.folder('20261026T193000Z')
        newest_complete = self.folder('20261027T193000Z')
        self.folder('20261028T193000Z', complete=False)  # a run still writing, or one that failed mid-way
        self.folder('20261029T193000Z.partial')  # a killed backup, even with its manifest already written
        (drill.PROD_BACKUPS / 'notes').mkdir()
        self.assertEqual(drill.resolve_backup('latest'), newest_complete)

    def test_no_backup(self):
        with self.assertRaisesRegex(ValueError, 'No complete backup'):
            drill.resolve_backup('latest')


class BaselineTests(DrillDir):
    def setUp(self):
        super().setUp()
        self.patch(lab, 'resolve_commit', side_effect=lambda commit: {'7ebbc68': OLD}.get(commit, commit))

    def test_manifest_revision_is_the_baseline(self):
        self.assertEqual(drill.baseline_commit({'api_revision': OLD}), OLD)
        self.assertEqual(drill.baseline_commit({'api_revision': OLD}, '7ebbc68'), OLD)

    def test_conflicting_baseline_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'different commit'):
            drill.baseline_commit({'api_revision': NEW}, '7ebbc68')

    def test_old_manifest_needs_the_baseline_commit(self):
        with self.assertRaisesRegex(ValueError, '--baseline-commit'):
            drill.baseline_commit({'api_image': 'sha256:dev'})
        self.assertEqual(drill.baseline_commit({'api_image': 'sha256:dev'}, '7ebbc68'), OLD)


class RestoreTests(DrillDir):
    """restore builds (or reuses) the baseline image before any drill service starts."""
    def setUp(self):
        super().setUp()
        self.backup = self.root / 'backups' / '20261027T193000Z'
        self.backup.mkdir(parents=True)
        files = {'database.dump': b'dump', 'roles.sql': b'roles', 'git.bundle': b'bundle'}
        with tarfile.open(self.backup / 'assets.tar', 'w') as archive:
            info = tarfile.TarInfo('./' + 'a' * 64)
            info.size = 3
            archive.addfile(info, io.BytesIO(b'svg'))
        for name, content in files.items():
            (self.backup / name).write_bytes(content)
        digests = {name: hashlib.sha256((self.backup / name).read_bytes()).hexdigest()
                   for name in [*files, 'assets.tar']}
        self.manifest = {'created_at': '20261027T193000Z', 'files': digests, 'tables': {THEMES: '7:abc'},
                         'active_release': {'release_id': 'r1'}, 'git_refs': ['1 refs/a'], 'api_revision': OLD,
                         'alembic_version': '0017'}
        (self.backup / 'manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')
        self.patch(lab, 'build_images', side_effect=lambda commit: self.calls.append(('build', commit)) or (commit[:12], ['api', 'web']))
        self.patch(drill, 'check', side_effect=lambda tag: self.calls.append(('check', tag)) or ['industryflow-research-drill_pg-data'])
        self.patch(drill, 'compose', side_effect=self.compose)
        self.patch(drill, 'run', side_effect=lambda args, **kw: '' if args[:3] == ['docker', 'volume', 'ls'] else b'')
        for name, value in (('protected_snapshot', {}), ('verify_protected', None), ('preview_snapshot', {}),
                            ('worktree_dirty', False)):
            self.patch(drill, name, return_value=value)
        self.patch(drill, 'db_inventory', return_value=({THEMES: '7:abc'}, {'release_id': 'r1'}))
        self.patch(lab, 'alembic_version', return_value='0017')
        response = mock.MagicMock(status=200)
        response.__enter__.return_value = io.BytesIO(json.dumps({'release_id': 'r1'}).encode())
        self.patch(drill.urllib.request, 'urlopen', return_value=response)
        self.patch(drill.socket.socket, 'connect_ex', return_value=1)

    def compose(self, *args, tag, input=None):
        self.calls.append(('compose', tag, *args))
        if args[:2] == ('ps', '-q'):
            return b'db1\n'
        if 'show-ref' in args:
            return b'1 refs/a\n'
        if 'sha256sum *' in ' '.join(args):
            return (('a' * 64) + '  ' + 'a' * 64 + '\n').encode()
        return b''

    def test_baseline_image_restores_the_backup(self):
        report = drill.restore(str(self.backup))
        build = self.calls.index(('build', OLD))
        first_compose = next(i for i, c in enumerate(self.calls) if c[0] == 'compose')
        self.assertLess(build, first_compose)
        self.assertEqual({c[1] for c in self.calls if c[0] == 'compose'}, {OLD[:12]})
        self.assertEqual((report['baseline_commit'], report['baseline_tag'], report['baseline_built']), (OLD, OLD[:12], ['api', 'web']))
        self.assertTrue(all(value for key, value in report['checks'].items() if key.endswith('_match')), report['checks'])
        self.assertEqual(report['checks']['reader_page_status'], 200)
        self.assertEqual(len(list(drill.REPORTS.glob('restore-*.json'))), 1)
        # Recorded outside the checkout too, so a rehearsal from another worktree finds the same baseline.
        restored = json.loads((drill.DRILL_HOME / 'last-restore.json').read_text(encoding='utf-8'))
        self.assertEqual((restored['baseline_commit'], restored['db_container'], restored['backup']),
                         (OLD, 'db1', '20261027T193000Z'))

    def test_old_manifest_without_baseline_is_refused_before_any_container(self):
        del self.manifest['api_revision']
        (self.backup / 'manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '--baseline-commit'):
            drill.restore(str(self.backup))
        self.assertEqual(self.calls, [])

    def test_tampered_backup_is_refused(self):
        (self.backup / 'roles.sql').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'roles.sql does not match'):
            drill.restore(str(self.backup))
        self.assertEqual(self.calls, [])


class RehearsalHarness(DrillDir):
    db_version = '0017'

    def setUp(self):
        super().setUp()
        self.target = target_info(NEW)
        self.infos = {OLD: target_info(OLD), NEW: self.target}
        self.after = {THEMES: '7:abc', 'public.segments': '17:new'}
        self.smoke = (True, {'health': {'ok': True}})
        self.patch(drill, 'running_revision', return_value=OLD)
        self.patch(lab, 'resolve_commit', side_effect=lambda commit: commit)
        self.patch(lab, 'commit_info', side_effect=lambda commit: self.infos[commit])
        self.patch(drill, 'compose', side_effect=lambda *a, tag, input=None: self.calls.append(('compose', tag, *a)) or b'db1\n')
        self.patch(drill, 'check', side_effect=lambda tag: self.calls.append(('check', tag)))
        self.patch(lab, 'alembic_version', side_effect=lambda container: self.db_version)
        self.patch(lab, 'build_images', side_effect=lambda commit: self.calls.append(('build', commit)) or (commit[:12], []))
        self.patch(lab, 'running_services', return_value={'db': {}, 'api': {}, 'web': {}})
        self.smoke_kwargs = []
        self.patch(lab, 'smoke_checks', side_effect=lambda *a, **kw: self.smoke_kwargs.append(kw) or
                   self.calls.append(('smoke', *a[1:5])) or self.smoke)
        self.patch(drill, 'db_inventory', side_effect=[({THEMES: '7:abc', 'public.segments': '17:old'}, {}), (self.after, {})])
        for name, value in (('protected_snapshot', {}), ('verify_protected', None), ('preview_snapshot', {}),
                            ('worktree_dirty', True)):
            self.patch(drill, name, return_value=value)

    def composed(self):
        return [c[2:] for c in self.calls if c[0] == 'compose' and c[2:4] != ('ps', '-q')]


class DeployRehearsalTests(RehearsalHarness):
    def test_production_steps_on_the_drill_project(self):
        report = drill.deploy_rehearsal(NEW)
        self.assertEqual(self.composed(), [('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'initialize'),
                                           ('up', '-d', '--no-deps', '--wait', 'api', 'web')])
        self.assertIn(('smoke', 'industryflow-research-drill', NEW[:12], NEW, '0017'), self.calls)
        self.assertLess(self.calls.index(('build', NEW)), next(i for i, c in enumerate(self.calls) if 'initialize' in c))

    def test_db_working_dir_is_not_compared_in_the_drill(self):
        drill.deploy_rehearsal(NEW)
        self.assertEqual(self.smoke_kwargs, [{'working_dir_skip': ('db',)}])

    def test_report_fields(self):
        report = drill.deploy_rehearsal(NEW)
        for key in ('commit', 'tag', 'baseline_commit', 'worktree_dirty', 'alembic', 'tables', 'theme_assessment_versions',
                    'smoke_ok', 'smoke', 'contract_revisions_added', 'report'):
            self.assertIn(key, report)
        self.assertEqual(report['commit'], NEW)
        self.assertIs(report['worktree_dirty'], True)
        self.assertEqual(report['alembic'], {'before': '0017', 'after': '0017', 'image_head': '0017'})
        self.assertEqual(report['tables']['changed'], {'public.segments': {'rows_before': 17, 'rows_after': 17,
                                                                           'md5_before': 'old', 'md5_after': 'new'}})
        self.assertEqual(report['tables']['unchanged'], 1)
        self.assertEqual(report['theme_assessment_versions'], {'before': 7, 'after': 7, 'added': 0})
        saved = json.loads(Path(report['report']).read_text(encoding='utf-8'))
        self.assertEqual(saved['commit'], NEW)

    def test_contract_needs_allow_contract_like_production(self):
        self.infos[NEW] = target_info(NEW, chain=[*CHAIN, '0018'], contracts=('0009', '0017', '0018'))
        with self.assertRaisesRegex(lab.Refused, r'Contract migration\(s\) 0018'):
            drill.deploy_rehearsal(NEW)
        self.assertEqual(self.composed(), [])
        drill.db_inventory.side_effect = [({}, {}), ({}, {})]
        self.assertEqual(drill.deploy_rehearsal(NEW, allow_contract=True)['contract_revisions_added'], ['0018'])

    def test_database_off_the_chain_is_refused(self):
        self.db_version = '0099'
        with self.assertRaisesRegex(lab.Refused, 'not on the migration chain'):
            drill.deploy_rehearsal(NEW)

    def test_smoke_failure_keeps_the_report(self):
        self.smoke = (False, {'next': {'ok': False, 'status': 500}})
        with self.assertRaisesRegex(RuntimeError, 'Smoke check failed'):
            drill.deploy_rehearsal(NEW)
        [path] = drill.REPORTS.glob('deploy-rehearsal-*.json')
        self.assertIs(json.loads(path.read_text(encoding='utf-8'))['smoke_ok'], False)


class RollbackRehearsalTests(RehearsalHarness):
    def setUp(self):
        super().setUp()
        self.patch(drill, 'running_revision', return_value=NEW)
        (drill.DRILL_HOME / 'last-restore.json').write_text(
            json.dumps({'backup': '20261027T193000Z', 'baseline_commit': OLD, 'db_container': 'db1'}), encoding='utf-8')

    def test_back_to_the_baseline_without_initialize(self):
        report = drill.rollback_rehearsal()
        self.assertEqual(self.composed(), [('up', '-d', '--no-deps', '--wait', 'api', 'web')])
        self.assertIn(('smoke', 'industryflow-research-drill', OLD[:12], OLD, '0017'), self.calls)
        self.assertEqual((report['judgement'], report['initialize_run'], report['migrations_between']), ('expand-only', False, []))
        self.assertEqual(report['theme_assessment_versions']['added'], 0)

    def test_db_working_dir_is_not_compared_in_the_drill(self):
        drill.rollback_rehearsal()
        self.assertEqual(self.smoke_kwargs, [{'working_dir_skip': ('db',)}])

    def test_restore_of_another_db_is_not_used_as_the_baseline(self):
        # A later restore, or another worktree's drill: the recorded DB container is not the one running.
        (drill.DRILL_HOME / 'last-restore.json').write_text(
            json.dumps({'backup': 'older', 'baseline_commit': 'c' * 40, 'db_container': 'db-from-another-restore'}),
            encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'pass --commit'):
            drill.rollback_rehearsal()
        self.assertEqual(self.composed(), [])
        self.assertEqual(drill.rollback_rehearsal(OLD)['to_commit'], OLD)

    def test_expand_migration_between(self):
        self.infos[NEW] = target_info(NEW, chain=[*CHAIN, '0018'])
        self.db_version = '0018'
        self.assertEqual(drill.rollback_rehearsal()['migrations_between'], ['0018'])

    def test_contract_between_is_refused_like_production(self):
        before_0017 = 'c' * 40
        self.infos[before_0017] = target_info(before_0017, chain=CHAIN[:-1], contracts=('0009',))
        with self.assertRaises(lab.Refused) as caught:
            drill.rollback_rehearsal(before_0017)
        message = str(caught.exception)
        self.assertIn('crosses contract migration(s) 0017', message)
        self.assertIn('20261027T193000Z (the backup this drill was restored from)', message)
        self.assertEqual(self.composed(), [])
        [path] = drill.REPORTS.glob('rollback-rehearsal-*.json')
        self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['judgement'], 'refused')

    def test_prefect_change_is_refused(self):
        self.infos[OLD] = target_info(OLD, prefect='3.8.7')
        with self.assertRaisesRegex(lab.Refused, 'Prefect would change'):
            drill.rollback_rehearsal()


class PostgresCheckTests(DrillDir):
    def setUp(self):
        super().setUp()
        self.patch(lab, 'resolve_commit', side_effect=lambda commit: commit)
        self.patch(lab, 'build_images', return_value=(NEW[:12], []))
        self.patch(drill, 'check', return_value=[])
        for name, value in (('protected_snapshot', {}), ('verify_protected', None), ('preview_snapshot', {}),
                            ('worktree_dirty', False)):
            self.patch(drill, name, return_value=value)
        self.compose = self.patch(drill, 'compose', side_effect=self.fake_compose)

    def fake_compose(self, *args, tag, input=None):
        if args[:2] == ('ps', '-q'):
            return b'db1\n'
        if 'app.research_rebuild_check' in args:
            return json.dumps({'entities': 254, 'search_plans': ['big']}).encode()
        return b'....\n===== 241 passed, 3 skipped in 80.00s =====\n'

    def test_pg_check_runs_the_branch_image_in_the_drill_bootstrap(self):
        report = drill.pg_check(NEW, 'reader-navigation')
        args = self.compose.call_args_list[-1]
        self.assertEqual(args.kwargs['tag'], NEW[:12])
        self.assertEqual(args.args[:8], ('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', '-e', 'PYTHONUNBUFFERED=1'))
        self.assertEqual(args.args[8:], ('bootstrap', 'python', '-m', 'app.research_pg_checks', '--suite', 'reader-navigation'))
        self.assertEqual(report['summary'], '241 passed, 3 skipped in 80.00s')
        self.assertIs(report['passed'], True)
        self.assertTrue(Path(report['report']).with_suffix('.log').exists())

    def test_failing_suite_still_leaves_its_report_and_log(self):
        self.compose.side_effect = lambda *args, tag, input=None: (
            b'db1\n' if args[:2] == ('ps', '-q') else
            (_ for _ in ()).throw(RuntimeError('docker compose failed (exit 1): ..E.\n== 157 passed, 1 error in 459.21s ==')))
        with self.assertRaisesRegex(RuntimeError, r'pg-check failed \(157 passed, 1 error in 459.21s\)'):
            drill.pg_check(NEW)
        [path] = drill.REPORTS.glob('pg-check-*.json')
        saved = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual((saved['passed'], saved['summary']), (False, '157 passed, 1 error in 459.21s'))
        self.assertIn('1 error', path.with_suffix('.log').read_text(encoding='utf-8'))

    def test_rebuild_check_writes_to_the_drill(self):
        archive = self.patch(drill, 'run', return_value=b'tar')
        report = drill.rebuild_check(NEW)
        self.assertEqual(archive.call_args.args[0][:4], ['git', '-c', 'core.autocrlf=false', 'archive'])
        call = self.compose.call_args_list[-1]
        self.assertIn('bootstrap', call.args)
        self.assertEqual(call.kwargs['input'], b'tar')
        self.assertEqual(report['result'], {'entities': 254})

    def test_drill_db_host_and_volumes_belong_to_the_drill(self):
        config = yaml.safe_load((ROOT / 'compose.research-drill.yaml').read_text(encoding='utf-8'))
        self.assertEqual(config['name'], 'industryflow-research-drill')
        bootstrap = config['services']['bootstrap']
        self.assertIn('@db:5432/industry_research', bootstrap['environment']['DATABASE_URL'])
        self.assertEqual(bootstrap['networks'], ['app'])
        for volume in bootstrap['volumes']:
            name = volume.split(':')[0]
            self.assertIn(name, config['volumes'], 'a named volume of the drill project, not a bind or external volume')
            self.assertFalse((config['volumes'][name] or {}).get('external'))
        self.assertEqual(set(config['networks']), {'app', 'offline'})

    def test_production_script_no_longer_has_these_actions(self):
        for action in ('pg-check', 'rebuild-check'):
            self.assertNotIn(action, lab.ACTIONS)
            self.assertIn(action, drill.ACTIONS)


class DocumentedCommandTests(unittest.TestCase):
    """Every drill command the docs show uses an action and flags the parser accepts."""
    DOCS = ('research-backup.md', 'research-deployment.md', 'research-performance.md', 'research-integration.md',
            'research-lab.md')

    def test_documented_commands_match_the_parser(self):
        options = {flag for action in drill.build_parser()._actions for flag in action.option_strings}
        seen = 0
        for name in self.DOCS:
            text = (ROOT / 'docs' / name).read_text(encoding='utf-8')
            for match in re.finditer(r'research_drill\.py ([a-z-]+)([^;#`\n|）]*)', text):
                seen += 1
                with self.subTest(doc=name, command=match.group(0)):
                    self.assertIn(match.group(1), drill.ACTIONS)
                    for flag in re.findall(r'--[a-z-]+', match.group(2)):
                        self.assertIn(flag, options)
        self.assertGreater(seen, 10)


if __name__ == '__main__':
    unittest.main()
