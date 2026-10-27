"""Research service operations (docs/research-deployment.md). Never prints resolved Compose secrets.

Actions that change the production service run only from the deployment directory, with a clean
working tree whose HEAD and running containers match the deployment record. Images are built only
from `git archive <commit>` and tagged with the commit; nothing here builds from a working tree.
"""
import argparse
import calendar
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

import migration_rules

if os.name == 'nt':
    import msvcrt
else:
    import fcntl

ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'industryflow-research'
ENV_FILE = ROOT / '.env.research'
APP_SERVICES = ('initialize', 'api', 'prefect', 'deploy', 'worker', 'ingestion')
PORTS = {'api': (8010, 8000), 'web': (3010, 3010), 'prefect': (4201, 4200), 'reader': (3015, 8000)}
PROTECTED = ('industryflow-', 'industryflow-reading-')
LEGACY_PROJECT = 'industryflow'
SECRET_KEYS = ('RESEARCH_POSTGRES_PASSWORD', 'RESEARCH_SESSION_SECRET',
               'RESEARCH_READER_PASSWORD', 'RESEARCH_WRITER_PASSWORD')
IMAGES = {'api': 'industryflow-research-api', 'web': 'industryflow-research-web'}
DOCKERFILES = {'api': 'backend/Dockerfile', 'web': 'frontend/Dockerfile'}
TAG = re.compile('[0-9a-f]{12}')
# Images that were running before the deployment record existed (the adopt record); never a deploy target.
PRE_LEDGER = 'pre-ledger'
PLACEHOLDER_TAG = '0' * 12
REVISION = 'org.opencontainers.image.revision'
LABELS = 'io.industryflow.'
PG_VOLUME = PROJECT + '_pg-data'
DEPLOYMENTS = ROOT / 'deployments'
HOME_FILE = DEPLOYMENTS / 'home.json'
LEDGER = DEPLOYMENTS / 'ledger.jsonl'
LOCK = DEPLOYMENTS / '.lock'
HANDOVER = DEPLOYMENTS / '.handover'
LEDGER_SCHEMA = 1
API, WEB, PREFECT_API = 'http://127.0.0.1:8010', 'http://127.0.0.1:3010', 'http://127.0.0.1:4201/api'


class Refused(RuntimeError):
    """A guard or compatibility rule refused the action before anything changed."""


def redact(message, *paths):
    for path in (ENV_FILE, *paths):
        if Path(path).exists():
            for line in Path(path).read_text(encoding='utf-8').splitlines():
                if '=' in line and not line.startswith('#'):
                    value = line.split('=', 1)[1]
                    if value:
                        message = message.replace(value, '[REDACTED]')
    return message


def run(args, redact_files=(), **kwargs):
    """Run a command; failures raise with the production secrets and any redact_files values removed."""
    result = subprocess.run(args, capture_output=True, check=False, **kwargs)
    if result.returncode:
        message = result.stdout + result.stderr
        if isinstance(message, bytes):
            message = message.decode('utf-8', errors='replace')
        raise RuntimeError(f'{args[0]} {args[1]} failed (exit {result.returncode}): {redact(message, *redact_files)[-12000:]}')
    return result.stdout


def valid_tag(tag):
    return bool(TAG.fullmatch(tag or '')) or tag == PRE_LEDGER


def compose(*args, tag, input=None):
    """Every call names the image tag. Host RESEARCH_* variables are dropped and the shell value wins over
    --env-file, so no file can change which image runs."""
    if not valid_tag(tag):
        raise ValueError(f'Image tag must be 12 lowercase hex characters, not {tag!r}')
    env = {k: v for k, v in os.environ.items() if not k.startswith('RESEARCH_')}
    env.pop('COMPOSE_PROFILES', None)
    env['RESEARCH_IMAGE_TAG'] = tag
    return run(['docker', 'compose', '--project-name', PROJECT, '--env-file', str(ENV_FILE),
                '-f', str(ROOT / 'compose.research.yaml'), *args], cwd=ROOT, env=env, input=input)


def env_pairs():
    pairs = {}
    for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            key, separator, value = line.partition('=')
            if not separator:
                raise ValueError('Invalid research environment; existing file preserved')
            pairs[key] = value
    if any(not re.fullmatch('[0-9a-f]{64}', pairs[key]) for key in SECRET_KEYS if key in pairs):
        raise ValueError('Invalid research environment; existing file preserved')
    return pairs


def setup():
    """Create or complete .env.research, but never next to an existing production database volume."""
    pairs = env_pairs() if ENV_FILE.exists() else None
    missing = [key for key in SECRET_KEYS if pairs is None or key not in pairs]
    if not missing:
        return
    if PG_VOLUME in run(['docker', 'volume', 'ls', '--format', '{{.Name}}'], text=True).split():
        raise Refused(f'Volume {PG_VOLUME} already exists; new secrets would not match its database. '
                      'Production secrets live in the deployment directory (docs/research-deployment.md)')
    content = ''.join(f'{key}={secrets.token_hex(32)}\n' for key in missing)
    with ENV_FILE.open('x' if pairs is None else 'a', encoding='utf-8', newline='\n') as output:
        output.write(content if pairs is None else '\n' + content)


def validate_restart(services):
    """Long-running scheduler services return after a reboot; a manual stop still keeps them down."""
    for name in ('prefect', 'worker'):
        if services[name].get('restart') != 'unless-stopped':
            raise ValueError(f'Scheduler service {name} must restart unless-stopped')
    if services['deploy'].get('restart', 'no') != 'no':
        raise ValueError('Scheduler deploy must stay one-shot')


