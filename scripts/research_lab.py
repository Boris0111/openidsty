"""Isolated preview operations. Never prints resolved Compose secrets."""
import argparse
import calendar
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'industryflow-research'
ENV_FILE = ROOT / '.env.research'
APP_SERVICES = ('initialize', 'api', 'prefect', 'deploy', 'worker', 'ingestion')
PORTS = {'api': (8010, 8000), 'web': (3010, 3010), 'prefect': (4201, 4200), 'reader': (3015, 8000)}
PROTECTED = ('industryflow-', 'industryflow-reading-')
LEGACY_PROJECT = 'industryflow'
SECRET_KEYS = ('RESEARCH_POSTGRES_PASSWORD', 'RESEARCH_SESSION_SECRET',
               'RESEARCH_READER_PASSWORD', 'RESEARCH_WRITER_PASSWORD')


def run(args, **kwargs):
    result = subprocess.run(args, capture_output=True, check=False, **kwargs)
    if result.returncode:
        message = result.stdout + result.stderr
        if isinstance(message, bytes):
            message = message.decode('utf-8', errors='replace')
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
                if '=' in line and not line.startswith('#'):
                    value = line.split('=', 1)[1]
                    if value:
                        message = message.replace(value, '[REDACTED]')
        raise RuntimeError(f'{args[0]} {args[1]} failed (exit {result.returncode}): {message[-12000:]}')
    return result.stdout


def compose(*args, input=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith('RESEARCH_')}
    env.pop('COMPOSE_PROFILES', None)
    return run(['docker', 'compose', '--project-name', PROJECT, '--env-file', str(ENV_FILE),
                '-f', str(ROOT / 'compose.research.yaml'), *args], cwd=ROOT, env=env, input=input)


def setup():
    if not ENV_FILE.exists():
        content = ''.join(f'{key}={secrets.token_hex(32)}\n' for key in SECRET_KEYS)
        with ENV_FILE.open('x', encoding='utf-8', newline='\n') as output:
            output.write(content)
    pairs = dict(line.split('=', 1) for line in ENV_FILE.read_text(encoding='utf-8').splitlines()
                 if line and not line.startswith('#'))
    if any(not re.fullmatch('[0-9a-f]{64}', pairs.get(key, '')) for key in SECRET_KEYS if key in pairs):
        raise ValueError('Invalid research environment; existing file preserved')
    missing = [key for key in SECRET_KEYS if key not in pairs]
    if missing:
        with ENV_FILE.open('a', encoding='utf-8', newline='\n') as output:
            output.write('\n' + ''.join(f'{key}={secrets.token_hex(32)}\n' for key in missing))


def validate_restart(services):
    """Long-running scheduler services return after a reboot; a manual stop still keeps them down."""
    for name in ('prefect', 'worker'):
        if services[name].get('restart') != 'unless-stopped':
            raise ValueError(f'Scheduler service {name} must restart unless-stopped')
    if services['deploy'].get('restart', 'no') != 'no':
        raise ValueError('Scheduler deploy must stay one-shot')


