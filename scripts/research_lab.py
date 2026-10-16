"""Isolated preview operations. Never prints resolved Compose secrets."""
import argparse
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
PORTS = {'api': (8014, 8000), 'web': (3014, 3010), 'prefect': (4204, 4200)}
PROTECTED = ('industryflow-', 'industryflow-reading-')
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


def validate_config(config):
    if config.get('name') != PROJECT:
        raise ValueError('Unexpected Compose project')
    services = config['services']
    if set(services) != {*APP_SERVICES, 'db', 'web'}:
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
    return {'project': PROJECT, 'services': sorted(services),
            'images': sorted({s['image'] for s in services.values()}),
            'ports': {k: v[0] for k, v in PORTS.items()},
            'volumes': sorted(v['name'] for v in config.get('volumes', {}).values())}


def check():
    setup()
    return validate_config(json.loads(compose('--profile', 'scheduler', '--profile', 'tools',
                                              'config', '--format', 'json')))


def protected_snapshot():
    names = run(['docker', 'ps', '-a', '--format', '{{.Names}}'], text=True).splitlines()
    names = sorted(n for n in names if n.startswith(PROTECTED) and not n.startswith(PROJECT + '-'))
    records = json.loads(run(['docker', 'inspect', *names], text=True)) if names else []
    return {r['Name']: {'id': r['Id'], 'image': r['Image'],
                       'started_at': r['State']['StartedAt'], 'restarts': r['RestartCount'],
                       'mounts': sorted([[m['Source'], m['Destination'], m['RW']] for m in r['Mounts']]),
                       'ports': r['HostConfig']['PortBindings']} for r in records}


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'check', 'up', 'stop', 'start', 'restore', 'pg-check', 'rebuild-check', 'bootstrap', 'seed-git'])
    parser.add_argument('--commit', default='HEAD')
    parser.add_argument('--source-container', default='industryflow-reading-db')
    parser.add_argument('--source-database', default='industry_reading')
    args = parser.parse_args()
    report = check()
    if args.action == 'seed-git':
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
    elif args.action == 'restore':
        result = restore(args.source_container, args.source_database)
        report['restored_tables'] = {k: int(v.split(':')[0]) for k, v in result['tables'].items()}
        report['protected_services_unchanged'] = result['protected_services_unchanged']
    elif args.action == 'pg-check':
        before = protected_snapshot()
        compose('build', 'api')
        output = compose('run', '--rm', '--no-deps', '-T', 'initialize',
                         'python', '-m', 'app.research_pg_checks')
        print(output.decode('utf-8', errors='replace'))
        verify_protected(before)
        report['protected_services_unchanged'] = True
    elif args.action in {'up', 'start', 'stop'}:
        before = protected_snapshot()
        if args.action == 'up':
            existing = bool(compose('ps', '-q', 'api').strip())
            if not existing:
                for port, _ in PORTS.values():
                    with socket.socket() as probe:
                        if probe.connect_ex(('127.0.0.1', port)) == 0:
                            raise RuntimeError(f'Preview port {port} already occupied')
            # Build the shared app image once; parallel initialize/api exports race.
            compose('build', 'api', 'web')
            compose('up', '-d', '--no-build', '--wait', 'api', 'web')
        elif args.action == 'stop':
            compose('stop', 'web', 'api')
        else:
            compose('start', 'api', 'web')
        verify_protected(before)
        report['protected_services_unchanged'] = True
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