def validate_config(config, tag):
    if not valid_tag(tag):
        raise ValueError(f'Image tag must be 12 lowercase hex characters, not {tag!r}')
    if config.get('name') != PROJECT:
        raise ValueError('Unexpected Compose project')
    services = config['services']
    if set(services) != {*APP_SERVICES, 'db', 'web', 'reader'}:
        raise ValueError('Unexpected preview services')
    api_image, web_image = f'{IMAGES["api"]}:{tag}', f'{IMAGES["web"]}:{tag}'
    for name, service in services.items():
        if 'build' in service:
            raise ValueError(f'{name} must not build; images come from scripts/research_lab.py')
    for name in APP_SERVICES:
        if services[name]['image'] != api_image:
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
    if services['web']['image'] != web_image:
        raise ValueError('Unsafe web image')
    reader = services['reader']
    if (reader['image'] != api_image or reader.get('profiles') != ['reader']
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
    return {'project': PROJECT, 'tag': tag, 'services': sorted(services),
            'images': sorted({s['image'] for s in services.values()}),
            'ports': {k: v[0] for k, v in PORTS.items()},
            'volumes': sorted(v['name'] for v in config.get('volumes', {}).values())}


def validate(tag):
    """Secrets file format and Compose rules for one image tag; reads and writes nothing else."""
    if not ENV_FILE.exists():
        raise Refused('No .env.research in this checkout; production secrets live in the deployment directory '
                      '(docs/research-deployment.md)')
    env_pairs()
    return validate_config(json.loads(compose('--profile', 'scheduler', '--profile', 'tools', '--profile', 'reader',
                                              'config', '--format', 'json', tag=tag)), tag)


def utc_now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def same_path(a, b):
    return bool(a) and os.path.normcase(str(Path(a).resolve())) == os.path.normcase(str(Path(b).resolve()))


def git_head():
    return run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def resolve_commit(commit):
    if not re.fullmatch(r'[0-9A-Za-z_./^~-]{1,100}', commit or ''):
        raise ValueError('Use a commit SHA or ref')
    return run(['git', 'rev-parse', '--verify', '--quiet', commit + '^{commit}'], cwd=ROOT, text=True).strip()


# --- Images: built only from git archive, tagged and labelled with the commit (design D3) ---

def commit_info(commit):
    """What a commit's image will contain, read from Git alone: migration chain, head, contracts, Prefect."""
    migrations = migration_rules.commit_migrations(commit, ROOT)
    constraints = run(['git', 'show', f'{commit}:backend/runtime-constraints.txt'], cwd=ROOT, text=True)
    prefect = re.search(r'^prefect==(\S+)', constraints, re.M)
    if not prefect:
        raise ValueError(f'{commit[:12]} pins no Prefect version in backend/runtime-constraints.txt')
    return {'commit': commit, 'alembic_head': migrations['head'], 'migrations': migrations['chain'],
            'contract_revisions': migrations['contracts'], 'prefect_version': prefect.group(1)}


def image_labels(info):
    return {REVISION: info['commit'], LABELS + 'alembic-head': info['alembic_head'],
            LABELS + 'contract-revisions': ','.join(info['contract_revisions']),
            LABELS + 'prefect-version': info['prefect_version'], LABELS + 'build': 'git-archive'}


def existing_labels(name):
    """Labels of a local image, or None when no image has this name."""
    if not run(['docker', 'image', 'ls', '-q', name], text=True).strip():
        return None
    return json.loads(run(['docker', 'image', 'inspect', name, '--format', '{{json .Config.Labels}}'], text=True)) or {}


def build_images(commit):
    """Build the api and web images of a commit, or reuse them when their labels match.
    Returns (tag, kinds built). An existing tag with different labels is refused, never overwritten."""
    commit = resolve_commit(commit)
    labels, tag, built, archive = image_labels(commit_info(commit)), commit[:12], [], None
    for kind in ('api', 'web'):
        name = f'{IMAGES[kind]}:{tag}'
        existing = existing_labels(name)
        if existing is not None:
            different = sorted(key for key, value in labels.items() if existing.get(key) != value)
            if different:
                raise Refused(f'{name} exists with different labels ({", ".join(different)}); refusing to overwrite it')
            continue
        if archive is None:
            # Exactly the committed bytes: no line-ending conversion and no untracked files. Python holds the
            # binary stream end to end; a PowerShell pipe would rewrite it.
            archive = run(['git', '-c', 'core.autocrlf=false', 'archive', '--format=tar', commit], cwd=ROOT)
        flags = [f'--label={key}={value}' for key, value in
                 {**labels, 'org.opencontainers.image.created': utc_now()}.items()]
        run(['docker', 'build', '-f', DOCKERFILES[kind], '-t', name, *flags, '-'], input=archive)
        built.append(kind)
    return tag, built


def image_ids(tag):
    return {kind: run(['docker', 'image', 'inspect', f'{IMAGES[kind]}:{tag}', '--format', '{{.Id}}'], text=True).strip()
            for kind in IMAGES}


def image_kind(service):
    return 'web' if service == 'web' else 'api'


# --- Running state ---

def running_services(project):
    """Running long-lived containers of a Compose project by service; one-off `run` containers excluded."""
    ids = run(['docker', 'ps', '-q', '--filter', 'label=com.docker.compose.project=' + project], text=True).split()
    services = {}
    for record in json.loads(run(['docker', 'inspect', *ids], text=True)) if ids else []:
        labels = record['Config'].get('Labels') or {}
        if labels.get('com.docker.compose.oneoff') == 'True':
            continue
        services[labels.get('com.docker.compose.service', record['Name'])] = {
            'container': record['Id'][:12], 'image_id': record['Image'], 'revision': labels.get(REVISION),
            'working_dir': labels.get('com.docker.compose.project.working_dir')}
    return services


def psql(container, statement, database='industry_research'):
    return run(['docker', 'exec', container, 'psql', '-U', 'industry', '-d', database,
                '-At', '-v', 'ON_ERROR_STOP=1', '-c', statement], text=True).strip()


def alembic_version(container):
    if not psql(container, "SELECT to_regclass('public.alembic_version') IS NOT NULL") == 't':
        return None
    return psql(container, 'SELECT version_num FROM public.alembic_version') or None


def http_status(url, attempts=12):
    """Status of a GET, retried while a just-started server is not answering yet; None if it never does."""
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == attempts - 1:
                return error.code
        except OSError:
            if attempt == attempts - 1:
                return None
        time.sleep(5)


def http_json(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.load(response)
    except (OSError, ValueError):
        return None


def prefect_runs(api=PREFECT_API):
    """Names of pending, running or cancelling flow runs. Raises when Prefect cannot be asked."""
    body = json.dumps({'flow_runs': {'state': {'type': {'any_': ['PENDING', 'RUNNING', 'CANCELLING']}}},
                       'limit': 20}).encode()
    request = urllib.request.Request(api + '/flow_runs/filter', data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=15) as response:
        return [flow_run['name'] for flow_run in json.load(response)]


# --- Deployment directory, record and guard (design D1, D2, D5) ---

def read_ledger():
    if not LEDGER.exists():
        return []
    return [json.loads(line) for line in LEDGER.read_text(encoding='utf-8').splitlines() if line.strip()]


def current_record(ledger):
    """The record describing what serves now: the latest one that replaced services (or adopted them)."""
    return next((record for record in reversed(ledger) if record.get('replaced')), None)


def append_record(record):
    """Append-only; older scripts read the same lines and ignore fields they do not know."""
    ledger = read_ledger()
    record = {'schema_version': LEDGER_SCHEMA, 'seq': (ledger[-1]['seq'] if ledger else 0) + 1, **record}
    with LEDGER.open('a', encoding='utf-8', newline='\n') as output:
        output.write(json.dumps(record, ensure_ascii=False) + '\n')
    return record


def home_problem():
    if not HOME_FILE.exists():
        return ('No deployments/home.json here: actions that change the production service run only from the '
                'deployment directory (docs/research-deployment.md)')
    path = json.loads(HOME_FILE.read_text(encoding='utf-8')).get('path')
    if not same_path(path, ROOT):
        return f'deployments/home.json names {path}, not this checkout {ROOT}'
    return None


def service_drift(record, services):
    """Running app containers that are not the recorded deployment."""
    drift = []
    for name, info in sorted(services.items()):
        if name == 'db':
            continue
        expected_image = (record.get('images') or {}).get(image_kind(name))
        if record.get('kind') == 'adopt':
            expected_image = (record['services'].get(name) or {}).get('image_id', expected_image)
            if info['image_id'] != expected_image:
                drift.append(f'{name} runs image {info["image_id"][:19]}, the adopt record has {str(expected_image)[:19]}')
        elif info['revision'] != record['commit'] or info['image_id'] != expected_image:
            drift.append(f'{name} runs {str(info["revision"])[:12]} ({info["image_id"][:19]}), '
                         f'the record has {record["commit"][:12]} ({str(expected_image)[:19]})')
    return drift


def guard_problems(expect_head=None, containers=True):
    """The four checks of design D2: marker, clean tree, HEAD and container revisions against the record."""
    problems = [problem for problem in [home_problem()] if problem]
    dirty = run(['git', 'status', '--porcelain'], cwd=ROOT, text=True).splitlines()
    if dirty:
        problems.append('Uncommitted changes or untracked files: ' + ', '.join(line[3:] for line in dirty[:5])
                        + (' …' if len(dirty) > 5 else ''))
    current = current_record(read_ledger())
    if current is None:
        return problems + ['No deployment record yet; run adopt first (docs/research-deployment.md)']
    head, expected = git_head(), expect_head or current['commit']
    if head != expected:
        problems.append(f'HEAD {head[:12]} is not the deployed commit {expected[:12]}')
    if containers:
        problems += service_drift(current, running_services(PROJECT))
    return problems


def refuse_if(problems, action):
    if problems:
        raise Refused(f'Refusing to {action}:\n- ' + '\n- '.join(problems))


def require_home():
    """Checked before the lock, so a development checkout gets no deployments/ folder or lock file."""
    refuse_if([problem for problem in [home_problem()] if problem], 'change the production service')


def try_lock(handle):
    handle.seek(0)
    try:
        if os.name == 'nt':
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def unlock(handle):
    handle.seek(0)
    if os.name == 'nt':
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def deployment_lock(wait_seconds=0):
    """One writer at a time for deploy, rollback, backup and the other production actions.
    The OS releases the lock when the process ends, so a crash never leaves it held."""
    with LOCK.open('a+b') as handle:
        deadline = time.time() + wait_seconds
        while not try_lock(handle):
            if time.time() >= deadline:
                raise Refused('Another deploy, rollback or backup holds deployments/.lock; retry after it finishes')
            time.sleep(10)
        try:
            yield
        finally:
            unlock(handle)


def lock_held():
    with LOCK.open('a+b') as handle:
        if try_lock(handle):
            unlock(handle)
            return False
        return True


@contextlib.contextmanager
def production(action):
    """Lock, then the guard; yields the deployed tag and the validated configuration summary."""
    require_home()
    with deployment_lock(wait_seconds=3600 if action == 'backup' else 0):
        refuse_if(guard_problems(), action)
        tag = current_record(read_ledger())['tag']
        yield tag, validate(tag)


def init_home(secondary=None):
    """Mark this clone as the deployment directory (design D1). Run once, in the new clone."""
    if HOME_FILE.exists():
        raise Refused(f'{HOME_FILE} already exists')
    # A development checkout sits on a branch, and a worktree's Git data lives in another repository.
    if not (ROOT / '.git').is_dir():
        raise Refused('The deployment directory must be its own git clone, not a worktree')
    if subprocess.run(['git', 'symbolic-ref', '-q', 'HEAD'], cwd=ROOT, capture_output=True).returncode == 0:
        raise Refused('The deployment directory stays detached at a merged commit: git checkout --detach <commit> first')
    DEPLOYMENTS.mkdir(exist_ok=True)
    marker = {'path': str(ROOT), 'created_at': utc_now(), **({'secondary': secondary} if secondary else {})}
    with HOME_FILE.open('x', encoding='utf-8', newline='\n') as output:
        output.write(json.dumps(marker, indent=2) + '\n')
    return marker


def backup_secondary(secondary):
    secondary = secondary or json.loads(HOME_FILE.read_text(encoding='utf-8')).get('secondary')
    if not secondary:
        raise Refused('Give --secondary or set "secondary" in deployments/home.json; '
                      'deploy and rollback always keep a second backup copy')
    return secondary


# --- Compatibility rules shared with the drill (design D6, D7) ---

def deploy_refusals(target, db_version, busy, force=False, allow_contract=False):
    """Reasons to refuse deploying target onto a database at db_version, and the contract migrations it adds."""
    refusals, added = [], []
    if db_version is not None and db_version not in target['migrations']:
        refusals.append(f'The database is at {db_version}, which is not on the migration chain of '
                        f'{target["commit"][:12]}: a deployed migration was withdrawn or rewritten; restore a backup instead')
    elif db_version is not None:
        added = migration_rules.contracts_between(target['migrations'], target['contract_revisions'],
                                                  db_version, target['alembic_head'])
    if added and not allow_contract:
        refusals.append(f'Contract migration(s) {", ".join(added)} would be applied and the pre-deploy backup would become '
                        'the rollback boundary; re-run with --allow-contract after reading docs/research-deployment.md')
    if busy and not force:
        refusals.append(f'Prefect has {len(busy)} pending or running flow run(s) ({", ".join(busy[:5])}); '
                        'wait for them, or pass --force to interrupt them')
    return refusals, added


def chain_union(records):
    """All migration chains the records have seen, as one chain, plus every contract revision.
    An older commit cannot see newer migrations, so rollback decisions use this union."""
    chain, contracts = [], set()
    for record in records:
        migrations = record.get('migrations') or []
        longer, shorter = (migrations, chain) if len(migrations) > len(chain) else (chain, migrations)
        if longer[:len(shorter)] != shorter:
            raise ValueError('Recorded migration chains disagree: a merged migration was rewritten; restore a backup instead')
        chain = longer
        contracts.update(record.get('contract_revisions') or [])
    return chain, contracts


def rollback_refusals(target, current, db_version, records, boundary=None):
    """Reasons a rollback to target cannot reuse the database as it is (no initialize, no downgrade)."""
    try:
        chain, contracts = chain_union(records)
    except ValueError as error:
        return [str(error)]
    head, refusals = target['alembic_head'], []
    if head not in chain or db_version not in chain:
        refusals.append(f'Schema {head} or database version {db_version} is not on a recorded migration chain; '
                        'restore a backup instead')
    elif chain.index(head) > chain.index(db_version):
        refusals.append(f'The target expects schema {head}, newer than the database at {db_version}')
    else:
        crossed = migration_rules.contracts_between(chain, contracts, head, db_version)
        if crossed:
            where = (f'the rollback-boundary backup {boundary}' if boundary else
                     'the pre-deploy backup of the deploy that applied it')
            refusals.append(f'Rolling back from {db_version} to {head} crosses contract migration(s) '
                            f'{", ".join(crossed)}; restore {where} instead (docs/research-deployment.md)')
    if target['prefect_version'] != current.get('prefect_version'):
        refusals.append(f'Prefect would change from {current.get("prefect_version")} to {target["prefect_version"]}; '
                        'the Prefect server migrates its own database, so restore a backup instead')
    return refusals


def latest_boundary(ledger):
    return next((r['backup'] for r in reversed(ledger) if r.get('contract_boundary') and r.get('backup')), None)


def run_initialize(compose_fn, tag, *profile):
    """Migrations, roles and the map import on the new image while the old services keep serving."""
    compose_fn(*profile, 'run', '--rm', '--no-deps', '-T', 'initialize', tag=tag)


def start_scheduler(compose_fn, tag):
    compose_fn('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'prefect', tag=tag)
    compose_fn('--profile', 'scheduler', 'run', '--rm', '--no-deps', 'deploy', tag=tag)
    compose_fn('--profile', 'scheduler', 'up', '-d', '--no-deps', '--wait', 'worker', tag=tag)


def replace_services(compose_fn, tag, running, recreate_db=False):
    """New containers for API, web and every running scheduler or reader service. The db container is
    recreated only when explicitly asked (the first deploy from a new directory)."""
    if recreate_db:
        compose_fn('up', '-d', '--no-deps', '--force-recreate', '--wait', 'db', tag=tag)
    compose_fn('up', '-d', '--no-deps', '--wait', 'api', 'web', tag=tag)
    if 'prefect' in running or 'worker' in running:
        start_scheduler(compose_fn, tag)
    if 'reader' in running:
        compose_fn('--profile', 'reader', 'up', '-d', '--no-deps', '--wait', 'reader', tag=tag)


def smoke_checks(compose_fn, project, tag, commit, expect_alembic, api=API, web=WEB):
    """After a replacement: health, served release, /next, every container's image and revision, the schema
    version and the directory Compose ran from. Returns (all passed, details)."""
    db = compose_fn('ps', '-q', 'db', tag=tag).decode().strip()
    images, services = image_ids(tag), running_services(project)
    release = psql(db, 'SELECT release_id FROM research.release_head') if db else None
    served = (http_json(api + '/api/v2/manifest') or {}).get('release_id')
    version = alembic_version(db) if db else None
    health, page = http_status(api + '/api/health'), http_status(web + '/next')
    wrong = sorted(name for name, info in services.items() if name != 'db' and
                   (info['revision'] != commit or info['image_id'] != images[image_kind(name)]))
    elsewhere = sorted(name for name, info in services.items() if not same_path(info['working_dir'], ROOT))
    checks = {'health': {'ok': health == 200, 'status': health},
              'release': {'ok': bool(release) and served == release, 'served': served, 'database': release},
              'next': {'ok': page == 200, 'status': page},
              'containers': {'ok': not wrong and {'api', 'web'} <= set(services), 'mismatched': wrong,
                             'services': sorted(services)},
              'alembic': {'ok': version == expect_alembic, 'database': version, 'expected': expect_alembic},
              'working_dir': {'ok': not elsewhere, 'elsewhere': elsewhere}}
    return all(check['ok'] for check in checks.values()), checks


def finish(record, outcome, error=None, fallback_from=None):
    """Complete a deploy or rollback record with the state it left behind and append it."""
    services = running_services(PROJECT)
    record.update(outcome=outcome, error=str(error)[:4000] if error else None, services=services,
                  alembic_after=alembic_version(services['db']['container']) if 'db' in services else None,
                  finished_at=utc_now())
    if outcome == 'failed' and record.get('replaced') and fallback_from is not None:
        record['fallback'] = fallback(fallback_from, record)
    return append_record(record)


def fallback(ledger, failed):
    """What the maintainer can run after a failed smoke check. Never executed automatically."""
    previous = next((r for r in reversed(ledger) if r['outcome'] == 'succeeded' and r['kind'] != 'adopt'), None)
    if previous is None:
        return ('No earlier image deployment to roll back to; return to the pre-ledger images as described in '
                'docs/research-deployment.md')
    boundary = failed.get('backup') if failed.get('contract_boundary') else latest_boundary(ledger)
    refusals = rollback_refusals(previous, failed, failed.get('alembic_after'), [*ledger, failed], boundary)
    if refusals:
        return ('Rollback is refused (' + '; '.join(refusals) + f'). Restore the pre-deploy backup {failed.get("backup")} '
                'in the drill and follow docs/research-backup.md')
    return f'python scripts/research_lab.py rollback --to {previous["seq"]}'


# --- deploy, rollback, adopt, status ---

def deploy(commit, secondary=None, force=False, allow_contract=False, recreate_db=False):
    """Steps 1-3 of design D6 in the deployed version's script; the target version's script does the rest."""
    require_home()
    with deployment_lock():
        refuse_if(guard_problems(), 'deploy')
        refuse_if(exclusion_conflicts(running_containers(), listening_ports(), [p for p, _ in PORTS.values()]), 'deploy')
        backup_secondary(secondary)
        run(['git', 'fetch', '--quiet', 'origin'], cwd=ROOT)
        commit = resolve_commit(commit)
        # Reachability alone would admit commits inside a merged PR that main never pointed to.
        if commit not in run(['git', 'rev-list', '--first-parent', 'origin/main'], cwd=ROOT, text=True).split():
            raise Refused(f'Refusing to deploy: {commit[:12]} is not on the first-parent chain of origin/main; '
                          'only merged commits are deployed (rehearse others with research_drill.py)')
        token = secrets.token_hex(16)
        HANDOVER.write_text(token, encoding='utf-8')
        try:
            run(['git', 'checkout', '--quiet', '--detach', commit], cwd=ROOT)
            flags = [*(['--secondary', secondary] if secondary else []), *(['--force'] if force else []),
                     *(['--allow-contract'] if allow_contract else []), *(['--recreate-db'] if recreate_db else [])]
            code = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'research_lab.py'), 'deploy',
                                   '--commit', commit, '--handover', token, *flags], cwd=ROOT).returncode
        finally:
            HANDOVER.unlink(missing_ok=True)
            # Whatever the target script did, the checkout ends on the commit that is serving.
            current = current_record(read_ledger())
            if current and git_head() != current['commit']:
                run(['git', 'checkout', '--quiet', '--detach', current['commit']], cwd=ROOT)
    if code:
        raise SystemExit(code)


