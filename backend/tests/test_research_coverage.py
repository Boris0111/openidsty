"""Owner coverage keeps event categories, review candidates and gap statuses apart in bounded SQL."""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import text, select, event as sqlalchemy_event
from sqlalchemy.orm import Session
from app.main import app
from app.research_db import get_admin_connection
from app.research_compile import insert
from app.research_v2 import reader_gaps
from app.import_map import import_map
from app.models import Source, Event, EventSegment, EventTheme, TechnicalDocument
from app.technical_documents import observation
from test_research_auth import owner, login  # noqa: F401 - pytest fixture


def test_reader_gaps_keep_reason_and_hide_status():
    assert reader_gaps(['研究限制', {'status': 'not-public', 'reason': '公司未揭露產品別營收'}]) == ['研究限制', '公司未揭露產品別營收']
    assert reader_gaps(None) == []


@pytest.fixture
def seeded(owner):
    client, engine = owner
    assert login(client).status_code == 200
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False, join_transaction_mode='create_savepoint')
    import_map(session)  # Real map structure, only inside this rolled-back transaction.
    tag = uuid.uuid4().hex[:12]
    session.add(Source(id='coverage-' + tag, name='覆蓋測試來源', url='https://example.org/coverage', status='success', data={}))
    session.flush()
    statements = []
    sqlalchemy_event.listen(connection, 'before_cursor_execute', lambda *args: statements.append(args[2]))
    app.dependency_overrides[get_admin_connection] = lambda: connection
    try:
        yield client, connection, session, statements, tag
    finally:
        session.close()
        transaction.rollback()
        connection.close()


def add_event(session, tag, key, published, segment=None, relevance='direct', theme=None, mentioned=()):
    row = Event(source_id='coverage-' + tag, external_id=key + '-' + tag, title='合成覆蓋事件 ' + key, body='僅供計數測試',
                kind='news', url='https://example.org/' + key, raw={}, published_at=published,
                published_precision='day' if published else 'unknown', mentioned=list(mentioned))
    session.add(row)
    session.flush()
    if segment:
        session.add(EventSegment(event_id=row.id, segment_id=segment, relevance=relevance, evidence=[]))
    if theme:
        session.add(EventTheme(event_id=row.id, theme_id=theme, relevance=relevance, evidence=[]))
    session.flush()
    return row


def scope(client, kind, key):
    response = client.get('/api/admin/coverage')
    assert response.status_code == 200, response.text
    assert response.headers['cache-control'] == 'no-store'
    return next(row for row in response.json()['rows'] if row['kind'] == kind and row['id'] == key)


def test_coverage_requires_owner(owner):
    client, _ = owner
    for path in ('/api/admin/coverage', '/api/admin/coverage/entities'):
        assert client.get(path).status_code == 401


def test_direct_background_mentions_and_unknown_dates_count_separately(seeded):
    client, _, session, _, tag = seeded
    before = scope(client, 'segment', 'thermal')
    now = datetime.now(timezone.utc)
    add_event(session, tag, 'direct-recent', now - timedelta(days=10), 'thermal')
    add_event(session, tag, 'direct-older', now - timedelta(days=60), 'thermal')
    add_event(session, tag, 'background', now - timedelta(days=5), 'thermal', 'background')
    add_event(session, tag, 'undated', None, 'thermal')
    add_event(session, tag, 'mention-only', now - timedelta(days=3), mentioned=['3017.TW'])
    after = scope(client, 'segment', 'thermal')
    delta = {key: after[key] - before[key] for key in
             ('direct_30d', 'direct_90d', 'background_90d', 'unknown_date', 'company_mentions_90d')}
    assert delta == {'direct_30d': 1, 'direct_90d': 2, 'background_90d': 1, 'unknown_date': 1, 'company_mentions_90d': 1}
    assert 'samples' not in after


def test_statistics_stay_in_sql_and_candidates_are_bounded(seeded):
    client, _, session, statements, tag = seeded
    theme = scope(client, 'theme', 'liquid-cooling')
    baseline = datetime.fromisoformat(theme['assessment_candidates']['baseline']).replace(tzinfo=timezone.utc)
    statements.clear()
    scope(client, 'theme', 'liquid-cooling')
    first = len(statements)
    now = datetime.now(timezone.utc)
    for index in range(30):
        add_event(session, tag, f'bulk-{index}', now - timedelta(days=2), 'thermal', theme='liquid-cooling')
    add_event(session, tag, 'theme-undated', None, theme='liquid-cooling')
    statements.clear()
    after = scope(client, 'theme', 'liquid-cooling')
    assert len(statements) == first  # More events do not add per-event queries.
    candidates = after['assessment_candidates']
    expected = 30 if now - timedelta(days=2) > baseline + timedelta(days=1) else 0
    assert candidates['dated_count'] - theme['assessment_candidates']['dated_count'] == expected
    assert candidates['undated_count'] - theme['assessment_candidates']['undated_count'] == 1
    assert candidates['status'] == 'awaiting-assessment' and len(candidates['samples']) <= 5


