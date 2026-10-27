"""Drill environment in its own Compose project (industryflow-research-drill): restore a production backup on the
image that took it, rehearse deploying and rolling back an unmerged commit, and run that commit's PostgreSQL and
rebuild checks. Never touches the production or the original services and never reads production secrets. Drill
secrets live in INDUSTRYFLOW_DRILL_HOME (default %USERPROFILE%\\industryflow-drill), so this runs from any checkout
or worktree. Reports go to .work/research-drill/ of the checkout it runs from.

python scripts/research_drill.py setup [--sec-user-agent "<contact>"]
python scripts/research_drill.py build --commit <sha>                         # api and web images only
python scripts/research_drill.py restore --backup latest|<folder> [--baseline-commit <sha>]
python scripts/research_drill.py deploy-rehearsal --commit <sha> [--allow-contract]
python scripts/research_drill.py rollback-rehearsal [--commit <sha>]          # default: the restored baseline
python scripts/research_drill.py pg-check --commit <sha> [--suite all]
python scripts/research_drill.py rebuild-check --commit <sha>
python scripts/research_drill.py migrate [--commit <sha>]   # upgrade a restored (older) schema to a commit's head
python scripts/research_drill.py owner      # drill-only owner credential from the drill env file
python scripts/research_drill.py run-job --job <uuid> [--stop-at before-activation]
python scripts/research_drill.py offline-refresh --source twse-revenue
python scripts/research_drill.py down       # remove the drill containers and volumes only
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import socket
import sys
import tarfile
import time
import traceback
import urllib.request
import uuid

import research_lab as lab
from research_lab import (ROOT, SECRET_KEYS, GIT_REPO, ASSET_DIR, sha256_file, db_inventory,
                          protected_snapshot, verify_protected)

PROJECT = 'industryflow-research-drill'
DRILL_HOME = Path(os.environ.get('INDUSTRYFLOW_DRILL_HOME') or Path.home() / 'industryflow-drill')
ENV_FILE = DRILL_HOME / '.env.research-drill'
# `--backup latest` picks from the deployment directory's backups; production secrets there are never read.
PROD_BACKUPS = Path(os.environ.get('INDUSTRYFLOW_PROD_HOME') or Path.home() / 'industryflow-prod') / 'backups' / 'research'
PORTS = {'api': (8016, 8000), 'web': (3016, 3010)}
API, WEB = 'http://127.0.0.1:8016', 'http://127.0.0.1:3016'
REPORTS = ROOT / '.work/research-drill'
SERVICES = {'db', 'api', 'web', 'initialize', 'bootstrap', 'worker', 'offline-worker'}
SUITES = ['all', 'admin-read', 'publication-restart', 'publication-interfaces', 'source-updates', 'research-dynamic',
          'reader-navigation']
THEME_VERSIONS = 'public.theme_assessment_versions'


def run(args, **kwargs):
    """research_lab.run that also removes the drill secrets from failure output."""
    return lab.run(args, redact_files=(ENV_FILE,), **kwargs)


def redact(message):
    return lab.redact(message, ENV_FILE)


def env_values():
    return dict(line.split('=', 1) for line in ENV_FILE.read_text(encoding='utf-8').splitlines()
                if line and not line.startswith('#'))


def compose(*args, tag, input=None):
    """Every call names the image tag; host RESEARCH_* variables never reach Compose."""
    if not lab.TAG.fullmatch(tag or ''):
        raise ValueError(f'Image tag must be 12 lowercase hex characters, not {tag!r}')
    env = {k: v for k, v in os.environ.items() if not k.startswith('RESEARCH_')}
    env.pop('COMPOSE_PROFILES', None)
    env['RESEARCH_IMAGE_TAG'] = tag
    return run(['docker', 'compose', '--project-name', PROJECT, '--env-file', str(ENV_FILE),
                '-f', str(ROOT / 'compose.research-drill.yaml'), *args], cwd=ROOT, env=env, input=input)


def setup(sec_user_agent=None):
    """Fresh drill secrets in DRILL_HOME. The public SEC contact string is passed in, never copied from production."""
    if ENV_FILE.exists():
        return
    if sec_user_agent and not re.fullmatch(r'[^\r\n=]+', sec_user_agent):
        raise ValueError('--sec-user-agent must be one line without "="')
    DRILL_HOME.mkdir(parents=True, exist_ok=True)
    lines = [f'{key}={secrets.token_hex(32)}' for key in SECRET_KEYS]
    lines.append('DRILL_OWNER_PASSWORD=' + secrets.token_urlsafe(24))
    if sec_user_agent:
        lines.append('SEC_USER_AGENT=' + sec_user_agent)
    with ENV_FILE.open('x', encoding='utf-8', newline='\n') as output:
        output.write('\n'.join(lines) + '\n')


def check(tag):
    setup()
    config = json.loads(compose('--profile', 'tools', 'config', '--format', 'json', tag=tag))
    services = config['services']
    if config.get('name') != PROJECT or set(services) != SERVICES:
        raise ValueError('Unexpected drill project')
    images = {f'{lab.IMAGES["api"]}:{tag}', f'{lab.IMAGES["web"]}:{tag}'}
    for name, service in services.items():
        if 'container_name' in service or service.get('network_mode'):
            raise ValueError('Fixed container name or host networking forbidden')
        if 'build' in service:
            raise ValueError('The drill never builds through Compose')
        if name != 'db' and service['image'] not in images:
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
    if not config['networks']['offline'].get('internal') or list(services['offline-worker']['networks']) != ['offline']:
        raise ValueError('The offline worker must only reach the internal network')
    return sorted(v['name'] for v in config['volumes'].values())


def running_revision():
    """The drill's tag comes from the running drill API's revision label; there is no state file."""
    api = lab.running_services(PROJECT).get('api')
    if not api or not api.get('revision'):
        raise RuntimeError('No drill API with a revision label is running; restore a backup first')
    return api['revision']


def current_tag():
    try:
        return running_revision()[:12]
    except RuntimeError:
        return lab.PLACEHOLDER_TAG


def drill_db(tag):
    db = compose('ps', '-q', 'db', tag=tag).decode().strip()
    if not db:
        raise RuntimeError('The drill DB is not running; restore a backup first')
    return db


def preview_snapshot():
    """Fingerprint of the production research containers (named preview before 2026-10-21)."""
    names = sorted(n for n in run(['docker', 'ps', '-a', '--format', '{{.Names}}'], text=True).splitlines()
                   if n.startswith('industryflow-research-') and not n.startswith(PROJECT + '-'))
    records = json.loads(run(['docker', 'inspect', *names], text=True)) if names else []
    return {r['Name']: [r['Id'], r['State']['StartedAt'], r['RestartCount']] for r in records}


def worktree_dirty():
    return bool(run(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())


def write_report(kind, report):
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f'{kind}-{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


def last_restore():
    reports = sorted(REPORTS.glob('restore-*.json')) if REPORTS.exists() else []
    return json.loads(reports[-1].read_text(encoding='utf-8')) if reports else None


def table_changes(before, after):
    """Row count and content md5 of every table that differs, plus how many stayed identical."""
    def split(value):
        return (int(value.split(':')[0]), value.split(':')[1]) if value else (None, None)
    changed = {}
    for table in sorted(set(before) | set(after)):
        if before.get(table) != after.get(table):
            (rows_before, md5_before), (rows_after, md5_after) = split(before.get(table)), split(after.get(table))
            changed[table] = {'rows_before': rows_before, 'rows_after': rows_after,
                              'md5_before': md5_before, 'md5_after': md5_after}
    return {'changed': changed, 'unchanged': sum(1 for table, value in before.items() if after.get(table) == value)}


def theme_versions(before, after):
    rows = [int(inventory[THEME_VERSIONS].split(':')[0]) if THEME_VERSIONS in inventory else None
            for inventory in (before, after)]
    return {'before': rows[0], 'after': rows[1], 'added': None if None in rows else rows[1] - rows[0]}


def build(commit):
    tag, built = lab.build_images(commit)
    return {'tag': tag, 'built': built, 'labels': lab.existing_labels(f'{lab.IMAGES["api"]}:{tag}')}


def resolve_backup(value):
    if value != 'latest':
        return Path(value).resolve()
    complete = sorted(folder for folder in PROD_BACKUPS.iterdir() if folder.is_dir() and lab.STAMP.fullmatch(folder.name)
                      and (folder / 'manifest.json').exists()) if PROD_BACKUPS.exists() else []
    if not complete:
        raise ValueError(f'No complete backup under {PROD_BACKUPS}; pass --backup <folder>')
    return complete[-1]


def baseline_commit(manifest, given=None):
    """The image that took the backup: its revision in the manifest, or --baseline-commit for older manifests."""
    revision = manifest.get('api_revision')
    if revision and given and lab.resolve_commit(given) != revision:
        raise ValueError(f'The backup was taken on {revision[:12]}; --baseline-commit names a different commit')
    if not (revision or given):
        raise ValueError('This backup predates api_revision in manifests; pass --baseline-commit '
                         '<the commit its API image was built from>')
    return revision or lab.resolve_commit(given)


def restore(backup, baseline=None):
    folder = resolve_backup(backup)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    for name, digest in manifest['files'].items():
        if sha256_file(folder / name) != digest:
            raise ValueError(f'Backup file {name} does not match its manifest')
    with tarfile.open(folder / 'assets.tar') as archive:
        expected_assets = sum(1 for member in archive.getmembers() if member.isfile())
    commit = baseline_commit(manifest, baseline)
    # The baseline image restores the backup, so a commit with new migrations never breaks the restore.
    tag, built = lab.build_images(commit)
    volumes = check(tag)
    existing = set(run(['docker', 'volume', 'ls', '--format', '{{.Name}}'], text=True).split())
    if existing & set(volumes):
        raise ValueError('Drill volumes already exist; run down first so the drill starts empty')
    for port, _ in PORTS.values():
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', port)) == 0:
                raise RuntimeError(f'Drill port {port} already occupied')
    protected, preview = protected_snapshot(), preview_snapshot()
    timings, started = {}, time.time()
    compose('up', '-d', '--wait', 'db', tag=tag)
    timings['db_ready'] = time.time() - started
    db = drill_db(tag)
    # The cluster already has the superuser; other roles are created without passwords and get
    # drill passwords from research_roles below. Errors for pre-existing roles are expected.
    run(['docker', 'exec', '-i', db, 'psql', '-U', 'industry', '-d', 'postgres', '-q'],
        input=(folder / 'roles.sql').read_bytes())
    compose('cp', str(folder / 'database.dump'), 'db:/tmp/restore.dump', tag=tag)
    compose('exec', '-T', 'db', 'pg_restore', '-U', 'industry', '-d', 'industry_research', '--exit-on-error', '/tmp/restore.dump', tag=tag)
    compose('exec', '-T', 'db', 'rm', '/tmp/restore.dump', tag=tag)
    tool = ('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'bootstrap')
    compose(*tool, 'python', '-m', 'app.research_roles', tag=tag)
    timings['database_restored'] = time.time() - started
    compose(*tool, 'sh', '-c', 'cat > /tmp/restore.bundle && '
            f'git clone -q --mirror /tmp/restore.bundle {GIT_REPO} && git -C {GIT_REPO} config --remove-section remote.origin',
            input=(folder / 'git.bundle').read_bytes(), tag=tag)
    compose(*tool, 'tar', '-C', ASSET_DIR, '-xf', '-', input=(folder / 'assets.tar').read_bytes(), tag=tag)
    timings['git_assets_restored'] = time.time() - started
    compose('up', '-d', '--wait', 'api', 'web', tag=tag)
    timings['serving'] = time.time() - started
    inventory, head = db_inventory(db)
    refs = compose(*tool, 'git', '-C', GIT_REPO, 'show-ref', tag=tag).decode().splitlines()
    assets = compose(*tool, 'sh', '-c', f'cd {ASSET_DIR} && sha256sum *', tag=tag).decode().split('\n')
    bad_assets = [line for line in assets if line and line.split()[0] != line.split()[-1]]
    with urllib.request.urlopen(API + '/api/v2/manifest', timeout=30) as response:
        served = json.load(response)
    page = urllib.request.urlopen(WEB + '/next', timeout=60).status
    checks = {
        'tables_match': inventory == manifest['tables'],
        'tables_differing': sorted(k for k in set(inventory) | set(manifest['tables'])
                                   if inventory.get(k) != manifest['tables'].get(k)),
        'active_release_match': head == manifest['active_release'],
        'served_release_match': served['release_id'] == manifest['active_release']['release_id'],
        'git_refs_match': refs == manifest['git_refs'],
        'assets_content_addressed': not bad_assets,
        'asset_count_match': len([a for a in assets if a]) == expected_assets,
        'alembic_version_match': manifest.get('alembic_version') in (None, lab.alembic_version(db)),
        'reader_page_status': page,
    }
    timings['verified'] = time.time() - started
    verify_protected(protected)
    report = {'backup': folder.name, 'backup_created_at': manifest['created_at'],
              'restored_at': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(started)),
              'baseline_commit': commit, 'baseline_tag': tag, 'baseline_built': built,
              'rto_seconds': round(timings['verified'], 1), 'timings': {k: round(v, 1) for k, v in timings.items()},
              'checks': checks, 'worktree_dirty': worktree_dirty(), 'protected_services_unchanged': True,
              'preview_unchanged': preview_snapshot() == preview}
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / ('restore-' + report['restored_at'] + '.json')).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def deploy_rehearsal(commit, force=False, allow_contract=False):
    """Design D6 steps 4-10 on the drill: the same refusals, build, initialize, replacement and smoke checks.
    No first-parent or deployment directory check: rehearsing an unmerged commit is the point."""
    commit = lab.resolve_commit(commit)
    baseline = running_revision()
    target = lab.commit_info(commit)
    db = drill_db(baseline[:12])
    version_before = lab.alembic_version(db)
    refusals, added = lab.deploy_refusals(target, version_before, [], force, allow_contract)
    lab.refuse_if(refusals, 'rehearse the deploy')
    protected, preview = protected_snapshot(), preview_snapshot()
    before, _ = db_inventory(db)
    started = time.time()
    tag, built = lab.build_images(commit)
    check(tag)
    lab.run_initialize(compose, tag, '--profile', 'tools')
    lab.replace_services(compose, tag, lab.running_services(PROJECT))
    ok, smoke = lab.smoke_checks(compose, PROJECT, tag, commit, target['alembic_head'], API, WEB)
    after, _ = db_inventory(db)
    report = {'kind': 'deploy-rehearsal', 'commit': commit, 'tag': tag, 'built': built, 'baseline_commit': baseline,
              'worktree_dirty': worktree_dirty(), 'contract_revisions_added': added,
              'alembic': {'before': version_before, 'after': lab.alembic_version(db), 'image_head': target['alembic_head']},
              'tables': table_changes(before, after), 'theme_assessment_versions': theme_versions(before, after),
              'smoke_ok': ok, 'smoke': smoke, 'seconds': round(time.time() - started, 1),
              'preview_unchanged': preview_snapshot() == preview}
    path = write_report('deploy-rehearsal', report)
    verify_protected(protected)
    report['protected_services_unchanged'] = True
    if not ok:
        raise RuntimeError(f'Smoke check failed; see {path}')
    return {**report, 'report': str(path)}


def rollback_rehearsal(commit=None):
    """Design D7 on the drill: back to the restored baseline (or --commit) without initialize, refused across
    contract migrations or a Prefect change, exactly as production would decide."""
    current_commit = running_revision()
    restored = last_restore()
    if commit is None and not restored:
        raise RuntimeError('No restore report in .work/research-drill; pass --commit')
    target_commit = lab.resolve_commit(commit) if commit else restored['baseline_commit']
    current, target = lab.commit_info(current_commit), lab.commit_info(target_commit)
    db = drill_db(current_commit[:12])
    version = lab.alembic_version(db)
    boundary = f'{restored["backup"]} (the backup this drill was restored from)' if restored else None
    refusals = lab.rollback_refusals(target, current, version, [target, current], boundary)
    report = {'kind': 'rollback-rehearsal', 'from_commit': current_commit, 'to_commit': target_commit,
              'database_version': version, 'target_head': target['alembic_head'], 'refusals': refusals,
              'worktree_dirty': worktree_dirty()}
    if refusals:
        report['judgement'] = 'refused'
        path = write_report('rollback-rehearsal', report)
        lab.refuse_if(refusals, f'rehearse the rollback (report {path})')
    chain, _ = lab.chain_union([target, current])
    report.update(judgement='expand-only', initialize_run=False,
                  migrations_between=chain[chain.index(target['alembic_head']) + 1:chain.index(version) + 1])
    protected, preview = protected_snapshot(), preview_snapshot()
    before, _ = db_inventory(db)
    tag, built = lab.build_images(target_commit)
    check(tag)
    lab.replace_services(compose, tag, lab.running_services(PROJECT))
    ok, smoke = lab.smoke_checks(compose, PROJECT, tag, target_commit, version, API, WEB)
    after, _ = db_inventory(db)
    report.update(tag=tag, rebuilt=bool(built), smoke_ok=ok, smoke=smoke, tables=table_changes(before, after),
                  theme_assessment_versions=theme_versions(before, after), preview_unchanged=preview_snapshot() == preview)
    path = write_report('rollback-rehearsal', report)
    verify_protected(protected)
    report['protected_services_unchanged'] = True
    if not ok:
        raise RuntimeError(f'Smoke check failed; see {path}')
    return {**report, 'report': str(path)}


def pg_check(commit, suite='all'):
    """The commit's PostgreSQL contract suites on the drill DB cluster only: industry_research_test is created
    there, through the drill's superuser bootstrap service, never on the production cluster."""
    commit = lab.resolve_commit(commit)
    tag, built = lab.build_images(commit)
    check(tag)
    drill_db(tag)
    protected, preview = protected_snapshot(), preview_snapshot()
    started = time.time()
    output = compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', '-e', 'PYTHONUNBUFFERED=1', 'bootstrap',
                     'python', '-m', 'app.research_pg_checks', '--suite', suite, tag=tag).decode('utf-8', errors='replace')
    verify_protected(protected)
    summary = next((line.strip('= ') for line in reversed(output.splitlines()) if re.search(r'\d+ passed', line)), None)
    report = {'kind': 'pg-check', 'commit': commit, 'tag': tag, 'built': built, 'suite': suite, 'summary': summary,
              'seconds': round(time.time() - started, 1), 'worktree_dirty': worktree_dirty(),
              'protected_services_unchanged': True, 'preview_unchanged': preview_snapshot() == preview}
    path = write_report('pg-check', report)
    path.with_suffix('.log').write_text(output, encoding='utf-8')
    return {**report, 'report': str(path)}


