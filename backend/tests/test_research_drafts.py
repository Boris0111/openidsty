"""Draft integration uses the disposable PG database and real authored research."""
import json
import subprocess
import uuid
import pytest
from sqlalchemy import text
from app.research_compile import project
from app.research_documents import materialize, validate_payload
from app.research_git import ManagedGit
from test_research_auth import owner, login, ORIGIN
from test_research_documents import authored


@pytest.fixture
def draft_context(owner, authored, tmp_path, monkeypatch):
    client, engine = owner
    payload, assets = authored
    source = tmp_path / 'source'
    source.mkdir()
    for name, content in materialize(payload, assets).items():
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(source), '-c', 'core.autocrlf=false',
            '-c', 'user.name=Test', '-c', 'user.email=test@localhost', *args])
    git('init'); git('add', '.'); git('commit', '-m', 'Synthetic test baseline')
    head = git('rev-parse', 'HEAD').decode().strip()
    bundle = tmp_path / 'source.bundle'
    git('bundle', 'create', str(bundle), 'HEAD')
    managed = ManagedGit(tmp_path / 'managed')
    managed.seed(bundle.read_bytes(), head)
    monkeypatch.setenv('RESEARCH_GIT_ROOT', str(managed.root))
    monkeypatch.setenv('RESEARCH_ASSET_ROOT', str(assets))
    valid, content = validate_payload(payload, assets)
    assert valid['valid']
    with engine.begin() as connection:
        projected = project(connection, content, head, reason='Synthetic draft integration baseline')
        release = projected['release_id']
        connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id AND status<>'published'"), {'id': release})
    response = login(client)
    assert response.status_code == 200
    headers = {'Origin': ORIGIN, 'X-CSRF-Token': response.json()['csrf_token']}
    yield client, engine, release, headers


def test_form_file_revision_preview_and_reader_isolation(draft_context):
    client, engine, release, headers = draft_context
    response = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers)
    assert response.status_code == 201, response.text
    draft = response.json(); url = '/api/admin/drafts/' + draft['draft_id']
    path = 'industry-map/companies/company-auras.md'
    parts = client.get(url + '/document', params={'path': path}).json()
    fields = parts['frontmatter']; fields['summary'] = '僅維護者可見的合成測試摘要。'
    patch = {'changes': [{'path': path, 'frontmatter': fields, 'markdown': parts['markdown']}]}
    saved = client.patch(url, json=patch, headers={**headers, 'If-Match': '"1"'})
    assert saved.status_code == 200, saved.text
    assert saved.json()['revision'] == 2 and saved.headers['etag'] == '"2"'
    stale = client.patch(url, json=patch, headers={**headers, 'If-Match': '"1"'})
    assert stale.status_code == 409
    exported = client.get(url + '/export').json()
    imported = client.post(url + '/import', json=exported, headers={**headers, 'If-Match': '"2"'})
    assert imported.status_code == 200 and imported.json()['revision'] == 2
    validation = client.post(url + '/validate', headers=headers).json()
    assert validation['valid'], validation
    assert path in [change['path'] for change in client.get(url + '/diff').json()['changes']]
    with engine.connect() as connection:
        before = connection.execute(text('SELECT count(*) FROM research.research_releases')).scalar_one()
        public_summary = connection.execute(text('SELECT summary FROM research.entity_snapshots WHERE release_id=:release AND entity_id=\'company-auras\''), {'release': release}).scalar_one()
    preview = client.get(url + '/preview', params={'entity_id': 'company-auras'})
    assert preview.status_code == 200, preview.text
    assert preview.json()['data']['summary'] == fields['summary'] != public_summary
    assert preview.json()['draft']['content_hash'] == validation['content_hash']
    with engine.connect() as connection:
        assert connection.execute(text('SELECT count(*) FROM research.research_releases')).scalar_one() == before
        assert connection.execute(text('SELECT summary FROM research.entity_snapshots WHERE release_id=:release AND entity_id=\'company-auras\''), {'release': release}).scalar_one() == public_summary
    client.cookies.clear()
    for endpoint in [url, url+'/export', url+'/preview?entity_id=company-auras']:
        assert client.get(endpoint).status_code == 401


