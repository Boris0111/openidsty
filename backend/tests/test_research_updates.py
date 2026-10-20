"""Favourite update summaries: per object, per dimension, read-only and bounded."""
import uuid
from sqlalchemy import text
from app.research_compile import insert
from test_research_dynamic import dynamic  # noqa: F401 - pytest fixture


def query(client, *targets, release=None):
    body = {'items': [dict(kind=kind, id=key, **({'seen': seen} if seen else {})) for kind, key, seen in targets]}
    if release:
        body['release_id'] = str(release)
    response = client.post('/api/v2/updates/query', json=body)
    assert response.status_code == 200, response.text
    assert response.headers['cache-control'] == 'no-store'
    return {item['id']: item for item in response.json()['data']['items']}


def seen(item):
    return {'research': item['research']['token'], 'values': item['values']['token'], 'events': item['events']['marker']}


def as_writer(connection):
    connection.execute(text('RESET ROLE'))


def as_reader(connection):
    connection.execute(text('SET LOCAL ROLE research_reader'))


def publish_copy(connection, base, change=lambda values: values, extra=(), relations=()):
    """Published releases are immutable, so each test release is assembled before publishing."""
    as_writer(connection)
    newer = uuid.uuid4()
    insert(connection, 'research_releases', {'release_id': newer, 'git_commit': uuid.uuid4().hex + '0' * 8,
        'schema_version': 'research-v1', 'content_hash': uuid.uuid4().hex * 2, 'status': 'preparing', 'reason': 'Synthetic release'})
    for row in connection.execute(text('SELECT * FROM research.entity_snapshots WHERE release_id=:id'), {'id': base}).mappings().all():
        values = {key: row[key] for key in ('entity_id', 'kind', 'name', 'summary', 'markdown', 'data', 'semantic_hash', 'reviewed')}
        insert(connection, 'entity_snapshots', {'release_id': newer, **change(values)})
    for entity_id, kind in extra:
        insert(connection, 'entities', {'entity_id': entity_id, 'kind': kind})
        insert(connection, 'entity_snapshots', {'release_id': newer, 'entity_id': entity_id, 'kind': kind, 'name': '合成' + kind,
            'summary': '僅測試', 'markdown': '測試', 'data': {}, 'semantic_hash': 'f' * 64})
    for relation in relations:
        insert(connection, 'relations', {'release_id': newer, **relation})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"), {'id': newer})
    connection.execute(text('UPDATE research.release_head SET release_id=:id,generation=generation+1'), {'id': newer})
    as_reader(connection)
    return newer


def test_research_values_and_events_change_separately_per_object(dynamic):
    client, keys, _, _, add, event, _ = dynamic
    first = query(client, ('company', keys[0], None), ('company', keys[1], None))
    assert first[keys[0]]['research']['changed'] is None and first[keys[0]]['events']['changed'] is None  # no baseline: pending
    baseline = {key: seen(item) for key, item in first.items()}
    add('120', index=0)
    event(index=1)
    event(index=1, known=False)
    after = query(client, *[('company', key, baseline[key]) for key in keys[:2]])
    assert (after[keys[0]]['values']['changed'], after[keys[0]]['research']['changed'], after[keys[0]]['events']['changed']) == (True, False, False)
    assert (after[keys[1]]['values']['changed'], after[keys[1]]['events']['changed']) == (False, True)
    assert (after[keys[1]]['events']['new_dated'], after[keys[1]]['events']['new_undated']) == (1, 1)
    # Marking only what was displayed: a later event stays unread.
    displayed = seen(after[keys[1]])
    event(index=1)
    later = query(client, ('company', keys[1], displayed))[keys[1]]
    assert later['events']['changed'] and later['events']['new_dated'] == 1 and later['events']['new_undated'] == 0


def test_new_release_only_updates_objects_whose_research_changed(dynamic):
    client, keys, release, _, _, _, connection = dynamic
    before = query(client, *[('company', key, None) for key in keys[:3]])
    marks = {key: seen(item) for key, item in before.items()}
    revised = lambda values: {**values, 'summary': '合成研究已修訂', 'semantic_hash': 'd' * 64} if values['entity_id'] == keys[1] else values
    publish_copy(connection, release, revised, relations=[{'relation_id': 'relation-synthetic-competition', 'source_id': keys[2],
        'target_id': keys[3], 'kind': 'competition', 'direction': 'symmetric', 'mechanism': '合成競爭關係',
        'conditions': ['僅測試'], 'confidence': 'inference', 'data': {}}])
    after = query(client, *[('company', key, marks[key]) for key in keys[:3]])
    assert [after[key]['research']['changed'] for key in keys[:3]] == [False, True, True]
    pinned = query(client, ('company', keys[1], marks[keys[1]]), release=release)
    assert pinned[keys[1]]['research']['changed'] is False  # The older displayed release still matches.


def test_retries_same_values_and_unpublished_drafts_do_not_create_unread(dynamic):
    client, keys, _, ready, add, _, connection = dynamic
    add('100', index=0)
    mark = seen(query(client, ('company', keys[0], None))[keys[0]])
    add('100', index=0)  # Same value re-filed: no new revision, so no new token.
    as_writer(connection)
    connection.execute(text("UPDATE public.sources SET status='failed',last_attempt=now(),error='synthetic retry' WHERE id LIKE 'dynamic-%'"))
    insert(connection, 'entity_snapshots', {'release_id': ready, 'entity_id': keys[0], 'kind': 'company', 'name': '未發布草稿',
        'summary': '草稿內容', 'markdown': '草稿', 'data': {}, 'semantic_hash': 'e' * 64})
    as_reader(connection)
    item = query(client, ('company', keys[0], mark))[keys[0]]
    assert (item['research']['changed'], item['values']['changed'], item['events']['changed']) == (False, False, False)
    response = client.post('/api/v2/updates/query', json={'release_id': str(ready), 'items': [{'kind': 'company', 'id': keys[0]}]})
    assert response.status_code == 404


def test_unknown_targets_are_itemised_and_requests_are_bounded(dynamic):
    client, keys, release, _, _, _, connection = dynamic
    theme = 'theme-updates-' + uuid.uuid4().hex[:8]
    publish_copy(connection, release, extra=[(theme, 'theme')])
    items = query(client, ('company', keys[0], None), ('company', 'company-missing-target', None),
                  ('product', keys[1], None), ('theme', theme, None))
    assert items[keys[0]]['available'] and not items['company-missing-target']['available']
    assert not items[keys[1]]['available']  # Kind must match; a company is not a product target.
    assert items[theme]['values']['applicable'] and items[theme]['values']['token']
    too_many = [{'kind': 'company', 'id': f'company-limit-{index}'} for index in range(101)]
    for body in ({'items': too_many}, {'items': [{'kind': 'concept', 'id': 'concept-x'}]},
                 {'items': [{'kind': 'company', 'id': keys[0]}] * 2},
                 {'items': [{'kind': 'company', 'id': keys[0], 'seen': {'events': -1}}]}):
        response = client.post('/api/v2/updates/query', json=body)
        assert response.status_code == 422 and response.json()['code'] == 'invalid-request'