def validate_config(config):
    if config.get('name') != PROJECT:
        raise ValueError('Unexpected Compose project')
    services = config['services']
    if set(services) != {*APP_SERVICES, 'db', 'web', 'reader'}:
        raise ValueError('Unexpected preview services')
    for name in APP_SERVICES:
        if services[name]['image'] != 'industryflow-research-api:dev':
            raise ValueError(f'Unsafe image for {name}')
        environment = services[name]['environment']
        for key in ('DATABASE_URL', 'RESEARCH_READ_DATABASE_URL', 'RESEARCH_WRITE_DATABASE_URL'):
            url = urlsplit(environment[key])
            if url.hostname != 'db' or url.path != '/industry_research':
                raise ValueError('Application must use the isolated DB')
        expected_user = ('research_reader_login' if name == 'api' else
                         'research_writer_login' if name in {'worker', 'ingestion'} else 'industry')
        if urlsplit(environment['DATABASE_URL']).username != expected_user:
            raise ValueError('Unexpected database privilege for ' + name)
    if services['web']['image'] != 'industryflow-research-web:dev':
        raise ValueError('Unsafe web image')
    reader = services['reader']
    if (reader['image'] != 'industryflow-research-api:dev' or reader.get('profiles') != ['reader']
        or reader.get('volumes') or not reader.get('read_only') or reader.get('cap_drop') != ['ALL']
        or set(reader.get('environment', {})) != {'READER_ALLOWED_HOSTS'}):
        raise ValueError('Reader gateway must be credential-free, isolated and opt-in')
    for name, service in services.items():
        if 'container_name' in service or service.get('network_mode'):
            raise ValueError('Fixed container name or host networking forbidden')
        ports = service.get('ports', [])
        expected = PORTS.get(name)
        if len(ports) != (1 if expected else 0):
            raise ValueError(f'Unexpected ports for {name}')
        for port in ports:
            if (port.get('host_ip'), int(port['published']), int(port['target'])) != ('127.0.0.1', *expected):
                raise ValueError(f'Unsafe port binding for {name}')
        for volume in service.get('volumes', []):
            if volume['type'] == 'bind' and not (
                name == 'db' and volume.get('read_only') and
                Path(volume['source']).resolve() == (ROOT / 'docker/research-init.sql').resolve()
            ):
                raise ValueError(f'Unexpected writable or external bind in {name}')
    for kind in ('volumes', 'networks'):
        for resource in config.get(kind, {}).values():
            if resource.get('external') or not resource.get('name', '').startswith(PROJECT + '_'):
                raise ValueError(f'Unsafe {kind} namespace')
    for name in ('prefect', 'deploy', 'worker'):
        if services[name].get('profiles') != ['scheduler']:
            raise ValueError('Scheduler must be opt-in')
    validate_restart(services)
    return {'project': PROJECT, 'services': sorted(services),
            'images': sorted({s['image'] for s in services.values()}),
            'ports': {k: v[0] for k, v in PORTS.items()},
            'volumes': sorted(v['name'] for v in config.get('volumes', {}).values())}


def check():
    setup()
    return validate_config(json.loads(compose('--profile', 'scheduler', '--profile', 'tools', '--profile', 'reader',
                                              'config', '--format', 'json')))


def protected_snapshot():
    names = run(['docker', 'ps', '-a', '--format', '{{.Names}}'], text=True).splitlines()
    names = sorted(n for n in names if n.startswith(PROTECTED) and not n.startswith(PROJECT + '-'))
    records = json.loads(run(['docker', 'inspect', *names], text=True)) if names else []
    return {r['Name']: {'id': r['Id'], 'image': r['Image'],
                       'started_at': r['State']['StartedAt'], 'restarts': r['RestartCount'],
                       'mounts': sorted([[m['Source'], m['Destination'], m['RW']] for m in r['Mounts']]),
                       'ports': r['HostConfig']['PortBindings']} for r in records}


def running_containers():
    """Running containers as name -> (Compose project, published host ports)."""
    lines = run(['docker', 'ps', '--format', '{{.Names}}\t{{.Label "com.docker.compose.project"}}\t{{.Ports}}'],
                text=True).splitlines()
    containers = {}
    for line in filter(None, lines):
        name, project, ports = (line.split('\t') + ['', ''])[:3]
        containers[name] = (project, {int(p) for p in re.findall(r':(\d+)->', ports)})
    return containers


def listening_ports():
    found = set()
    for port, _ in PORTS.values():
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', port)) == 0:
                found.add(port)
    return found


def exclusion_conflicts(containers, listening, ports):
    """The research service and the original service share 3010/8010/4201 and must never run together.
    Only report conflicts; stopping the original service is the maintainer's decision."""
    conflicts = []
    legacy = sorted(name for name, (project, _) in containers.items() if project == LEGACY_PROJECT)
    if legacy:
        conflicts.append('Original service still running: ' + ', '.join(legacy))
    own = set().union(*[published for project, published in containers.values() if project == PROJECT])
    for port in ports:
        if port in listening and port not in own:
            holders = sorted(name for name, (_, published) in containers.items() if port in published)
            conflicts.append(f'Port {port} occupied by ' + (', '.join(holders) or 'a non-Docker process'))
    return conflicts


def verify_protected(before):
    after = protected_snapshot()
    if after != before:
        folder = ROOT / '.work/research-lab'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'isolation-difference.json').write_text(
            json.dumps({'before': before, 'after': after}, indent=2), encoding='utf-8')
        raise RuntimeError('Existing service fingerprint changed; inspect safe isolation-difference.json')