def deploy_target(commit, token, secondary=None, force=False, allow_contract=False, recreate_db=False):
    """Steps 4-10 of design D6, run by the target version's script while the parent holds the lock."""
    if not (HANDOVER.exists() and HANDOVER.read_text(encoding='utf-8') == token and lock_held()):
        raise Refused('--handover is internal to deploy; run: python scripts/research_lab.py deploy --commit <sha>')
    refuse_if(guard_problems(expect_head=commit), 'deploy')
    ledger = read_ledger()
    current, target, running = current_record(ledger), commit_info(commit), running_services(PROJECT)
    if 'db' not in running:
        raise Refused('Refusing to deploy: the research DB is not running')
    db_version = alembic_version(running['db']['container'])
    refusals, added = deploy_refusals(target, db_version, prefect_runs() if 'prefect' in running else [],
                                      force, allow_contract)
    if not same_path(running['db']['working_dir'], ROOT) and not recreate_db:
        refusals.append(f'The db container was created from {running["db"]["working_dir"]}; the first deploy from this '
                        'directory recreates it: re-run with --recreate-db (a brief full outage)')
    refuse_if(refusals, 'deploy')
    secondary, tag = backup_secondary(secondary), commit[:12]
    validate(tag)
    record = {'kind': 'deploy', 'commit': commit, 'tag': tag, **target, 'alembic_before': db_version,
              'contract_boundary': bool(added), 'replaced': False, 'rebuilt': False, 'started_at': utc_now()}
    try:
        record['backup'] = Path(backup(secondary, tag=current['tag'], boundary=added)['backup']).name
        tag, built = build_images(commit)
        record.update(images=image_ids(tag), built=built)
        run_initialize(compose, tag)
    except Exception as error:
        finish(record, 'failed', error)
        raise
    record['replaced'] = True
    try:
        replace_services(compose, tag, running, recreate_db)
        ok, record['smoke'] = smoke_checks(compose, PROJECT, tag, commit, target['alembic_head'])
        error = None if ok else 'Smoke check failed: ' + ', '.join(k for k, v in record['smoke'].items() if not v['ok'])
    except Exception as caught:
        ok, error = False, caught
    record = finish(record, 'succeeded' if ok else 'failed', error, fallback_from=ledger)
    if not ok:
        raise RuntimeError(f'{error}\nThe new services stay in place; nothing was rolled back automatically.\n'
                           f'Next step: {record["fallback"]}')
    return record


