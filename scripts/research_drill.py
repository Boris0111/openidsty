"""Restore drill in a separate Compose project: restore a research backup into new DB/Git/asset volumes,
verify it against the backup manifest and time it. Never touches the preview or the original services.

python scripts/research_drill.py setup
python scripts/research_drill.py restore --backup backups/research/<stamp>
python scripts/research_drill.py owner      # drill-only owner credential from .env.research-drill
python scripts/research_drill.py down       # remove the drill containers and volumes only
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import socket
import tarfile
import time
import urllib.request

from research_lab import (ROOT, SECRET_KEYS, GIT_REPO, ASSET_DIR, run, sha256_file, db_inventory,
                          protected_snapshot, verify_protected)

PROJECT = 'industryflow-research-drill'
ENV_FILE = ROOT / '.env.research-drill'
PORTS = {'api': (8016, 8000), 'web': (3016, 3010)}
REPORTS = ROOT / '.work/research-drill'


def env_values():
    return dict(line.split('=', 1) for line in ENV_FILE.read_text(encoding='utf-8').splitlines()
                if line and not line.startswith('#'))


def compose(*args, input=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith('RESEARCH_')}
    env.pop('COMPOSE_PROFILES', None)
    return run(['docker', 'compose', '--project-name', PROJECT, '--env-file', str(ENV_FILE),
                '-f', str(ROOT / 'compose.research-drill.yaml'), *args], cwd=ROOT, env=env, input=input)


def setup():
    if not ENV_FILE.exists():
        preview = dict(line.split('=', 1) for line in (ROOT / '.env.research').read_text(encoding='utf-8').splitlines()
                       if line and not line.startswith('#'))
        # Fresh drill secrets; only the public SEC contact string is shared with the preview.
        lines = [f'{key}={secrets.token_hex(32)}' for key in SECRET_KEYS]
        lines.append('DRILL_OWNER_PASSWORD=' + secrets.token_urlsafe(24))
        if preview.get('SEC_USER_AGENT'):
            lines.append('SEC_USER_AGENT=' + preview['SEC_USER_AGENT'])
        with ENV_FILE.open('x', encoding='utf-8', newline='\n') as output:
            output.write('\n'.join(lines) + '\n')


def check():
    setup()
    config = json.loads(compose('--profile', 'tools', 'config', '--format', 'json'))
    services = config['services']
    if config.get('name') != PROJECT or set(services) != {'db', 'api', 'web', 'bootstrap', 'worker'}:
        raise ValueError('Unexpected drill project')
    for name, service in services.items():
        if 'container_name' in service or service.get('network_mode'):
            raise ValueError('Fixed container name or host networking forbidden')
        if name != 'db' and service['image'] not in ('industryflow-research-api:dev', 'industryflow-research-web:dev'):
            raise ValueError('Unexpected image for ' + name)
        if any(v['type'] == 'bind' for v in service.get('volumes', [])):
            raise ValueError('Bind mounts are not allowed in the drill')
        ports = [(p.get('host_ip'), int(p['published']), int(p['target'])) for p in service.get('ports', [])]
        if ports != ([('127.0.0.1', *PORTS[name])] if name in PORTS else []):
            raise ValueError('Unsafe port binding for ' + name)
    for kind in ('volumes', 'networks'):
        for resource in config.get(kind, {}).values():
            if resource.get('external') or not resource.get('name', '').startswith(PROJECT + '_'):
                raise ValueError(f'Unsafe {kind} namespace')
    return sorted(v['name'] for v in config['volumes'].values())


def preview_snapshot():
    names = sorted(n for n in run(['docker', 'ps', '-a', '--format', '{{.Names}}'], text=True).splitlines()
                   if n.startswith('industryflow-research-') and not n.startswith(PROJECT + '-'))
    records = json.loads(run(['docker', 'inspect', *names], text=True)) if names else []
    return {r['Name']: [r['Id'], r['State']['StartedAt'], r['RestartCount']] for r in records}


def restore(backup):
    folder = Path(backup).resolve()
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    for name, digest in manifest['files'].items():
        if sha256_file(folder / name) != digest:
            raise ValueError(f'Backup file {name} does not match its manifest')
    with tarfile.open(folder / 'assets.tar') as archive:
        expected_assets = sum(1 for member in archive.getmembers() if member.isfile())
    volumes = check()
    existing = set(run(['docker', 'volume', 'ls', '--format', '{{.Name}}'], text=True).split())
    if existing & set(volumes):
        raise ValueError('Drill volumes already exist; run down first so the drill starts empty')
    for port, _ in PORTS.values():
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', port)) == 0:
                raise RuntimeError(f'Drill port {port} already occupied')
    protected, preview = protected_snapshot(), preview_snapshot()
    timings, started = {}, time.time()
    compose('up', '-d', '--wait', 'db')
    timings['db_ready'] = time.time() - started
    db = compose('ps', '-q', 'db').decode().strip()
    # The cluster already has the superuser; other roles are created without passwords and get
    # drill passwords from research_roles below. Errors for pre-existing roles are expected.
    run(['docker', 'exec', '-i', db, 'psql', '-U', 'industry', '-d', 'postgres', '-q'],
        input=(folder / 'roles.sql').read_bytes())
    compose('cp', str(folder / 'database.dump'), 'db:/tmp/restore.dump')
    compose('exec', '-T', 'db', 'pg_restore', '-U', 'industry', '-d', 'industry_research', '--exit-on-error', '/tmp/restore.dump')
    compose('exec', '-T', 'db', 'rm', '/tmp/restore.dump')
    tool = ('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'bootstrap')
    compose(*tool, 'python', '-m', 'app.research_roles')
    timings['database_restored'] = time.time() - started
    compose(*tool, 'sh', '-c', 'cat > /tmp/restore.bundle && '
            f'git clone -q --mirror /tmp/restore.bundle {GIT_REPO} && git -C {GIT_REPO} config --remove-section remote.origin',
            input=(folder / 'git.bundle').read_bytes())
    compose(*tool, 'tar', '-C', ASSET_DIR, '-xf', '-', input=(folder / 'assets.tar').read_bytes())
    timings['git_assets_restored'] = time.time() - started
    compose('up', '-d', '--wait', 'api', 'web')
    timings['serving'] = time.time() - started
    inventory, head = db_inventory(db)
    refs = compose(*tool, 'git', '-C', GIT_REPO, 'show-ref').decode().splitlines()
    assets = compose(*tool, 'sh', '-c', f'cd {ASSET_DIR} && sha256sum *').decode().split('\n')
    bad_assets = [line for line in assets if line and line.split()[0] != line.split()[-1]]
    with urllib.request.urlopen('http://127.0.0.1:8016/api/v2/manifest', timeout=30) as response:
        served = json.load(response)
    page = urllib.request.urlopen('http://127.0.0.1:3016/next', timeout=60).status
    checks = {
        'tables_match': inventory == manifest['tables'],
        'tables_differing': sorted(k for k in set(inventory) | set(manifest['tables'])
                                   if inventory.get(k) != manifest['tables'].get(k)),
        'active_release_match': head == manifest['active_release'],
        'served_release_match': served['release_id'] == manifest['active_release']['release_id'],
        'git_refs_match': refs == manifest['git_refs'],
        'assets_content_addressed': not bad_assets,
        'asset_count_match': len([a for a in assets if a]) == expected_assets,
        'reader_page_status': page,
    }
    timings['verified'] = time.time() - started
    verify_protected(protected)
    report = {'backup': folder.name, 'backup_created_at': manifest['created_at'],
              'restored_at': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(started)),
              'rto_seconds': round(timings['verified'], 1), 'timings': {k: round(v, 1) for k, v in timings.items()},
              'checks': checks, 'protected_services_unchanged': True,
              'preview_unchanged': preview_snapshot() == preview}
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / ('restore-' + report['restored_at'] + '.json')).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def owner():
    """Replace the restored owner credential with the drill-only test password, inside the drill DB only."""
    check()
    password = env_values()['DRILL_OWNER_PASSWORD']
    script = ('import sys; from app.research_db import writer_engine; from app.research_owner import set_owner\n'
              'password = sys.stdin.read()\n'
              'with writer_engine().begin() as connection:\n'
              '    set_owner(connection, password, reset=True)\n'
              'print("drill owner reset")')
    return compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'worker', 'python', '-c', script,
                   input=password.encode()).decode().strip()


def down():
    volumes = check()
    preview = preview_snapshot()
    compose('--profile', 'tools', 'down', '--volumes', '--remove-orphans')
    if preview_snapshot() != preview:
        raise RuntimeError('Preview containers changed during drill teardown')
    return {'removed_volumes': volumes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'check', 'restore', 'owner', 'down'])
    parser.add_argument('--backup')
    args = parser.parse_args()
    if args.action == 'restore' and not args.backup:
        parser.error('--backup is required')
    result = {'setup': lambda: (setup(), 'ok')[1], 'check': check, 'restore': lambda: restore(args.backup),
              'owner': owner, 'down': down}[args.action]()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
