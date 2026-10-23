"""Snapshot export against isolated PostgreSQL: same responses as the API, repeatable bytes, nothing private."""
import json
import pytest
from sqlalchemy import text
from test_research_v2 import v2  # noqa: F401
from app.public_snapshot import export, leak_findings, SnapshotError, COLLECTIONS
from app.research_v2 import COLLECTIONS as KINDS


def files(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob('*') if path.is_file() and path.name != 'export.json'}


def read(root, relative):
    return json.loads((root / relative).read_text(encoding='utf-8'))


def test_export_matches_database_and_repeats_byte_for_byte(v2, tmp_path):
    client, data = v2
    session = data['session']
    first, manifest = export(tmp_path / 'a', session=session)
    second, _ = export(tmp_path / 'b', session=session)
    assert first.name == data['release'] and files(first) == files(second)
    assert leak_findings(first) == []
    counts = dict(session.execute(text('SELECT kind,count(*) FROM research.entity_snapshots WHERE release_id=:r GROUP BY kind'), {'r': data['release']}).all())
    assert {collection: manifest['counts'][collection] for collection in COLLECTIONS} == {collection: counts.get(KINDS[collection], 0) for collection in COLLECTIONS}
    assert manifest['counts']['aliases'] == session.scalar(text('SELECT count(*) FROM research.entity_aliases WHERE release_id=:r'), {'r': data['release']})
    # Stored responses are the API's own, and the role filter keeps only its members in directory order.
    company = data['keys'][0]
    api = client.get(f'/api/v2/companies/{company}', params={'release_id': data['release']}).json()
    assert read(first, f'v2/companies/{company}.json') == api
    directory = read(first, 'v2/directory/companies.json')
    assert [row['id'] for row in directory['items']] == data['keys'][:2] and directory['filters']['role'][data['role']] == [company]
    assert directory['filters']['market']['TW'] == [company] and directory['filters']['market']['US'] == []
    resolve = read(first, 'v2/resolve.json')['keys']
    assert resolve['TEST']['status'] == 200 and resolve['TEST']['body']['data']['id'] == company
    assert resolve['AMBIGUOUS']['status'] == 409 and resolve['1234.TW']['body']['data']['id'] == company
    pair = client.get('/api/v2/compare', params={'company_ids': ','.join(data['keys'][:2]), 'release_id': data['release']}).json()['data']['companies']
    assert [read(first, f'v2/compare/{key}.json')['data'] for key in data['keys'][:2]] == pair
    search = read(first, 'v2/search.json')
    assert ['台積電', '台積電', company] in search['aliases'] and data['keys'][2] not in {row['id'] for row in search['entities']}
    assert (first / f'v2/documents/{data["doc"]}/{data["cited"]}.json').exists()
    assert not (first / f'v2/documents/{data["private_doc"]}').exists()


def test_export_refuses_a_release_that_is_not_published_now(v2, tmp_path):
    _, data = v2
    with pytest.raises(SnapshotError):
        export(tmp_path, release_id=data['ready'], session=data['session'])
    assert not any(tmp_path.iterdir())