def rollback(seq, secondary=None, force=False):
    """Design D7: back to a successful record without initialize; refused across contract migrations or Prefect."""
    require_home()
    with deployment_lock():
        # Container drift is reported, not refused: rollback exists to put known images back.
        refuse_if(guard_problems(containers=False), 'roll back')
        ledger = read_ledger()
        current, running = current_record(ledger), running_services(PROJECT)
        target = next((r for r in ledger if r['seq'] == seq), None)
        if target is None or target['outcome'] != 'succeeded' or target['kind'] not in ('deploy', 'rollback'):
            raise Refused(f'Refusing to roll back: record {seq} is not a successful deploy or rollback')
        if 'db' not in running:
            raise Refused('Refusing to roll back: the research DB is not running')
        db_version = alembic_version(running['db']['container'])
        refusals = rollback_refusals(target, current, db_version, ledger, latest_boundary(ledger))
        busy = prefect_runs() if 'prefect' in running else []
        if busy and not force:
            refusals.append(f'Prefect has {len(busy)} pending or running flow run(s); wait, or pass --force')
        refuse_if(refusals, 'roll back')
        secondary = backup_secondary(secondary)
        record = {'kind': 'rollback', 'commit': target['commit'], 'tag': target['tag'], 'rolled_back_to': seq,
                  **{key: target[key] for key in ('alembic_head', 'migrations', 'contract_revisions', 'prefect_version')},
                  'alembic_before': db_version, 'contract_boundary': False, 'replaced': False,
                  'drift_before': service_drift(current, running), 'started_at': utc_now()}
        try:
            record['backup'] = Path(backup(secondary, tag=current['tag'])['backup']).name
            tag, built = build_images(target['commit'])
            # pip and npm builds are not byte-reproducible, so a rebuilt image is marked as such.
            record.update(images=image_ids(tag), built=built, rebuilt=bool(built))
            run(['git', 'checkout', '--quiet', '--detach', target['commit']], cwd=ROOT)
            validate(tag)
        except Exception as error:
            if git_head() != current['commit']:
                run(['git', 'checkout', '--quiet', '--detach', current['commit']], cwd=ROOT)
            finish(record, 'failed', error)
            raise
        record['replaced'] = True
        try:
            replace_services(compose, tag, running)
            ok, record['smoke'] = smoke_checks(compose, PROJECT, tag, target['commit'], db_version)
            error = None if ok else 'Smoke check failed: ' + ', '.join(k for k, v in record['smoke'].items() if not v['ok'])
        except Exception as caught:
            ok, error = False, caught
        record = finish(record, 'succeeded' if ok else 'failed', error)
        if not ok:
            raise RuntimeError(f'{error}\nRestore the pre-rollback backup {record["backup"]} in the drill and follow '
                               'docs/research-backup.md')
        return record


