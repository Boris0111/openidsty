"""Real authoring content, hostile imports and identical form/file compilation."""
import io
import hashlib
from pathlib import Path
import subprocess
import tarfile
import uuid
import pytest
import yaml
from app.config import ROOT
from app.research_documents import (export_files, normalize_payload, validate_payload,
                                    form_document, safe_yaml, MAX_DRAFT, materialize)
from app.research_git import ManagedGit, read_archive, make_archive, safe_path
from app.research_cli import export_directory, import_directory, Client
from app.research_documents import upload_asset


@pytest.fixture(scope='module')
def authored(tmp_path_factory):
    if (ROOT / '.git').exists():
        archive = subprocess.check_output(['git', '-c', 'core.autocrlf=false', 'archive', 'HEAD', 'industry-map',
            'data/company-research.yaml', 'data/theme-indicators.yaml'], cwd=ROOT)
    else:
        names = [path for path in (ROOT / 'industry-map').rglob('*') if path.is_file()]
        names += [ROOT / 'data/company-research.yaml', ROOT / 'data/theme-indicators.yaml']
        archive = make_archive({path.relative_to(ROOT).as_posix(): path.read_bytes() for path in names})
    root = tmp_path_factory.mktemp('research-authoring-assets')
    payload = export_files(read_archive(archive), root)
    return payload, root


def expected_snapshots(files):
    # One snapshot per research page, legacy segment and theme; derived so the authored map can grow.
    folders = {'companies', 'applications', 'roles', 'products', 'concepts', 'research', 'ai-server', 'semiconductor', 'themes'}
    return sum(1 for path in files if path.endswith('.md') and not path.endswith('README.md')
               and path.count('/') == 2 and path.split('/')[1] in folders)


def test_real_content_round_trip_and_form_matches_file(authored):
    payload, root = authored
    valid, bundle = validate_payload(payload, root)
    assert valid['valid'] and len(bundle['snapshots']) == expected_snapshots(payload['files']) >= 254
    path = 'industry-map/companies/company-auras.md'
    _, front, prose = payload['files'][path].split('---', 2)
    fields = safe_yaml(front)
    fields['summary'] = '合成表單測試，不代表新增公司研究。'
    content = form_document(fields, prose.strip() + '\n\n合成測試段落。\n')
    form = {**payload, 'files': {**payload['files'], path: content}}
    exported = normalize_payload(form)
    imported = normalize_payload({**exported, 'files': dict(exported['files'])})
    a, left = validate_payload(exported, root)
    b, right = validate_payload(imported, root)
    assert a == b and left == right and a['valid']
    assert bundle['snapshots'] != left['snapshots']


@pytest.mark.parametrize('content', ['<script>alert(1)</script>', '<iframe src="https://evil.example"></iframe>',
    '[開啟](javascript:alert(1))', '![追蹤](https://evil.example/pixel.png)'])
def test_unsafe_markdown_is_rejected(authored, content):
    payload, _ = authored
    changed = {**payload, 'files': {**payload['files'], 'industry-map/research/research-test.md': content}}
    with pytest.raises(ValueError):
        normalize_payload(changed)


def test_service_yaml_uses_libyaml():
    # CI and the API image ship PyYAML wheels with libyaml; a pure-Python fallback would be a silent slowdown.
    import app.research_documents as documents
    assert yaml.__with_libyaml__
    assert issubclass(documents.UniqueLoader, yaml.CSafeLoader)


@pytest.mark.parametrize('content', ['a: 1\na: 2', 'a: &x [*x]', 'a: !!python/object:evil {}'])
def test_ambiguous_or_executable_yaml_is_rejected(content):
    with pytest.raises((ValueError, yaml.YAMLError)):
        safe_yaml(content)


def flat_sequence(events):
    # Stream, document and sequence start/end are six events; every scalar adds one.
    # Quoted scalars skip implicit-tag resolution, which keeps this 400,000-event case quick.
    return '[' + ','.join(['"x"'] * (events - 6)) + ']'


def test_yaml_event_limit_is_exact():
    from app.research_documents import MAX_YAML_EVENTS
    assert len(safe_yaml(flat_sequence(MAX_YAML_EVENTS))) == MAX_YAML_EVENTS - 6
    with pytest.raises(ValueError, match='深度或數量'):
        safe_yaml(flat_sequence(MAX_YAML_EVENTS + 1))


def test_yaml_depth_limit():
    assert safe_yaml('[' * 32 + ']' * 32) is not None
    with pytest.raises(ValueError, match='深度或數量'):
        safe_yaml('[' * 33 + ']' * 33)
    block = ''.join('  ' * level + f'k{level}:\n' for level in range(33)) + '  ' * 33 + 'leaf: 1\n'
    with pytest.raises(ValueError, match='深度或數量'):
        safe_yaml(block)