def test_invalid_document_and_read_only_schema_cannot_overwrite_draft(draft_context):
    client, _, release, headers = draft_context
    draft = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers).json()
    url = '/api/admin/drafts/' + draft['draft_id']
    for path, content in [('industry-map/README.md', 'replace schema'),
                          ('../.env', 'secret'),
                          ('industry-map/companies/company-auras.md', '<script>bad()</script>')]:
        response = client.patch(url, json={'changes': [{'path': path, 'content': content}]}, headers={**headers, 'If-Match': '"1"'})
        assert response.status_code == 422
    assert client.get(url).json()['revision'] == 1


def test_saves_and_imports_recheck_only_edited_files(draft_context, monkeypatch):
    import app.research_documents as documents
    client, _, release, headers = draft_context
    draft = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers).json()
    url = '/api/admin/drafts/' + draft['draft_id']
    path = 'industry-map/companies/company-auras.md'
    original = client.get(url + '/export').json()['files'][path]
    checked, check = [], documents.check_document
    monkeypatch.setattr(documents, 'check_document', lambda name, content: (checked.append(name), check(name, content))[1])

    saved = client.patch(url, json={'changes': [{'path': path, 'content': original + '\n增量儲存測試。\n'}]},
                         headers={**headers, 'If-Match': '"1"'})
    assert saved.status_code == 200 and saved.json()['revision'] == 2 and checked == [path]
    checked.clear()
    same = client.patch(url, json={'changes': [{'path': path, 'content': original + '\n增量儲存測試。\n'}]},
                        headers={**headers, 'If-Match': '"2"'})
    assert same.status_code == 200 and same.json()['revision'] == 2  # Identical content invents no revision.
    stale = client.patch(url, json={'changes': [{'path': path, 'content': original}]}, headers={**headers, 'If-Match': '"1"'})
    assert stale.status_code == 409

    checked.clear()
    rejected = client.patch(url, json={'changes': [{'path': path, 'content': original + '\n<div>raw</div>\n'}]},
                            headers={**headers, 'If-Match': '"2"'})
    assert rejected.status_code == 422 and path in rejected.json()['message'] and checked == [path]
    assert client.get(url).json()['revision'] == 2

    checked.clear()
    exported = client.get(url + '/export').json()
    exported['files'][path] = original + '\n匯入也只檢查變動檔案。\n'
    imported = client.post(url + '/import', json=exported, headers={**headers, 'If-Match': '"2"'})
    assert imported.status_code == 200 and imported.json()['revision'] == 3 and checked == [path]


def test_summary_and_save_response_carry_no_unrelated_content(draft_context):
    client, _, release, headers = draft_context
    draft = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers).json()
    url = '/api/admin/drafts/' + draft['draft_id']
    exported = client.get(url + '/export').json()
    summary = client.get(url + '/summary')
    assert summary.status_code == 200 and summary.headers['etag'] == '"1"'
    assert summary.json() == {'draft_id': draft['draft_id'], 'base_release_id': release, 'revision': 1,
                              'schema_version': exported['schema_version'], 'paths': sorted(exported['files']),
                              'assets': exported['assets']}
    assert 'files' not in summary.json() and len(summary.content) < len(client.get(url).content) / 10

    path = 'industry-map/companies/company-auras.md'
    parts = client.get(url + '/document', params={'path': path}).json()
    parts['frontmatter']['summary'] = '摘要回應測試。'
    saved = client.patch(url, json={'changes': [{'path': path, 'frontmatter': parts['frontmatter'], 'markdown': parts['markdown']}]},
                         headers={**headers, 'If-Match': '"1"'})
    body = saved.json()
    assert saved.status_code == 200 and saved.headers['etag'] == '"2"' and body['revision'] == 2 and 'files' not in body
    assert set(body['documents']) == {path} and body['paths'] == summary.json()['paths']
    document = body['documents'][path]
    assert document['frontmatter']['summary'] == '摘要回應測試。' and document['markdown'] == parts['markdown']
    assert document == client.get(url + '/document', params={'path': path}).json()
    removed = client.patch(url, json={'changes': [{'path': path, 'delete': True}]}, headers={**headers, 'If-Match': '"2"'})
    assert removed.json()['documents'] == {} and path not in removed.json()['paths']

    assert client.patch(url, json={'changes': []}, headers={'Origin': headers['Origin'], 'If-Match': '"3"'}).status_code == 403
    client.cookies.clear()
    assert client.get(url + '/summary').status_code == 401