def adopt():
    """First record of a new deployment directory: the containers already running, their images tagged
    pre-ledger so they stay recoverable. Builds and replaces nothing."""
    require_home()
    with deployment_lock():
        if read_ledger():
            raise Refused('The deployment record already has entries; adopt only starts an empty record')
        refuse_if([p for p in guard_problems(containers=False) if not p.startswith('No deployment record')], 'adopt')
        services = running_services(PROJECT)
        images = {}
        for name, info in services.items():
            if name != 'db':
                images.setdefault(image_kind(name), set()).add(info['image_id'])
        if any(len(ids) > 1 for ids in images.values()):
            raise Refused('Running app services use different images; stop or fix them before adopting')
        images = {kind: ids.pop() for kind, ids in images.items()}
        for kind, image in images.items():
            run(['docker', 'tag', image, f'{IMAGES[kind]}:{PRE_LEDGER}'])
        version = alembic_version(services['db']['container']) if 'db' in services else None
        prefect = (run(['docker', 'exec', services['api']['container'], 'python', '-c',
                        'import prefect; print(prefect.__version__)'], text=True).strip() if 'api' in services else None)
        return append_record({
            'kind': 'adopt', 'outcome': 'succeeded', 'error': None, 'commit': git_head(), 'tag': PRE_LEDGER,
            'images': images, 'rebuilt': False, 'alembic_before': version, 'alembic_after': version,
            'alembic_head': version, 'migrations': None, 'contract_revisions': None, 'prefect_version': prefect,
            'backup': None, 'contract_boundary': False, 'replaced': True, 'services': services,
            'note': 'Services predate the deployment record; commit is this checkout, not the source of the images',
            'started_at': utc_now(), 'finished_at': utc_now()})