def test_technical_baselines_citations_and_pending_candidates(seeded):
    client, _, session, _, _ = seeded
    data = client.get('/api/admin/coverage').json()
    row = next(r for r in data['rows'] if r['technical_documents'])
    document = row['technical_documents'][0]
    assert document['adopted'] and all(version['reviewed'] and version['locators'] for version in document['adopted'])
    before = document['review_counts'].get('pending', 0)
    observation(session, document['id'], 'coverage-test-version', 'f' * 64, 'coverage-test', 'https://example.org/new', {})
    session.flush()
    after = next(d for r in client.get('/api/admin/coverage').json()['rows'] if r['id'] == row['id']
                 for d in r['technical_documents'] if d['id'] == document['id'])
    assert after['review_counts']['pending'] == before + 1
    assert after['candidates'][0]['official_version'] == 'coverage-test-version' and after['candidates'][0]['status'] == 'pending'
    assert len(after['candidates']) <= 5
    cited = [r for r in data['rows'] for d in r['technical_documents'] if d['citations']]
    assert all(c['claim_id'] and c['version_id'] for r in cited for d in r['technical_documents'] for c in d['citations'])


def test_entity_gap_statuses_are_counted_in_sql_and_paginated(seeded):
    client, connection, _, _, tag = seeded
    release = uuid.uuid4()
    insert(connection, 'research_releases', {'release_id': release, 'git_commit': uuid.uuid4().hex + '00000000',
        'schema_version': 'research-v1', 'content_hash': uuid.uuid4().hex * 2, 'status': 'ready', 'reason': 'coverage test'})
    entities = {
        'company-cov-basic-' + tag: ('company', {'research-depth': 'basic', 'gaps': ['尚未完成獨立深研。']}),
        'company-cov-deep-' + tag: ('company', {'research-depth': 'deep', 'gaps': [
            {'status': 'not-public', 'reason': '未揭露產品別營收'}, {'status': 'not-obtained', 'reason': '歷史年報入口 403'}]}),
        'product-cov-' + tag: ('product', {'gaps': [{'status': 'not-applicable', 'reason': '分類頁不承載公司財務'}, '額定能力不等於場址驗收']}),
    }
    for key, (kind, data) in entities.items():
        insert(connection, 'entities', {'entity_id': key, 'kind': kind})
        insert(connection, 'entity_snapshots', {'release_id': release, 'entity_id': key, 'kind': kind, 'name': '覆蓋測試',
            'summary': '合成資料', 'markdown': '測試', 'data': data, 'semantic_hash': 'e' * 64})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"), {'id': release})
    connection.execute(text('INSERT INTO research.release_head VALUES (true,:id,1,now()) ON CONFLICT(singleton) DO UPDATE SET release_id=excluded.release_id'), {'id': release})
    connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))

    page = client.get('/api/admin/coverage/entities').json()
    assert page['release_id'] == str(release)
    rows = {item['entity_id']: item for item in page['items']}
    basic, deep, product = (rows['company-cov-basic-' + tag], rows['company-cov-deep-' + tag], rows['product-cov-' + tag])
    assert (basic['not_researched'], basic['unclassified'], basic['implied_not_researched']) == (1, 1, True)
    assert (deep['not_researched'], deep['not_public'], deep['not_obtained']) == (0, 1, 1)
    assert (product['not_applicable'], product['unclassified']) == (1, 1)
    assert deep['gaps'][0] == {'status': 'not-public', 'reason': '未揭露產品別營收'}
    assert product['gaps'][1] == {'status': None, 'reason': '額定能力不等於場址驗收'}
    totals = {row['kind']: row for row in page['totals']}
    assert (totals['company']['entities'], totals['company']['basic_companies'], totals['company']['not_researched']) == (2, 1, 1)

    filtered = client.get('/api/admin/coverage/entities', params={'status': 'not-public'}).json()['items']
    assert [item['entity_id'] for item in filtered] == ['company-cov-deep-' + tag]
    first = client.get('/api/admin/coverage/entities', params={'limit': 1}).json()
    second = client.get('/api/admin/coverage/entities', params={'limit': 1, 'cursor': first['next_cursor']}).json()
    assert first['has_more'] and second['items'][0]['entity_id'] != first['items'][0]['entity_id']
    for params in ({'status': 'unknown'}, {'kind': 'segment'}, {'cursor': 'bad cursor'}, {'limit': 101}):
        assert client.get('/api/admin/coverage/entities', params=params).status_code == 422