@pytest.fixture
def compiles(monkeypatch):
    """Count full draft validations that actually ran (cache misses), starting from empty caches."""
    import app.research_drafts as drafts
    drafts.VALIDATIONS.clear(); drafts.BASE_EXPORTS.clear()
    calls, original = [], drafts.validate_payload
    monkeypatch.setattr(drafts, 'validate_payload', lambda payload, root: (calls.append(1), original(payload, root))[1])
    yield calls
    drafts.VALIDATIONS.clear(); drafts.BASE_EXPORTS.clear()


def test_validation_preview_and_diagrams_share_one_compile(draft_context, compiles):
    client, _, release, headers = draft_context
    draft = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers).json()
    url = '/api/admin/drafts/' + draft['draft_id']
    validation = client.post(url + '/validate?revision=1', headers=headers).json()
    assert validation['valid'] and len(compiles) == 1
    again = client.post(url + '/validate?revision=1', headers=headers).json()
    assert again == validation and len(compiles) == 1
    first = client.get(url + '/preview', params={'entity_id': 'concept-hbm-stack', 'revision': 1})
    second = client.get(url + '/preview', params={'entity_id': 'concept-hbm-stack', 'revision': 1})
    assert first.status_code == 200 and first.json() == second.json()  # The shared bundle is not mutated.
    other = client.get(url + '/preview', params={'entity_id': 'concept-liquid-cooling-loop', 'revision': 1}).json()
    diagrams = [asset['url'] for asset in first.json()['data']['assets']] + [other['data']['assets'][0]['url']]
    assert len(diagrams) == 3
    for diagram in diagrams:
        response = client.get(diagram.removeprefix('http://localhost:3010'))
        assert response.status_code == 200 and response.headers['content-type'].startswith('image/')
    assert len(compiles) == 1

    path = 'industry-map/companies/company-auras.md'
    content = client.get(url + '/export').json()['files'][path]
    saved = client.patch(url, json={'changes': [{'path': path, 'content': content + '\n新修訂。\n'}]}, headers={**headers, 'If-Match': '"1"'})
    assert saved.status_code == 200
    assert client.post(url + '/validate?revision=2', headers=headers).json()['valid'] and len(compiles) == 2


def test_invalid_revision_diagrams_are_refused_without_recompiling(draft_context, compiles):
    client, _, release, headers = draft_context
    draft = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers).json()
    url = '/api/admin/drafts/' + draft['draft_id']
    exported = client.get(url + '/export').json()
    sha = next(iter(exported['assets'].values()))
    # Removing a company that other research cites passes the per-file checks but fails the full compile.
    broken = client.patch(url, json={'changes': [{'path': 'industry-map/companies/company-auras.md', 'delete': True}]},
                          headers={**headers, 'If-Match': '"1"'})
    assert broken.status_code == 200 and broken.json()['revision'] == 2
    assert client.post(url + '/validate?revision=2', headers=headers).json()['valid'] is False and len(compiles) == 1
    for _ in range(2):
        assert client.get(f'{url}/assets/{sha}?revision=2').status_code == 422
    assert len(compiles) == 1


def test_owner_asset_upload_is_private_and_rejects_active_svg(owner, tmp_path, monkeypatch):
    client, _ = owner
    monkeypatch.setenv('RESEARCH_ASSET_ROOT', str(tmp_path / 'assets'))
    endpoint = '/api/admin/drafts/asset-upload?path=industry-map/assets/test.svg'
    content = b'<svg xmlns="http://www.w3.org/2000/svg"/>'
    assert client.post(endpoint, content=content, headers={'Origin': ORIGIN, 'Content-Type': 'image/svg+xml'}).status_code == 401
    token = login(client).json()['csrf_token']
    headers = {'Origin': ORIGIN, 'X-CSRF-Token': token, 'Content-Type': 'image/svg+xml'}
    malicious = b'<svg xmlns="http://www.w3.org/2000/svg" onload="bad()"/>'
    assert client.post(endpoint, content=malicious, headers=headers).status_code == 422
    assert not (tmp_path / 'assets').exists()
    result = client.post(endpoint, content=content, headers=headers)
    assert result.status_code == 200
    assert (tmp_path / 'assets' / result.json()['sha256']).read_bytes() == content
    assert client.post(endpoint.replace('test.svg', '../../.env'), content=content, headers=headers).status_code == 422