def brief(record):
    if record is None:
        return None
    return {key: record.get(key) for key in ('seq', 'kind', 'outcome', 'commit', 'tag', 'backup', 'finished_at')}


def status():
    """Read-only: what runs, what the record says and every difference between them."""
    ledger = read_ledger()
    services = running_services(PROJECT)
    report = {'directory': str(ROOT), 'marker': json.loads(HOME_FILE.read_text(encoding='utf-8')) if HOME_FILE.exists() else None,
              'head': git_head(), 'deployed': brief(current_record(ledger)), 'latest_record': brief(ledger[-1] if ledger else None),
              'records': len(ledger),
              'services': {name: {k: info[k] for k in ('container', 'image_id', 'revision')} for name, info in services.items()},
              'alembic_version': alembic_version(services['db']['container']) if 'db' in services else None}
    if not ledger:
        report['note'] = 'No deployment record yet'
    report['problems'] = guard_problems()
    return report


def check():
    """Read-only: secrets format, Compose rules for the deployed tag, and every guard problem."""
    current = current_record(read_ledger())
    report = validate(current['tag'] if current else PLACEHOLDER_TAG)
    report['deployed'] = brief(current)
    report['problems'] = guard_problems()
    return report


# --- Existing operations ---

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


def restore(source, database, tag):
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
    compose('up', '-d', '--wait', 'db', tag=tag)
    target = compose('ps', '-q', 'db', tag=tag).decode().strip()
    if database_snapshot(target, 'industry_research'):
        raise ValueError('Target database is not empty; preserved without restore')
    compose('cp', str(backup), 'db:/tmp/research-restore.dump', tag=tag)
    compose('exec', '-T', 'db', 'pg_restore', '-U', 'industry', '-d', 'industry_research',
            '--no-owner', '--no-privileges', '--exit-on-error', '/tmp/research-restore.dump', tag=tag)
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