def test_alias_expansion_beyond_node_limit_is_rejected():
    # Ten aliases per level: few parser events, about a million nodes once expanded.
    levels = ['l0: &l0 [1,1,1,1,1,1,1,1,1,1]']
    levels += [f'l{n}: &l{n} [' + ','.join([f'*l{n - 1}'] * 10) + ']' for n in range(1, 6)]
    with pytest.raises(ValueError, match='展開後'):
        safe_yaml('\n'.join(levels))


def test_rejected_file_is_named(authored):
    payload, _ = authored
    path = 'industry-map/research/research-test.md'
    with pytest.raises(ValueError, match=path):
        normalize_payload({**payload, 'files': {**payload['files'], path: '<script>alert(1)</script>'}})


@pytest.fixture
def checked(monkeypatch):
    import app.research_documents as documents
    calls, original = [], documents.check_document
    def counting(path, content):
        calls.append(path)
        return original(path, content)
    monkeypatch.setattr(documents, 'check_document', counting)
    return calls


COMPANY = 'industry-map/companies/company-auras.md'


def test_save_checks_only_edited_files(authored, checked):
    from app.research_documents import normalize_changes
    payload, _ = authored
    edited = {**payload, 'files': {**payload['files'], COMPANY: payload['files'][COMPANY] + '\n補充一段。\n'}}
    result = normalize_changes(payload, edited)
    assert checked == [COMPANY]
    checked.clear()
    assert result == normalize_payload(edited) and len(checked) == len(payload['files']) - 1  # README is exempt


def test_unchanged_file_is_trusted_from_the_previous_revision(authored, checked):
    from app.research_documents import normalize_changes
    payload, _ = authored
    # A file that only a newer rule would reject: the save leaves it alone, full validation does not.
    stale = 'industry-map/research/research-legacy.md'
    previous = {**payload, 'files': {**payload['files'], stale: '<b>舊規則允許的內容</b>'}}
    edited = {**previous, 'files': {**previous['files'], COMPANY: payload['files'][COMPANY] + '\n補充。\n'}}
    assert stale in normalize_changes(previous, edited)['files'] and checked == [COMPANY]
    with pytest.raises(ValueError, match=stale):
        normalize_payload(edited)


def test_incremental_save_still_rejects_new_collisions_and_size(authored):
    from app.research_documents import normalize_changes
    payload, _ = authored
    added = 'industry-map/research/research-new.md'
    with pytest.raises(ValueError, match=added):
        normalize_changes(payload, {**payload, 'files': {**payload['files'], added: '<script>x</script>'}})
    # Text paths are lowercase-only, so a case-colliding rename is already an unsafe path.
    with pytest.raises(ValueError, match='研究範圍'):
        normalize_changes(payload, {**payload, 'files': {**payload['files'], 'industry-map/companies/Company-Auras.md': 'x'}})
    with pytest.raises(ValueError, match='5 MiB'):
        normalize_changes(payload, {**payload, 'files': {**payload['files'], added: 'x' * MAX_DRAFT}})
    removed = {**payload, 'files': {path: text for path, text in payload['files'].items() if path != COMPANY}}
    assert COMPANY not in normalize_changes(payload, removed)['files']


@pytest.fixture
def tiny_git(tmp_path):
    """A seeded managed repository with only the files a research archive needs."""
    source = tmp_path / 'tiny'
    files = {'industry-map/README.md': '# Schema\n', COMPANY: '---\nentity-id: company-auras\n---\n\n本文\n',
             'data/company-research.yaml': 'companies: []\n', 'data/theme-indicators.yaml': 'themes: []\n'}
    for name, text in files.items():
        (source / name).parent.mkdir(parents=True, exist_ok=True)
        (source / name).write_text(text, encoding='utf-8', newline='\n')
    git = lambda *args: subprocess.check_output(['git', '-C', str(source), '-c', 'core.autocrlf=false', '-c', 'user.name=Test',
                                                 '-c', 'user.email=test@localhost', *args])
    git('init', '-q'); git('add', '.'); git('commit', '-q', '-m', 'tiny baseline')
    head = git('rev-parse', 'HEAD').decode().strip()
    git('bundle', 'create', str(tmp_path / 'tiny.bundle'), 'HEAD')
    managed = ManagedGit(tmp_path / 'managed')
    managed.seed((tmp_path / 'tiny.bundle').read_bytes(), head)
    return managed, head, files


