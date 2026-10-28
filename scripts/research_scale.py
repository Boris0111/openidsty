"""Task 9.2 scaled dataset in the restore drill: 300 companies and 3,000 relations.

python scripts/research_scale.py            # restore drill must already serve the real data with the drill owner

1. Copy HEAD's authored map and add clearly synthetic companies (company-synth-NNN), taxonomy placements and
   relations until there are 300 companies and 3,000 relations; validate it with the real map validator.
2. Try the normal owner draft import (recorded: a 3,000-relation manifest exceeds the draft YAML token limit),
   then project it as the drill's head with research_compile in one drill-DB transaction (test-only path).
   Everything stays in the drill DB, never the preview. Company financials were removed, so no financial
   observations are generated.
"""
import io
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tarfile
import uuid
import yaml

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from research_drill import compose as drill_compose, env_values, running_revision  # noqa: E402
from research_integration import Session  # noqa: E402

TREE = ROOT / '.work/research-scale/tree'
COMPANIES, RELATIONS = 300, 3000
DAY = '2026-10-19'
SOURCE = 'synthetic-load-test'
HEADINGS = ('供應角色', '研究界線', '產品與用途', '商業模式', '客戶與供應商', '競爭與替代', '業務曝險', '風險', '財務可取性')
DB = ['docker', 'exec', '-i', 'industryflow-research-drill-db-1', 'psql', '-U', 'industry', '-d', 'industry_research',
      '-v', 'ON_ERROR_STOP=1', '-At']


def remove(path):
    # Git marks object files read-only on Windows; clear the flag before deleting the scratch copy.
    def writable(function, name, _):
        os.chmod(name, 0o700)
        function(name)
    shutil.rmtree(path, onexc=writable)