def is_boundary(folder):
    try:
        return bool(json.loads((folder / 'manifest.json').read_text(encoding='utf-8')).get('rollback_boundary'))
    except (OSError, ValueError):
        return True  # an unreadable manifest is left alone


def prune(root, keep_days, now):
    removed = []
    for folder in sorted(root.iterdir()) if root.exists() else []:
        # Only complete, script-named backups are eligible; rollback boundaries and anything else are left alone.
        if (folder.is_dir() and STAMP.fullmatch(folder.name) and (folder / 'manifest.json').exists()
                and not is_boundary(folder)):
            created = calendar.timegm(time.strptime(folder.name, '%Y%m%dT%H%M%SZ'))
            if now - created > keep_days * 86400:
                for item in folder.iterdir():
                    item.unlink()
                folder.rmdir()
                removed.append(folder.name)
    return removed


def log_backup(stamp, status, seconds):
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    with (BACKUP_ROOT / 'backup-log.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps({'stamp': stamp, 'status': status, 'seconds': seconds}) + '\n')


def backup(secondary=None, keep_days=30, *, tag, boundary=()):
    """Daily and pre-deploy backup: DB dump, roles without passwords, managed Git refs, assets and the
    active release. The caller holds deployments/.lock. A pre-deploy backup that precedes contract
    migrations (boundary) is the rollback boundary and is never pruned."""
    before = protected_snapshot()
    started = time.time()
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(started))
    folder = BACKUP_ROOT / stamp
    folder.mkdir(parents=True)
    status = 'failed'
    try:
        db = compose('ps', '-q', 'db', tag=tag).decode().strip()
        if not db:
            raise RuntimeError('Research DB is not running; nothing backed up')
        for attempt in range(3):
            inventory, head = db_inventory(db)
            # Direct binary capture: the custom dump never passes through a text decoder.
            (folder / 'database.dump').write_bytes(compose('exec', '-T', 'db', 'pg_dump', '-U', 'industry',
                                                           '-d', 'industry_research', '-Fc', tag=tag))
            if db_inventory(db)[0] == inventory:
                break
        else:
            raise RuntimeError('Database kept changing during backup; retry when writes are idle')
        (folder / 'roles.sql').write_bytes(compose('exec', '-T', 'db', 'pg_dumpall', '-U', 'industry',
                                                   '--roles-only', '--no-role-passwords', tag=tag))
        tool = ('run', '--rm', '--no-deps', '-T', 'initialize')
        (folder / 'git.bundle').write_bytes(compose(*tool, 'git', '-C', GIT_REPO, 'bundle', 'create', '-', '--all', tag=tag))
        refs = compose(*tool, 'git', '-C', GIT_REPO, 'show-ref', tag=tag).decode().splitlines()
        (folder / 'assets.tar').write_bytes(compose(*tool, 'tar', '-C', ASSET_DIR, '-cf', '-', '.', tag=tag))
        files = {name: sha256_file(folder / name) for name in ('database.dump', 'roles.sql', 'git.bundle', 'assets.tar')}
        api = running_services(PROJECT).get('api') or {}
        manifest = {'created_at': stamp, 'duration_seconds': round(time.time() - started, 1), 'files': files,
                    'sizes': {name: (folder / name).stat().st_size for name in files}, 'active_release': head,
                    'tables': inventory, 'git_refs': refs, 'api_image': api.get('image_id'),
                    'api_revision': api.get('revision'), 'alembic_version': alembic_version(db),
                    'rollback_boundary': bool(boundary), 'contract_revisions': list(boundary),
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
        log_backup(stamp, status, round(time.time() - started, 1))


def snapshot_command(folder, release_id=None):
    """Export from the running API image; the container sees only the output folder, never the host checkout."""
    if release_id and not re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', release_id):
        raise ValueError('Use a full research release ID')
    command = ['run', '--rm', '--no-deps', '-T', '-v', Path(folder).resolve().as_posix() + ':/export',
               'api', 'python', '-m', 'app.public_snapshot', '--out', '/export']
    return command + (['--release-id', release_id] if release_id else [])


def public_snapshot(release_id=None, *, tag):
    folder = ROOT / 'public-snapshot'
    folder.mkdir(exist_ok=True)
    output = compose(*snapshot_command(folder, release_id), tag=tag).decode('utf-8', errors='replace')
    result = json.loads(output.strip().splitlines()[-1])
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
    from app.public_snapshot import leak_findings
    # The container already scanned its own environment; this pass uses the host's secret file as well.
    pairs = dict(line.split('=', 1) for line in ENV_FILE.read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))
    findings = leak_findings(folder / result['folder'], [pairs[key] for key in SECRET_KEYS if pairs.get(key)])
    if findings:
        raise RuntimeError('Snapshot contains private content:\n' + '\n'.join(findings[:50]))
    return {'folder': str(folder / result['folder']), 'published_at': result['published_at'], 'counts': result['counts']}