def test_managed_git_reads_one_file(tiny_git):
    from app.research_git import MissingResearchFile
    managed, head, files = tiny_git
    assert managed.file(head, COMPANY) == managed.files(head)[COMPANY] == files[COMPANY].encode()
    with pytest.raises(MissingResearchFile):
        managed.file(head, 'industry-map/companies/company-missing.md')
    assert issubclass(MissingResearchFile, ValueError)
    for commit in ('0' * 40, 'HEAD', head[:12]):
        with pytest.raises(ValueError):
            managed.file(commit, COMPANY)
    for path in ('../.env', 'industry-map/.git/config', 'industry-map/companies/x.py', 'backend/app/main.py'):
        with pytest.raises(ValueError):
            managed.file(head, path)


def test_save_baseline_check_reads_only_the_schema_file(tiny_git, monkeypatch):
    import app.research_drafts as drafts
    from app.research_http import ResearchError
    managed, head, files = tiny_git
    monkeypatch.setenv('RESEARCH_GIT_ROOT', str(managed.root))
    monkeypatch.setattr(drafts, 'base_release', lambda connection, release_id=None: {'git_commit': head})
    monkeypatch.setattr(ManagedGit, 'files', lambda *_: pytest.fail('a save must not archive the whole base'))
    drafts.protect_baseline(None, {'base_release_id': None}, {'files': files})
    with pytest.raises(ResearchError) as rejected:
        drafts.protect_baseline(None, {'base_release_id': None},
                                {'files': {**files, 'industry-map/README.md': '# Schema\n改寫\n'}})
    assert rejected.value.status == 422 and rejected.value.code == 'draft-rejected'


@pytest.mark.slow
def test_scaled_relation_manifest_is_accepted(scaled_tree):
    manifest = (scaled_tree / 'industry-map/research-relations.yaml').read_text(encoding='utf-8')
    assert len(safe_yaml(manifest)['relations']) == 3000


@pytest.mark.parametrize('path', ['../.env', 'industry-map/../backend/app/main.py',
    'industry-map/companies/../../.env', 'C:/Users/User/.env', 'industry-map\\companies\\x.md',
    'industry-map/.git/config', 'industry-map/companies/x.py', 'industry-map/README.md'])
def test_edit_paths_cannot_escape_or_modify_schema(path):
    with pytest.raises(ValueError):
        safe_path(path, write=True)


def test_size_limit_and_missing_asset_do_not_compile(authored):
    payload, root = authored
    with pytest.raises(ValueError):
        normalize_payload({**payload, 'files': {'industry-map/research/research-test.md': 'x' * MAX_DRAFT}})
    altered = {**payload, 'assets': {**payload['assets'], 'industry-map/assets/missing.svg': 'a' * 64}}
    result, compiled = validate_payload(altered, root)
    assert not result['valid'] and compiled is None


def test_managed_git_does_not_touch_development_index_or_allow_schema_edits(authored, tmp_path):
    payload, root = authored
    development = ROOT
    if not (development / '.git').exists():
        development = tmp_path / 'development'
        development.mkdir()
        subprocess.run(['git', 'init', str(development)], check=True, capture_output=True)
        for name, value in materialize(payload, root).items():
            target = development / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        subprocess.run(['git', '-C', str(development), 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(development), '-c', 'user.name=Test', '-c', 'user.email=test@localhost', 'commit', '-m', 'Synthetic test baseline'], check=True, capture_output=True)
    index_name = subprocess.check_output(['git', 'rev-parse', '--git-path', 'index'], cwd=development, text=True).strip()
    index_path = development / index_name
    before = hashlib.sha256(index_path.read_bytes()).hexdigest()
    bundle = tmp_path / 'content.bundle'
    subprocess.run(['git', 'bundle', 'create', str(bundle), 'HEAD'], cwd=development, check=True, capture_output=True)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=development, text=True).strip()
    managed = ManagedGit(tmp_path / 'isolated-git')
    managed.seed(bundle.read_bytes(), head)
    files = materialize(payload, root)
    path = 'industry-map/companies/company-auras.md'
    files[path] += '\n\n合成 Git 隔離測試。\n'.encode()
    commit = managed.commit_files(head, files)
    assert commit != head and managed.files(commit)[path] == files[path]
    release = uuid.uuid4()
    managed.protect_release(release, commit)
    managed.protect_release(release, commit)
    with pytest.raises(ValueError):
        managed.protect_release(release, head)
    assert hashlib.sha256(index_path.read_bytes()).hexdigest() == before
    assert not list((managed.root / 'worktrees').iterdir())
    files['industry-map/README.md'] += b'changed'
    with pytest.raises(ValueError):
        managed.commit_files(head, files)