def rebuild_check(commit):
    """Compile the commit's research content in the drill (assets land in the drill's volume) and roll back."""
    commit = lab.resolve_commit(commit)
    tag, built = lab.build_images(commit)
    check(tag)
    drill_db(tag)
    protected, preview = protected_snapshot(), preview_snapshot()
    archive = run(['git', '-c', 'core.autocrlf=false', 'archive', '--format=tar', commit, 'industry-map',
                   'data/company-research.yaml', 'data/theme-indicators.yaml'], cwd=ROOT)
    result = json.loads(compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'bootstrap', 'python', '-m',
                                'app.research_rebuild_check', '--commit', commit, input=archive, tag=tag))
    verify_protected(protected)
    report = {'kind': 'rebuild-check', 'commit': commit, 'tag': tag, 'built': built, 'worktree_dirty': worktree_dirty(),
              'result': {key: value for key, value in result.items() if key != 'search_plans'},
              'protected_services_unchanged': True, 'preview_unchanged': preview_snapshot() == preview}
    path = write_report('rebuild-check', {**report, 'search_plans': result.get('search_plans')})
    return {**report, 'report': str(path)}


def migrate(commit=None):
    """A backup keeps the schema revision it was taken at; bring the drill DB to a commit's head."""
    tag = lab.build_images(commit)[0] if commit else running_revision()[:12]
    check(tag)
    db = drill_db(tag)
    before = lab.alembic_version(db)
    compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'bootstrap', 'alembic', 'upgrade', 'head', tag=tag)
    # Recreate so the API runs that image and opens new reader sessions (role settings such as jit apply per session).
    compose('up', '-d', '--wait', '--force-recreate', '--no-deps', 'api', tag=tag)
    return {'before': before, 'after': lab.alembic_version(db), 'tag': tag}