ACTIONS = ['setup', 'check', 'status', 'init-home', 'adopt', 'deploy', 'rollback', 'up', 'start', 'stop',
           'scheduler-start', 'reader-start', 'reader-stop', 'restore', 'seed-git', 'bootstrap', 'backup',
           'public-snapshot']


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=ACTIONS)
    parser.add_argument('--commit', help='deploy: a commit on the first-parent chain of origin/main; '
                                         'seed-git, bootstrap: a commit reachable from HEAD (default HEAD)')
    parser.add_argument('--to', type=int, help='rollback: the deployment record seq to return to (see status)')
    parser.add_argument('--force', action='store_true', help='deploy, rollback: interrupt running Prefect flow runs')
    parser.add_argument('--allow-contract', action='store_true',
                        help='deploy: apply contract migrations; the pre-deploy backup becomes the rollback boundary')
    parser.add_argument('--recreate-db', action='store_true',
                        help='deploy: recreate the db container from this directory (first deploy only; brief full outage)')
    parser.add_argument('--handover', help=argparse.SUPPRESS)
    parser.add_argument('--release-id', help='public-snapshot: the published release to export (default: the current one)')
    parser.add_argument('--secondary', help='second storage device for the verified backup copy '
                                            '(deploy, rollback: default from deployments/home.json)')
    parser.add_argument('--keep-days', type=int, default=30)
    parser.add_argument('--source-container', default='industryflow-reading-db')
    parser.add_argument('--source-database', default='industry_reading')
    return parser


def main():
    args = build_parser().parse_args()
    if args.action == 'up':
        raise SystemExit('up no longer builds or replaces services. Deploy a merged commit with\n'
                         '  python scripts/research_lab.py deploy --commit <sha>\n'
                         'and start stopped services with start (docs/research-deployment.md).')
    if args.action in ('deploy', 'rollback') and not (args.commit if args.action == 'deploy' else args.to):
        build_parser().error('deploy needs --commit; rollback needs --to')
    if args.action == 'setup':
        setup()
        report = {'setup': 'ok', 'env_file': str(ENV_FILE)}
    elif args.action == 'check':
        report = check()
    elif args.action == 'status':
        report = status()
    elif args.action == 'init-home':
        report = init_home(args.secondary)
    elif args.action == 'adopt':
        report = adopt()
    elif args.action == 'deploy':
        if args.handover:
            report = deploy_target(args.commit, args.handover, args.secondary, args.force, args.allow_contract,
                                   args.recreate_db)
        else:
            return deploy(args.commit, args.secondary, args.force, args.allow_contract, args.recreate_db)
    elif args.action == 'rollback':
        report = rollback(args.to, args.secondary, args.force)
    elif args.action == 'backup':
        try:
            with production('backup') as (tag, report):
                report['result'] = backup(args.secondary, args.keep_days, tag=tag)
        except Refused as refusal:
            if HOME_FILE.exists():
                log_backup(time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), 'refused: ' + str(refusal)[:500], 0)
            raise
    else:
        with production(args.action) as (tag, report):
            before = protected_snapshot()
            if args.action in ('start', 'reader-start'):
                refuse_if(exclusion_conflicts(running_containers(), listening_ports(), [p for p, _ in PORTS.values()]),
                          args.action)
            if args.action == 'start':
                compose('start', 'api', 'web', tag=tag)
            elif args.action == 'stop':
                # Release every shared port (and stop fetching) so the original service can take the origin back.
                compose('--profile', 'scheduler', '--profile', 'reader', 'stop', 'reader', 'worker', 'prefect', 'web', 'api', tag=tag)
            elif args.action == 'scheduler-start':
                start_scheduler(compose, tag)
            elif args.action == 'reader-start':
                compose('--profile', 'reader', 'up', '-d', '--no-deps', '--wait', 'reader', tag=tag)
            elif args.action == 'reader-stop':
                compose('--profile', 'reader', 'stop', 'reader', tag=tag)
            elif args.action == 'seed-git':
                commit = resolve_commit(args.commit or 'HEAD')
                folder = ROOT / '.work/research-lab'
                folder.mkdir(parents=True, exist_ok=True)
                bundle = folder / ('seed-' + commit + '.bundle')
                # HEAD is a named ref and retains the selected ancestor; a bare object ID
                # by itself is not a valid bundle inclusion ref on every Git version.
                if run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], cwd=ROOT) != b'':
                    raise ValueError('Seed commit must be reachable from HEAD')
                run(['git', 'bundle', 'create', str(bundle), 'HEAD'], cwd=ROOT)
                output = compose('run', '--rm', '--no-deps', '-T', 'initialize', 'python', '-m', 'app.research_git',
                                 'seed', '--commit', commit, input=bundle.read_bytes(), tag=tag)
                report['managed_git'] = output.decode().strip()
            elif args.action == 'bootstrap':
                commit = resolve_commit(args.commit or 'HEAD')
                archive = run(['git', 'archive', '--format=tar', commit, 'industry-map',
                               'data/company-research.yaml', 'data/theme-indicators.yaml'], cwd=ROOT)
                output = compose('run', '--rm', '--no-deps', '-T', 'initialize', 'python', '-m', 'app.research_compile',
                                 '--commit', commit, '--bootstrap', input=archive, tag=tag)
                result = json.loads(output)
                run(['git', 'update-ref', 'refs/research/releases/' + result['release_id'], commit], cwd=ROOT)
                folder = ROOT / '.work/research-lab'
                folder.mkdir(parents=True, exist_ok=True)
                (folder / 'bootstrap.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                report['result'] = {key: value for key, value in result.items() if key != 'search_plans'}
            elif args.action == 'public-snapshot':
                report['result'] = public_snapshot(args.release_id, tag=tag)
            elif args.action == 'restore':
                result = restore(args.source_container, args.source_database, tag)
                report['restored_tables'] = {k: int(v.split(':')[0]) for k, v in result['tables'].items()}
            verify_protected(before)
            report['protected_services_unchanged'] = True
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
