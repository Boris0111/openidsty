"""Shared fakes for the deployment tests: a temporary deployment directory and recorded deployments.
No Docker, Git remote or database is used; every external call is patched by the tests."""
import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_lab as lab

OLD = 'a' * 40
NEW = 'b' * 40
CHAIN = [f'{n:04d}' for n in range(1, 18)]


def deployment_dir(test, marked=True):
    """Point every deployment path of research_lab at a fresh temporary directory."""
    temp = tempfile.TemporaryDirectory()
    test.addCleanup(temp.cleanup)
    root = Path(temp.name)
    deployments = root / 'deployments'
    patcher = mock.patch.multiple(lab, ROOT=root, DEPLOYMENTS=deployments, HOME_FILE=deployments / 'home.json',
                                  LEDGER=deployments / 'ledger.jsonl', LOCK=deployments / '.lock',
                                  HANDOVER=deployments / '.handover', ENV_FILE=root / '.env.research',
                                  BACKUP_ROOT=root / 'backups' / 'research')
    patcher.start()
    test.addCleanup(patcher.stop)
    if marked:
        deployments.mkdir()
        lab.HOME_FILE.write_text(json.dumps({'path': str(root), 'secondary': str(root / 'secondary')}), encoding='utf-8')
    return root


def deploy_record(commit=OLD, chain=CHAIN, contracts=('0009', '0017'), prefect='3.8.8', **extra):
    return {'kind': 'deploy', 'outcome': 'succeeded', 'replaced': True, 'commit': commit, 'tag': commit[:12],
            'images': {'api': 'sha256:api-' + commit[:4], 'web': 'sha256:web-' + commit[:4]},
            'alembic_head': chain[-1], 'migrations': list(chain), 'contract_revisions': list(contracts),
            'prefect_version': prefect, 'backup': '20261027T000000Z', 'contract_boundary': False, **extra}


def target_info(commit=NEW, chain=CHAIN, contracts=('0009', '0017'), prefect='3.8.8'):
    """commit_info() of a commit, without Git."""
    return {'commit': commit, 'alembic_head': chain[-1], 'migrations': list(chain),
            'contract_revisions': list(contracts), 'prefect_version': prefect}


def services(record, scheduler=False, reader=False, **overrides):
    """Running services exactly as the record describes them."""
    running = {'db': {'container': 'db1', 'image_id': 'sha256:pg', 'revision': None, 'working_dir': str(lab.ROOT)}}
    names = ['api', 'web', *(['prefect', 'worker'] if scheduler else []), *(['reader'] if reader else [])]
    for name in names:
        running[name] = {'container': name + '1', 'image_id': record['images'][lab.image_kind(name)],
                         'revision': record['commit'], 'working_dir': str(lab.ROOT)}
    for name, values in overrides.items():
        running[name] = {**running.get(name, {}), **values}
    return running