def database_snapshot(container, database):
    def sql(statement):
        return run(['docker', 'exec', container, 'psql', '-U', 'industry', '-d', database,
                    '-At', '-v', 'ON_ERROR_STOP=1', '-c', statement], text=True).strip()
    tables = sql("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").splitlines()
    if any(not re.fullmatch('[a-z_][a-z_0-9]*', t) for t in tables):
        raise ValueError('Unexpected table identifier')
    return {t: sql(f"SELECT count(*) || ':' || md5(coalesce(string_agg(row_to_json(t)::text, '' "
                   f"ORDER BY row_to_json(t)::text), '')) FROM public.\"{t}\" t") for t in tables}


def restore(source, database):
    if source not in {'industryflow-reading-db', 'industryflow-db-1'} or not re.fullmatch('[a-z_]+', database):
        raise ValueError('Only explicit existing IndustryFlow databases may be backup sources')
    before = protected_snapshot()
    source_data = database_snapshot(source, database)
    folder = ROOT / '.work/research-lab'
    folder.mkdir(parents=True, exist_ok=True)
    backup = folder / ('source-' + time.strftime('%Y%m%d-%H%M%S') + '.dump')
    # Direct binary stream: PowerShell must never decode the custom dump.
    with backup.open('xb') as output:
        process = subprocess.run(['docker', 'exec', source, 'pg_dump', '-U', 'industry',
                                  '-d', database, '-Fc'], stdout=output, stderr=subprocess.PIPE)
    if process.returncode:
        raise RuntimeError('Source pg_dump failed')
    compose('up', '-d', '--wait', 'db')
    target = compose('ps', '-q', 'db').decode().strip()
    if database_snapshot(target, 'industry_research'):
        raise ValueError('Target database is not empty; preserved without restore')
    compose('cp', str(backup), 'db:/tmp/research-restore.dump')
    compose('exec', '-T', 'db', 'pg_restore', '-U', 'industry', '-d', 'industry_research',
            '--no-owner', '--no-privileges', '--exit-on-error', '/tmp/research-restore.dump')
    target_data = database_snapshot(target, 'industry_research')
    if target_data != source_data:
        raise RuntimeError('Restored data does not match backup source')
    verify_protected(before)
    report = {'source': source, 'source_database': database, 'target_database': 'industry_research',
              'backup_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
              'tables': target_data, 'protected_services_unchanged': True,
              'protected_services': before}
    (folder / 'restore.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


BACKUP_ROOT = ROOT / 'backups/research'
STAMP = re.compile(r'\d{8}T\d{6}Z')
GIT_REPO = '/home/app/research-git/repository.git'
ASSET_DIR = '/home/app/research-assets'


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def db_inventory(container, database='industry_research'):
    """Per-table row count and content md5 for the research and public schemas, plus the active head."""
    def sql(statement):
        return run(['docker', 'exec', container, 'psql', '-U', 'industry', '-d', database,
                    '-At', '-v', 'ON_ERROR_STOP=1', '-c', statement], text=True).strip()
    tables = sql("SELECT schemaname || '.' || tablename FROM pg_tables "
                 "WHERE schemaname IN ('public', 'research') ORDER BY 1").splitlines()
    if any(not re.fullmatch(r'(public|research)\.[a-z_][a-z_0-9]*', t) for t in tables):
        raise ValueError('Unexpected table identifier')
    inventory = {}
    for table in tables:
        schema, name = table.split('.')
        inventory[table] = sql(f"SELECT count(*) || ':' || md5(coalesce(string_agg(row_to_json(t)::text, '' "
                               f"ORDER BY row_to_json(t)::text), '')) FROM \"{schema}\".\"{name}\" t")
    head = sql("SELECT h.release_id || '|' || h.generation || '|' || r.content_hash || '|' || r.git_commit "
               "FROM research.release_head h JOIN research.research_releases r USING (release_id)")
    return inventory, dict(zip(('release_id', 'generation', 'content_hash', 'git_commit'), head.split('|')))


def copy_verified(folder, target, files):
    target.mkdir(parents=True)
    for name, digest in files.items():
        (target / name).write_bytes((folder / name).read_bytes())
        if sha256_file(target / name) != digest:
            raise RuntimeError(f'Secondary copy of {name} does not match')


def prune(root, keep_days, now):
    removed = []
    for folder in sorted(root.iterdir()) if root.exists() else []:
        # Only complete, script-named backups are eligible; anything else is left alone.
        if folder.is_dir() and STAMP.fullmatch(folder.name) and (folder / 'manifest.json').exists():
            created = calendar.timegm(time.strptime(folder.name, '%Y%m%dT%H%M%SZ'))
            if now - created > keep_days * 86400:
                for item in folder.iterdir():
                    item.unlink()
                folder.rmdir()
                removed.append(folder.name)
    return removed


def backup(secondary=None, keep_days=30):
    """Daily backup: DB dump, roles without passwords, managed Git refs, assets and the active release."""
    before = protected_snapshot()
    started = time.time()
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(started))
    folder = BACKUP_ROOT / stamp
    folder.mkdir(parents=True)
    status = 'failed'
    try:
        db = compose('ps', '-q', 'db').decode().strip()
        if not db:
            raise RuntimeError('Research DB is not running; nothing backed up')
        for attempt in range(3):
            inventory, head = db_inventory(db)
            # Direct binary capture: the custom dump never passes through a text decoder.
            (folder / 'database.dump').write_bytes(compose('exec', '-T', 'db', 'pg_dump', '-U', 'industry',
                                                           '-d', 'industry_research', '-Fc'))
            if db_inventory(db)[0] == inventory:
                break
        else:
            raise RuntimeError('Database kept changing during backup; retry when writes are idle')
        (folder / 'roles.sql').write_bytes(compose('exec', '-T', 'db', 'pg_dumpall', '-U', 'industry',
                                                   '--roles-only', '--no-role-passwords'))
        tool = ('run', '--rm', '--no-deps', '-T', 'initialize')
        (folder / 'git.bundle').write_bytes(compose(*tool, 'git', '-C', GIT_REPO, 'bundle', 'create', '-', '--all'))
        refs = compose(*tool, 'git', '-C', GIT_REPO, 'show-ref').decode().splitlines()
        (folder / 'assets.tar').write_bytes(compose(*tool, 'tar', '-C', ASSET_DIR, '-cf', '-', '.'))
        files = {name: sha256_file(folder / name) for name in ('database.dump', 'roles.sql', 'git.bundle', 'assets.tar')}
        image = run(['docker', 'image', 'inspect', 'industryflow-research-api:dev', '--format', '{{.Id}}'], text=True).strip()
        manifest = {'created_at': stamp, 'duration_seconds': round(time.time() - started, 1), 'files': files,
                    'sizes': {name: (folder / name).stat().st_size for name in files}, 'active_release': head,
                    'tables': inventory, 'git_refs': refs, 'api_image': image,
                    'excluded': 'Environment secrets (.env.research) are backed up separately; the DB includes the owner password hash.'}
        (folder / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        files['manifest.json'] = sha256_file(folder / 'manifest.json')
        result = {'backup': str(folder), 'release_id': head['release_id'], 'files': files}
        if secondary:
            copy_verified(folder, Path(secondary) / stamp, files)
            result['secondary'] = str(Path(secondary) / stamp)
        result['pruned'] = {str(root): prune(root, keep_days, started)
                            for root in [BACKUP_ROOT, *([Path(secondary)] if secondary else [])]}
        verify_protected(before)
        result['protected_services_unchanged'] = True
        status = 'ok'
        return result
    except Exception as error:
        status = 'failed: ' + str(error)[:500]
        # Remove only this run's incomplete folder so it is never mistaken for a backup.
        for item in folder.iterdir():
            item.unlink()
        folder.rmdir()
        raise
    finally:
        with (BACKUP_ROOT / 'backup-log.jsonl').open('a', encoding='utf-8') as log:
            log.write(json.dumps({'stamp': stamp, 'status': status, 'seconds': round(time.time() - started, 1)}) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'check', 'up', 'stop', 'start', 'restore', 'pg-check', 'rebuild-check', 'bootstrap', 'seed-git', 'reader-start', 'reader-stop', 'backup'])
    parser.add_argument('--secondary', help='second storage device for the verified backup copy')
    parser.add_argument('--keep-days', type=int, default=30)
    parser.add_argument('--commit', default='HEAD')
    parser.add_argument('--source-container', default='industryflow-reading-db')
    parser.add_argument('--source-database', default='industry_reading')
    parser.add_argument('--suite', choices=['all', 'admin-read', 'publication-restart', 'publication-interfaces','financial-core','financial-sec','financial-imports','source-updates','research-dynamic','reader-navigation'], default='all')
    args = parser.parse_args()
    report = check()
    if args.action in ('reader-start','reader-stop'):
        before = protected_snapshot()
        if args.action == 'reader-start':
            compose('--profile','reader','up','-d','--no-build','--wait','reader')
        else:
            compose('--profile','reader','stop','reader')
        verify_protected(before)
        report['protected_services_unchanged'] = True
    elif args.action == 'seed-git':
        before = protected_snapshot()
        if args.commit != 'HEAD' and not re.fullmatch('[0-9a-f]{40,64}', args.commit):
            raise ValueError('Use HEAD or a full Git commit')
        commit = run(['git', 'rev-parse', '--verify', args.commit + '^{commit}'], cwd=ROOT, text=True).strip()
        folder = ROOT / '.work/research-lab'
        folder.mkdir(parents=True, exist_ok=True)
        bundle = folder / ('seed-' + commit + '.bundle')
        # HEAD is a named ref and retains the selected ancestor; a bare object ID
        # by itself is not a valid bundle inclusion ref on every Git version.
        if run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], cwd=ROOT) != b'':
            raise ValueError('Seed commit must be reachable from HEAD')
        run(['git', 'bundle', 'create', str(bundle), 'HEAD'], cwd=ROOT)
        compose('build', 'api')
        output = compose('run', '--rm', '--no-deps', '-T', 'initialize', 'python', '-m', 'app.research_git',
                         'seed', '--commit', commit, input=bundle.read_bytes())
        report['managed_git'] = output.decode().strip()
        verify_protected(before)
        report['protected_services_unchanged'] = True
    elif args.action in {'rebuild-check', 'bootstrap'}:
        before = protected_snapshot()
        if args.commit != 'HEAD' and not re.fullmatch('[0-9a-f]{40,64}', args.commit):
            raise ValueError('Use HEAD or a full Git commit')
        commit = run(['git', 'rev-parse', '--verify', args.commit + '^{commit}'], cwd=ROOT, text=True).strip()
        archive = run(['git', 'archive', '--format=tar', commit, 'industry-map',
                       'data/company-research.yaml', 'data/theme-indicators.yaml'], cwd=ROOT)
        compose('build', 'api')
        command = ['python', '-m', 'app.research_rebuild_check' if args.action == 'rebuild-check' else 'app.research_compile', '--commit', commit]
        if args.action == 'bootstrap':
            command.append('--bootstrap')
        output = compose('run', '--rm', '--no-deps', '-T', 'initialize', *command, input=archive)
        result = json.loads(output)
        if args.action == 'bootstrap':
            run(['git', 'update-ref', 'refs/research/releases/' + result['release_id'], commit], cwd=ROOT)
        folder = ROOT / '.work/research-lab'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (args.action + '.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
        report['result'] = {key: value for key, value in result.items() if key != 'search_plans'}
        if 'search_plans' in result:
            report['search_plans_saved'] = str(folder / (args.action + '.json'))
        verify_protected(before)
        report['protected_services_unchanged'] = True
    elif args.action == 'backup':
        report['result'] = backup(args.secondary, args.keep_days)
    elif args.action == 'restore':
        result = restore(args.source_container, args.source_database)
        report['restored_tables'] = {k: int(v.split(':')[0]) for k, v in result['tables'].items()}
        report['protected_services_unchanged'] = result['protected_services_unchanged']
    elif args.action == 'pg-check':
        before = protected_snapshot()
        compose('build', 'api')
        output = compose('run', '--rm', '--no-deps', '-T', '-e', 'PYTHONUNBUFFERED=1', 'initialize',
                         'python', '-m', 'app.research_pg_checks', '--suite', args.suite)
        print(output.decode('utf-8', errors='replace'))
        verify_protected(before)
        report['protected_services_unchanged'] = True
    elif args.action in {'up', 'start', 'stop'}:
        before = protected_snapshot()
        if args.action in {'up', 'start'}:
            conflicts = exclusion_conflicts(running_containers(), listening_ports(), [p for p, _ in PORTS.values()])
            if conflicts:
                raise RuntimeError('; '.join(conflicts))
        if args.action == 'up':
            # Build the shared app image once; parallel initialize/api exports race.
            compose('build', 'api', 'web')
            compose('up', '-d', '--no-build', '--wait', 'api', 'web')
        elif args.action == 'stop':
            # Release every shared port (and stop fetching) so the original service can take the origin back.
            compose('--profile', 'scheduler', '--profile', 'reader', 'stop', 'reader', 'worker', 'prefect', 'web', 'api')
        else:
            compose('start', 'api', 'web')
        verify_protected(before)
        report['protected_services_unchanged'] = True
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