def test_archive_rejects_executable_and_case_colliding_paths():
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        info = tarfile.TarInfo('industry-map/companies/company-test.md')
        info.mode, info.size = 0o755, 1
        archive.addfile(info, io.BytesIO(b'x'))
    with pytest.raises(ValueError):
        read_archive(stream.getvalue())


def test_cli_markdown_directory_roundtrip_and_credential_free_metadata(authored, tmp_path):
    payload, _ = authored
    exported = {'draft_id': str(uuid.uuid4()), 'base_release_id': str(uuid.uuid4()), 'revision': 3, **payload}
    directory = tmp_path / 'exchange'
    export_directory(exported, directory)
    assert import_directory(directory) == exported
    metadata = (directory / 'draft.json').read_text(encoding='utf-8')
    assert 'csrf' not in metadata and 'password' not in metadata and 'cookie' not in metadata
    target = directory / 'industry-map/companies/company-auras.md'
    target.write_text(target.read_text(encoding='utf-8') + '\n合成 CLI 編輯。\n', encoding='utf-8')
    edited = import_directory(directory)['files'][target.relative_to(directory).as_posix()]
    assert edited.rstrip('\r\n').endswith('合成 CLI 編輯。')
    assert edited.encode('utf-8') == target.read_bytes()
    with pytest.raises(ValueError):
        export_directory(exported, directory)
    (directory / '.env').write_text('unexpected', encoding='utf-8')
    with pytest.raises(ValueError):
        import_directory(directory)


@pytest.mark.parametrize('url', ['http://example.com', 'https://user:password@example.com', 'https://example.com/path', 'file:///etc/passwd'])
def test_cli_rejects_unsafe_admin_origin(url):
    with pytest.raises(ValueError):
        Client(url)


@pytest.mark.parametrize('newline', ['\n', '\r\n'])
def test_cli_preserves_file_line_endings(tmp_path, newline):
    payload = {'draft_id': str(uuid.uuid4()), 'base_release_id': str(uuid.uuid4()), 'revision': 1,
        'schema_version': 'research-draft-v1', 'assets': {},
        'files': {'industry-map/research/research-test.md': newline.join(['## 測試', '', '內文', ''])}}
    directory = tmp_path / 'exchange'
    export_directory(payload, directory)
    assert import_directory(directory) == payload


@pytest.mark.parametrize('content', [b'<svg xmlns="http://www.w3.org/2000/svg"><script>bad()</script></svg>',
    b'<!DOCTYPE svg><svg xmlns="http://www.w3.org/2000/svg"/>',
    b'<svg xmlns="http://www.w3.org/2000/svg" onload="bad()"/>',
    b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://evil.example/pixel"/></svg>',
    b'<svg xmlns="http://www.w3.org/2000/svg"><rect fill="url(https://evil.example)"/></svg>'])
def test_malicious_asset_never_enters_store(tmp_path, content):
    with pytest.raises(ValueError):
        upload_asset(tmp_path / 'assets', 'industry-map/assets/test.svg', 'image/svg+xml', content)
    assert not (tmp_path / 'assets').exists()


def test_safe_asset_is_content_addressed_and_mime_checked(tmp_path):
    content = b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>'
    root = tmp_path / 'assets'
    result = upload_asset(root, 'industry-map/assets/test.svg', 'image/svg+xml', content)
    assert (root / result['sha256']).read_bytes() == content
    assert upload_asset(root, 'industry-map/assets/test.svg', 'image/svg+xml', content) == result
    with pytest.raises(ValueError):
        upload_asset(root, 'industry-map/assets/test.png', 'image/png', content)


def test_archive_rejects_symlink():
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        item = tarfile.TarInfo('industry-map/companies/company-test.md')
        item.type, item.linkname = tarfile.SYMTYPE, '../../.env'
        archive.addfile(item)
    with pytest.raises(ValueError):
        read_archive(stream.getvalue())


def test_symlink_store_and_managed_root_are_rejected(tmp_path):
    real = tmp_path / 'outside'
    real.mkdir()
    link = tmp_path / 'linked'
    try:
        link.symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip('Windows account lacks symlink privilege; Linux container test is required')
    with pytest.raises(ValueError):
        ManagedGit(link)
    with pytest.raises(ValueError):
        upload_asset(link, 'industry-map/assets/test.svg', 'image/svg+xml', b'<svg xmlns="http://www.w3.org/2000/svg"/>')
    assert not list(real.iterdir())
