"""Images are built only from `git archive <commit>`, tagged and labelled with the commit; no Docker needed."""
import fnmatch
import json
from pathlib import Path
import shlex
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_lab as lab

COMMIT = '0123456789abcdef0123456789abcdef01234567'
INFO = {'commit': COMMIT, 'alembic_head': '0017', 'migrations': [f'{n:04d}' for n in range(1, 18)],
        'contract_revisions': ['0009', '0017'], 'prefect_version': '3.8.8'}
LABELS = {'org.opencontainers.image.revision': COMMIT, 'io.industryflow.alembic-head': '0017',
          'io.industryflow.contract-revisions': '0009,0017', 'io.industryflow.prefect-version': '3.8.8',
          'io.industryflow.build': 'git-archive'}


class FakeDocker:
    """Answers the commands build_images runs; images maps a name to its labels."""
    def __init__(self, images=None):
        self.images, self.calls = dict(images or {}), []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if args[:2] == ['git', 'rev-parse']:
            return COMMIT + '\n'
        if args[:4] == ['git', '-c', 'core.autocrlf=false', 'archive']:
            return b'tar-bytes'
        if args[:3] == ['docker', 'image', 'ls']:
            return 'sha256:abc\n' if args[-1] in self.images else ''
        if args[:3] == ['docker', 'image', 'inspect']:
            return json.dumps(self.images[args[3]])
        if args[:2] == ['docker', 'build']:
            return b''
        raise AssertionError(f'unexpected command {args}')

    def builds(self):
        return [(args, kwargs) for args, kwargs in self.calls if args[:2] == ['docker', 'build']]


def build(docker):
    with mock.patch.object(lab, 'run', docker), mock.patch.object(lab, 'commit_info', return_value=INFO):
        return lab.build_images(COMMIT)


class BuildTests(unittest.TestCase):
    def test_archive_and_build_arguments(self):
        docker = FakeDocker()
        tag, built = build(docker)
        self.assertEqual((tag, built), (COMMIT[:12], ['api', 'web']))
        archives = [c for c in docker.calls if 'archive' in c[0]]
        self.assertEqual(len(archives), 1, 'one archive feeds both builds')
        self.assertEqual(archives[0][0], ['git', '-c', 'core.autocrlf=false', 'archive', '--format=tar', COMMIT])
        self.assertEqual(archives[0][1]['cwd'], lab.ROOT)
        (api, api_kwargs), (web, web_kwargs) = docker.builds()
        self.assertEqual(api[:6], ['docker', 'build', '-f', 'backend/Dockerfile', '-t', f'industryflow-research-api:{COMMIT[:12]}'])
        self.assertEqual(web[:6], ['docker', 'build', '-f', 'frontend/Dockerfile', '-t', f'industryflow-research-web:{COMMIT[:12]}'])
        for args, kwargs in docker.builds():
            self.assertEqual(args[-1], '-', 'the build context is the tar on stdin')
            self.assertEqual(kwargs['input'], b'tar-bytes')
            self.assertNotIn('cwd', kwargs, 'nothing is read from a working tree')

    def test_label_values(self):
        docker = FakeDocker()
        build(docker)
        for args, _ in docker.builds():
            labels = dict(flag[len('--label='):].split('=', 1) for flag in args if flag.startswith('--label='))
            self.assertEqual({k: v for k, v in labels.items() if k != 'org.opencontainers.image.created'}, LABELS)
            self.assertRegex(labels['org.opencontainers.image.created'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')

    def test_matching_labels_are_reused(self):
        images = {f'industryflow-research-{kind}:{COMMIT[:12]}': {**LABELS, 'org.opencontainers.image.created': 'earlier'}
                  for kind in ('api', 'web')}
        docker = FakeDocker(images)
        self.assertEqual(build(docker), (COMMIT[:12], []))
        self.assertEqual(docker.builds(), [])
        self.assertFalse(any('archive' in args for args, _ in docker.calls))

    def test_contract_label_from_older_rules_is_still_the_same_image(self):
        # Stricter lint rules change contract-revisions for old commits; that never makes the image a different one.
        images = {f'industryflow-research-{kind}:{COMMIT[:12]}': {**LABELS, 'io.industryflow.contract-revisions': '0009'}
                  for kind in ('api', 'web')}
        docker = FakeDocker(images)
        self.assertEqual(build(docker), (COMMIT[:12], []))
        self.assertEqual(docker.builds(), [])

    def test_missing_half_is_built(self):
        docker = FakeDocker({f'industryflow-research-api:{COMMIT[:12]}': LABELS})
        self.assertEqual(build(docker)[1], ['web'])

    def test_different_labels_are_refused_not_overwritten(self):
        for key in ('io.industryflow.alembic-head', 'org.opencontainers.image.revision', 'io.industryflow.build'):
            docker = FakeDocker({f'industryflow-research-api:{COMMIT[:12]}': {**LABELS, key: 'other'}})
            with self.subTest(key=key), self.assertRaisesRegex(lab.Refused, key):
                build(docker)
            self.assertEqual(docker.builds(), [])

    def test_a_working_tree_dev_image_is_never_reused(self):
        # A pre-ledger :dev build has no labels at all.
        docker = FakeDocker({f'industryflow-research-api:{COMMIT[:12]}': {}})
        with self.assertRaises(lab.Refused):
            build(docker)


class CommitInfoTests(unittest.TestCase):
    def test_head_commit(self):
        info = lab.commit_info(lab.git_head())
        self.assertEqual(info['alembic_head'], info['migrations'][-1])
        self.assertEqual(info['prefect_version'], '3.8.8')
        self.assertIn('0017', info['contract_revisions'])
        self.assertEqual(lab.image_labels(info)['org.opencontainers.image.revision'], info['commit'])


class DockerfileSourceTests(unittest.TestCase):
    """A build from git archive sees only committed files, so every COPY source must be tracked."""
    def test_copy_sources_are_tracked(self):
        tracked = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
        for dockerfile in lab.DOCKERFILES.values():
            for line in (ROOT / dockerfile).read_text(encoding='utf-8').splitlines():
                words = shlex.split(line)
                if not words or words[0] != 'COPY' or any(w.startswith('--from=') for w in words):
                    continue
                for source in [w for w in words[1:-1] if not w.startswith('--')]:
                    with self.subTest(dockerfile=dockerfile, source=source):
                        self.assertTrue(any(fnmatch.fnmatch(path, source) or path.startswith(source.rstrip('/') + '/')
                                            for path in tracked), f'{source} is not in version control')


if __name__ == '__main__':
    unittest.main()