def owner():
    """Set or replace the owner credential with the drill-only test password, inside the drill DB only."""
    tag = running_revision()[:12]
    check(tag)
    password = env_values()['DRILL_OWNER_PASSWORD']
    script = ('import sys; from sqlalchemy import text\n'
              'from app.research_db import writer_engine; from app.research_owner import set_owner\n'
              'password = sys.stdin.read()\n'
              'with writer_engine().begin() as connection:\n'
              '    exists = connection.execute(text("SELECT count(*) FROM research.admin_owner")).scalar_one() > 0\n'
              '    set_owner(connection, password, reset=exists)\n'
              'print("drill owner reset" if exists else "drill owner set")')
    return compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'worker', 'python', '-c', script,
                   input=password.encode(), tag=tag).decode().strip()


def run_job(job_id, stop_at=None):
    """Execute one publication job once in the drill (no scheduler); optionally stop it at a stage."""
    tag = running_revision()[:12]
    check(tag)
    job = str(uuid.UUID(job_id))
    if stop_at and not re.fullmatch('[a-z-]+', stop_at):
        raise ValueError('Invalid stage name')
    script = ('import json; from app.research_publication import run_job\n'
              f'stop = {stop_at!r}\n'
              'def inject(stage):\n'
              '    if stage == stop:\n'
              '        raise RuntimeError("drill interruption at " + stage)\n'
              'try:\n'
              f'    result = run_job({job!r}, inject=inject)\n'
              'except RuntimeError as error:\n'
              '    result = {"interrupted": str(error)}\n'
              'print(json.dumps({k: result.get(k) for k in ("status", "stage", "failure", "target_release_id", "interrupted")}, default=str))')
    output = compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'worker', 'python', '-c', script, tag=tag).decode()
    return json.loads(output.strip().splitlines()[-1])