def build_tree():
    if TREE.exists():
        remove(TREE)
    archive = subprocess.check_output(['git', '-c', 'core.autocrlf=false', 'archive', 'HEAD', 'industry-map',
                                       'data/company-research.yaml', 'data/theme-indicators.yaml'], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(TREE, filter='data')
    maps = TREE / 'industry-map'
    real = sorted(p.stem for p in (maps / 'companies').glob('*.md'))
    roles = sorted(p.stem for p in (maps / 'roles').glob('*.md'))
    synthetic = [f'company-synth-{n:03d}' for n in range(1, COMPANIES - len(real) + 1)]
    for index, entity in enumerate(synthetic, 1):
        front = {'schema-version': 'research-v1', 'entity-id': entity, 'kind': 'company', 'name-zh': f'合成測試公司 {index:03d}',
                 'aliases': [], 'summary': '效能測試用的合成公司，不代表任何真實企業。', 'legacy-keys': [], 'listings': [],
                 'source-identifiers': [], 'research-depth': 'deep', 'reviewed': DAY, 'roles': [],
                 'claims': [{'id': 'synthetic-basis', 'statement': '此主張只供效能測試，引用合成來源。', 'confidence': 'well-supported',
                             'conditions': ['合成負載測試資料'], 'reviewed': DAY,
                             'evidence': [{'source-id': SOURCE, 'url': 'https://example.com/synthetic-load-test', 'locator': '合成測試',
                                           'read-scope': '合成測試', 'stance': 'supporting', 'applicable-period': '2026'}]}],
                 'gaps': [{'status': 'not-applicable', 'reason': '合成負載測試資料，不代表研究內容。'}]}
        body = '\n\n'.join(f'## {heading}\n\n合成測試段落，供效能量測使用。' for heading in HEADINGS)
        (maps / 'companies' / f'{entity}.md').write_text('---\n' + yaml.safe_dump(front, allow_unicode=True, sort_keys=False)
                                                        + '---\n\n' + body + '\n', encoding='utf-8', newline='\n')
    registry = (maps / 'sources.yaml').read_text(encoding='utf-8')
    marker = '  technical-documents:\n'
    entry = yaml.safe_dump([{'id': SOURCE, 'name': '合成負載測試來源', 'url': 'https://example.com/synthetic-load-test',
                             'type': 'technical-documents', 'access': 'free', 'reachability': 'verified', 'checked': DAY,
                             'segments': [], 'themes': [], 'notes': '只在擴大效能測試資料使用，不進預覽或正式 release。'}],
                           allow_unicode=True, sort_keys=False)
    at = registry.index(marker, registry.index('\nglobal:\n')) + len(marker)
    (maps / 'sources.yaml').write_text(registry[:at] + ''.join('  ' + l + '\n' for l in entry.rstrip('\n').split('\n')) + registry[at:],
                                       encoding='utf-8', newline='\n')
    relations = yaml.safe_load((maps / 'research-relations.yaml').read_text(encoding='utf-8'))
    for index, entity in enumerate(synthetic):
        relations['taxonomy'].append({'id': f'taxonomy-{entity}', 'parent': roles[index % len(roles)], 'child': entity})
    rng, pairs = random.Random(92), {tuple(sorted((r['source'], r['target']))) for r in relations['relations']}
    while len(relations['relations']) < RELATIONS:
        source = rng.choice(synthetic)
        target = rng.choice(real) if rng.random() < 0.3 else rng.choice(synthetic)
        pair = tuple(sorted((source, target)))
        if source == target or pair in pairs:
            continue
        pairs.add(pair)
        supply = rng.random() < 0.5
        relations['relations'].append({
            'id': f'relation-synth-{len(relations["relations"]):04d}', 'source': source, 'target': target,
            'kind': 'named-supply' if supply else 'competition', 'direction': 'directed' if supply else 'symmetric',
            'mechanism': '合成負載測試關係', 'conditions': ['合成負載測試資料'], 'confidence': 'well-supported', 'reviewed': DAY,
            'claim-refs': [{'entity-id': source, 'claim-id': 'synthetic-basis'}]})
    (maps / 'research-relations.yaml').write_text(yaml.safe_dump(relations, allow_unicode=True, sort_keys=False, width=1000),
                                                  encoding='utf-8', newline='\n')
    result = subprocess.run([sys.executable, str(SCRIPTS / 'validate_map.py'), '--map-dir', str(maps)], capture_output=True,
                            text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    if result.returncode:
        raise RuntimeError('synthetic map does not validate: ' + (result.stdout + result.stderr)[-2000:])
    return synthetic, len(relations['relations'])


def publish(owner):
    created = owner.call('POST', '/api/admin/drafts', {})[1]
    draft = created['draft_id']
    exported = owner.call('GET', f'/api/admin/drafts/{draft}/export')[1]
    files = dict(exported['files'])
    for path in TREE.rglob('*'):
        name = path.relative_to(TREE).as_posix()
        if path.is_file() and not name.startswith('industry-map/assets/') and name != 'industry-map/README.md':
            files[name] = path.read_text(encoding='utf-8')
    status, imported = owner.call('POST', f'/api/admin/drafts/{draft}/import', {**exported, 'files': files},
                                  headers={'If-Match': f'"{exported["revision"]}"'})
    if status != 200:
        raise RuntimeError(f'import failed {status}: {str(imported)[:500]}')
    valid = owner.call('POST', f'/api/admin/drafts/{draft}/validate')[1]
    if not valid.get('valid'):
        raise RuntimeError('synthetic draft invalid: ' + json.dumps(valid, ensure_ascii=False)[:1500])
    base = owner.call('GET', '/api/admin/releases')[1]['active_release_id']
    job = owner.call('POST', f'/api/admin/drafts/{draft}/publish', {'base_release_id': base, 'revision': imported['revision'],
                     'reason': '擴大效能測試資料（合成）'}, headers={'Idempotency-Key': str(uuid.uuid4())})[1]
    ran = subprocess.run([sys.executable, 'research_drill.py', 'run-job', '--job', job['job_id']], cwd=SCRIPTS, capture_output=True,
                         text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, check=True)
    return json.loads(ran.stdout), len(json.dumps(files, ensure_ascii=False).encode())


def project():
    """Commit the synthetic tree in a scratch repository and project it as the drill head (test-only)."""
    repo = ROOT / '.work/research-scale/git'
    if repo.exists():
        remove(repo)
    shutil.copytree(TREE, repo)
    git = lambda *a: subprocess.run(['git', '-c', 'core.autocrlf=false', '-C', str(repo), *a], capture_output=True, text=True, check=True).stdout
    git('init', '-q'); git('add', '-A')
    git('-c', 'user.name=research-scale', '-c', 'user.email=scale@localhost.invalid', 'commit', '-q', '-m', 'synthetic scaled dataset')
    commit = git('rev-parse', 'HEAD').strip()
    archive = subprocess.check_output(['git', '-c', 'core.autocrlf=false', '-C', str(repo), 'archive', '--format=tar', commit, 'industry-map',
                                       'data/company-research.yaml', 'data/theme-indicators.yaml'])
    script = '\n'.join([
        'import sys, json',
        'from sqlalchemy import create_engine, text',
        'from app.config import DATABASE_URL',
        'from app.research_compile import compile_archive, project',
        'bundle = compile_archive(sys.stdin.buffer.read())',
        'with create_engine(DATABASE_URL).begin() as connection:',
        '    connection.execute(text("DELETE FROM research.release_head"))',
        f'    print(json.dumps(project(connection, bundle, {commit!r}, True)))'])
    # The drill's own secrets and the image the drill API runs; the same path every drill script uses.
    output = drill_compose('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'bootstrap', 'python', '-c', script,
                           input=archive, tag=running_revision()[:12])
    return {'commit': commit, **json.loads(output.decode().strip().splitlines()[-1])}


def sql(statement):
    return subprocess.run(DB, input=statement, capture_output=True, text=True, encoding='utf-8', check=True).stdout.strip()


def main():
    synthetic, relation_count = build_tree()
    owner = Session()
    owner.login(env_values()['DRILL_OWNER_PASSWORD'])
    try:
        job, payload_bytes = publish(owner)
        draft = {'status': 'published', 'job': job, 'payload_bytes': payload_bytes}
    except RuntimeError as error:
        draft = {'status': 'rejected', 'reason': str(error)[:300]}
    owner.call('DELETE', '/api/admin/session')
    projected = project() if draft['status'] == 'rejected' else None
    counts = {
        'companies': int(sql("SELECT count(*) FROM research.entity_snapshots s JOIN research.release_head h USING (release_id) WHERE s.kind='company';")),
        'relations': int(sql('SELECT count(*) FROM research.relations r JOIN research.release_head h USING (release_id);')),
        'authored_relations': relation_count}
    report = {'draft_path': draft, 'projection': projected, 'release': counts}
    folder = ROOT / '.work/research-load'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'scaled-dataset.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