def refresh(source, service):
    tag = running_revision()[:12]
    check(tag)
    if not re.fullmatch('[a-z0-9-]+', source):
        raise ValueError('Invalid source id')
    output = compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', service,
                     'python', '-m', 'app.source_updates', '--source', source, tag=tag).decode()
    return json.loads(output.strip().splitlines()[-1])


def online_refresh(source):
    """One real refresh of a registered official source from the drill (same limits as production)."""
    return refresh(source, 'worker')


def offline_refresh(source):
    """Refresh one registered source from the internal-only network, so every fetch fails."""
    return refresh(source, 'offline-worker')


def down():
    tag = current_tag()
    volumes = check(tag)
    preview = preview_snapshot()
    compose('--profile', 'tools', 'down', '--volumes', '--remove-orphans', tag=tag)
    if preview_snapshot() != preview:
        raise RuntimeError('Production containers changed during drill teardown')
    return {'removed_volumes': volumes}


ACTIONS = ['setup', 'check', 'build', 'restore', 'deploy-rehearsal', 'rollback-rehearsal', 'pg-check', 'rebuild-check',
           'migrate', 'owner', 'run-job', 'online-refresh', 'offline-refresh', 'down']
REQUIRED = {'restore': 'backup', 'build': 'commit', 'deploy-rehearsal': 'commit', 'pg-check': 'commit',
            'rebuild-check': 'commit', 'run-job': 'job', 'online-refresh': 'source', 'offline-refresh': 'source'}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=ACTIONS)
    parser.add_argument('--backup', help='restore: latest (newest complete backup in the deployment directory) or a backup folder')
    parser.add_argument('--baseline-commit', help='restore: the commit whose API image took the backup; '
                                                  'only for manifests without api_revision')
    parser.add_argument('--commit', help='build, deploy-rehearsal, pg-check, rebuild-check: the commit to build; '
                                         'rollback-rehearsal: the target (default: the restored baseline); migrate: optional')
    parser.add_argument('--allow-contract', action='store_true', help='deploy-rehearsal: apply contract migrations')
    parser.add_argument('--force', action='store_true', help='deploy-rehearsal: same flag as deploy (the drill has no scheduler)')
    parser.add_argument('--suite', choices=SUITES, default='all', help='pg-check: one suite or all')
    parser.add_argument('--sec-user-agent', help='setup: the public SEC contact string for online refreshes')
    parser.add_argument('--job')
    parser.add_argument('--stop-at')
    parser.add_argument('--source')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.action in REQUIRED and not getattr(args, REQUIRED[args.action]):
        parser.error(f'{args.action} needs --{REQUIRED[args.action]}')
    actions = {'setup': lambda: (setup(args.sec_user_agent), {'setup': 'ok', 'env_file': str(ENV_FILE)})[1],
               'check': lambda: check(current_tag()), 'build': lambda: build(args.commit),
               'restore': lambda: restore(args.backup, args.baseline_commit),
               'deploy-rehearsal': lambda: deploy_rehearsal(args.commit, args.force, args.allow_contract),
               'rollback-rehearsal': lambda: rollback_rehearsal(args.commit),
               'pg-check': lambda: pg_check(args.commit, args.suite), 'rebuild-check': lambda: rebuild_check(args.commit),
               'migrate': lambda: migrate(args.commit), 'owner': owner, 'down': down,
               'run-job': lambda: run_job(args.job, args.stop_at),
               'online-refresh': lambda: online_refresh(args.source), 'offline-refresh': lambda: offline_refresh(args.source)}
    try:
        result = actions[args.action]()
    except Exception:
        # Every failure, wherever it was raised, leaves without production or drill secret values.
        sys.stderr.write(redact(traceback.format_exc()))
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
