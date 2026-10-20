import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.main import app
from app.db import get_session
from app.research_db import get_research_session
from app.research_compile import insert, document, normalize


@pytest.fixture
def v2():
    url = os.environ.get('RESEARCH_PG_TEST_URL')
    if not url:
        pytest.skip('research v2 contracts require isolated PostgreSQL')
    engine = create_engine(url, hide_parameters=True)
    if engine.url.database != 'industry_research_test':
        raise RuntimeError('Refusing v2 fixtures outside research test DB')
    connection = engine.connect()
    transaction = connection.begin()
    token = uuid.uuid4().hex
    published, ready, preparing = [uuid.uuid4() for _ in range(3)]
    keys = ['company-v2-' + token + '-' + str(i) for i in range(3)]
    for release, status in [(published, 'ready'), (ready, 'ready'), (preparing, 'preparing')]:
        insert(connection, 'research_releases', {'release_id': release, 'git_commit': uuid.uuid4().hex + '00000000',
            'schema_version': 'research-v1', 'content_hash': uuid.uuid4().hex * 2, 'status': status, 'reason': 'v2 isolated test'})
    for index, key in enumerate(keys):
        insert(connection, 'entities', {'entity_id': key, 'kind': 'company'})
        insert(connection, 'entity_snapshots', {'release_id': published if index < 2 else ready,
            'entity_id': key, 'kind': 'company', 'name': '測試公司' + str(index), 'summary': '合成契約資料',
            'markdown': '## 供應角色\n\n測試內容', 'data': {'gaps': ['未研究'], 'aliases': ['同名候選']},
            'semantic_hash': 'a' * 64})
        if index < 2:
            insert(connection, 'legacy_mappings', {'release_id': published, 'kind': 'company',
                'legacy_key': 'AMBIGUOUS', 'entity_id': key})
    insert(connection, 'legacy_mappings', {'release_id': published, 'kind': 'company', 'legacy_key': 'TEST', 'entity_id': keys[0]})
    role, product, concept = 'role-v2-' + token, 'product-v2-' + token, 'concept-v2-' + token
    for key, kind in [(role, 'role'), (product, 'product'), (concept, 'concept')]:
        content = {'related-ids':[keys[1],keys[2]],'comparisons':[{'left':product,'right':concept,
            'conditions':['合成比較條件'],'limitations':['合成比較限制']}]} if kind=='concept' else {}
        insert(connection, 'entities', {'entity_id': key, 'kind': kind})
        insert(connection, 'entity_snapshots', {'release_id': published, 'entity_id': key, 'kind': kind,
            'name': '合成分類', 'summary': '測試', 'markdown': '測試', 'data': content, 'semantic_hash': 'b' * 64})
    insert(connection, 'listings', {'release_id': published, 'listing_id': 'test', 'company_id': keys[0],
        'ticker': '1234.TW', 'market': 'TW', 'exchange': 'XTAI', 'share_class': 'test'})
    insert(connection, 'taxonomy_links', {'release_id': published, 'link_id': 'test-company', 'parent_id': role, 'child_id': keys[0]})
    insert(connection, 'taxonomy_links', {'release_id': published, 'link_id': 'test-product', 'parent_id': role, 'child_id': product})
    insert(connection, 'company_offerings', {'release_id': published, 'offering_id': 'test',
        'company_id': keys[0], 'product_id': product, 'role_id': role, 'conditions': ['測試']})
    structures = {
        'thermal': {'upstream': [], 'downstream': ['odm'], 'themes': ['liquid-cooling'], 'companies': []},
        'pcb': {'upstream': [], 'downstream': ['odm'], 'themes': [], 'companies': []},
        'power': {'upstream': [], 'downstream': ['odm'], 'themes': ['liquid-cooling'], 'companies': []},
        'odm': {'upstream': ['thermal', 'pcb', 'power'], 'downstream': ['thermal'], 'themes': [], 'companies': []}}
    for legacy_id, authored in structures.items():
        key = 'segment-' + legacy_id
        insert(connection, 'entities', {'entity_id': key, 'kind': 'segment'}, True)
        insert(connection, 'entity_snapshots', {'release_id': published, 'entity_id': key, 'kind': 'segment',
            'name': legacy_id, 'summary': '合成結構測試', 'markdown': '測試', 'data': {**authored,'layer':'ai-server','segment':legacy_id}, 'semantic_hash': 'c' * 64})
    insert(connection, 'entities', {'entity_id': 'theme-liquid-cooling', 'kind': 'theme'}, True)
    insert(connection, 'entity_snapshots', {'release_id': published, 'entity_id': 'theme-liquid-cooling', 'kind': 'theme',
        'name': '液冷結構測試', 'summary': '合成資料', 'markdown': '測試', 'data': {'segments': ['thermal', 'power']}, 'semantic_hash': 'd' * 64})
    for source, target, kind in [('thermal', 'odm', 'segment-supply'), ('odm', 'thermal', 'segment-feedback')]:
        insert(connection, 'relations', {'release_id': published, 'relation_id': source + '-to-' + target,
            'source_id': 'segment-' + source, 'target_id': 'segment-' + target, 'kind': kind, 'direction': 'directed',
            'mechanism': '合成結構測試', 'conditions': ['測試'], 'confidence': 'inference', 'data': {}})
    # Synthetic aliases exercise matching, not real company identity assertions.
    for key, aliases in [(keys[0], ['臺積電', '台積電', 'NVIDIA', 'AMD', '1234.TW', '同名候選']),
                          (keys[1], ['AMDOCS', '同名候選']), (product, ['冷板', 'cold plate']),
                          (concept, ['熱阻', 'thermal resistance']), (keys[2], ['未發布搜尋'])]:
        for alias in aliases:
            insert(connection, 'entity_aliases', {'release_id': ready if key == keys[2] else published,
                'entity_id': key, 'alias': alias, 'normalized': normalize(alias), 'alias_kind': 'alias'})
    cited = document(connection, published, 'document-' + token, 'one', '實際引用測試', 'https://example.org/one',
                     'informative', {'locator': 'section', 'excerpt': '合法短摘錄', 'parser-error': 'must not appear'})
    unreferenced = document(connection, published, 'document-unused-' + token, 'one', '未被引用版本',
                            'https://example.org/unused', 'informative', {}, cited=False)
    insert(connection, 'research_claims', {'release_id': published, 'entity_id': keys[0], 'claim_id': 'product',
        'statement': '僅為合成測試主張', 'confidence': 'inference', 'conditions': ['測試'], 'reviewed': '2026-10-16'})
    insert(connection, 'claim_evidence', {'release_id': published, 'entity_id': keys[0], 'claim_id': 'product',
        'ordinal': 0, 'revision_id': cited, 'locator': 'section', 'stance': 'supporting', 'applicable_period': '測試', 'data': {}})
    uncited = document(connection, ready, 'document-private-' + token, 'one', '未發布文件', 'https://example.org/private',
                       'informative', {'parser-error': 'must not appear'})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"), {'id': published})
    connection.execute(text('INSERT INTO research.release_head VALUES (true,:id,1,now()) ON CONFLICT(singleton) DO UPDATE SET release_id=excluded.release_id'), {'id': published})
    connection.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
    connection.execute(text('SET LOCAL ROLE research_reader'))
    session = Session(bind=connection, expire_on_commit=False, join_transaction_mode='create_savepoint')
    app.dependency_overrides[get_research_session] = lambda: session
    app.dependency_overrides[get_session] = lambda: session
    try:
        with TestClient(app) as client:
            yield client, {'release': str(published), 'ready': str(ready), 'preparing': str(preparing),
                           'keys': keys, 'doc': 'document-' + token, 'cited': cited,
                           'unused_doc': 'document-unused-' + token, 'unreferenced': unreferenced,
                           'role': role, 'product': product, 'concept': concept,
                           'private_doc': 'document-private-' + token, 'uncited': uncited, 'session': session}
    finally:
        app.dependency_overrides.clear()
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def test_manifest_pagination_pin_and_legacy_coexist(v2):
    client, data = v2
    manifest = client.get('/api/v2/manifest')
    assert manifest.status_code == 200 and manifest.json()['release_id'] == data['release']
    assert manifest.headers['Cache-Control'] == 'no-store'
    first = client.get('/api/v2/companies', params={'limit': 1, 'release_id': data['release']}).json()
    assert len(first['data']['items']) == 1 and first['data']['has_more']
    second = client.get('/api/v2/companies', params={'limit': 1, 'release_id': data['release'], 'cursor': first['data']['next_cursor']}).json()
    assert first['data']['items'][0]['id'] != second['data']['items'][0]['id']
    # Existing synthetic PG companies may exist; all cursor rows remain pinned.
    assert second['release_id'] == data['release']
    assert client.get('/api/health').json()['status'] == 'ok'


def test_unknown_and_unpublished_releases_are_not_reader_content(v2):
    client, data = v2
    for release in (data['ready'], data['preparing'], str(uuid.uuid4())):
        response = client.get('/api/v2/companies', params={'release_id': release})
        assert response.status_code == 404 and response.json()['code'] == 'release-not-found'
    response = client.get('/api/v2/companies/company-missing')
    assert response.status_code == 404
    assert {'code', 'message', 'request_id', 'retryable'} <= response.json().keys()
    assert response.headers['X-Request-ID'] == response.json()['request_id']
    assert client.get('/api/v2/companies', params={'limit': 101}).status_code == 422
    assert client.get('/api/v2/companies', params={'cursor': 'not-json'}).status_code == 422


def test_resolve_unknown_and_ambiguity(v2):
    client, data = v2
    assert client.get('/api/v2/resolve', params={'kind': 'company', 'key': 'TEST'}).json()['data']['id'] == data['keys'][0]
    assert client.get('/api/v2/resolve', params={'kind': 'company', 'key': 'missing'}).status_code == 404
    ambiguous = client.get('/api/v2/resolve', params={'kind': 'company', 'key': 'AMBIGUOUS'})
    assert ambiguous.status_code == 409 and len(ambiguous.json()['candidates']) == 2


def test_document_versions_are_fixed_and_do_not_expose_maintenance(v2):
    client, data = v2
    response = client.get('/api/v2/documents/' + data['doc'] + '/revisions/' + data['cited'])
    assert response.status_code == 200
    assert response.json()['data']['locators'][0]['excerpt'] == '合法短摘錄'
    assert 'parser-error' not in response.text and 'data' not in response.json()['data']
    assert client.get('/api/v2/documents/' + data['doc'] + '/revisions/latest').status_code == 404
    assert client.get('/api/v2/documents/' + data['doc'] + '/revisions/one').json()['data']['revision_id'] == data['cited']
    assert client.get('/api/v2/documents/' + data['private_doc'] + '/revisions/' + data['uncited']).status_code == 404
    assert client.get('/api/v2/documents/' + data['unused_doc'] + '/revisions/' + data['unreferenced']).status_code == 404
    claims = client.get('/api/v2/companies/' + data['keys'][0]).json()['data']['claims']
    assert claims[0]['evidence'][0]['revision_id'] == data['cited']


def test_authored_related_and_comparison_targets_resolve_only_in_same_release(v2):
    client,data=v2
    response=client.get('/api/v2/concepts/'+data['concept'],params={'release_id':data['release']})
    result=response.json()
    assert result['release_id']==data['release']
    related={row['id'] for row in result['data']['related']}
    assert related=={data['keys'][1],data['product']}
    assert data['keys'][2] not in related
    assert data['keys'][2] not in response.text
    assert result['data']['content']['comparisons'][0]['conditions']==['合成比較條件']


def test_detail_and_cursor_do_not_mix_filters(v2):
    client, data = v2
    item = client.get('/api/v2/companies/' + data['keys'][1]).json()['data']
    assert item['markdown'].startswith('## 供應角色') and item['claims'] == []
    assert 'raw' not in item and 'source-identifiers' not in item['content']
    first = client.get('/api/v2/companies', params={'limit': 1}).json()
    response = client.get('/api/v2/companies', params={'market': 'US', 'cursor': first['data']['next_cursor']})
    assert response.status_code == 409 and response.json()['code'] == 'cursor-conflict'


def test_catalog_and_market_role_category_filters(v2):
    client, data = v2
    catalog = client.get('/api/v2/catalog').json()['data']
    assert {data['role'], data['product'], 'segment-thermal', 'theme-liquid-cooling'} <= {r['id'] for r in catalog['items']}
    assert len(catalog['links']) == 2
    for filters in ({'market': 'TW'}, {'role': data['role']}, {'category': data['role']}, {'category':data['product']}):
        result = client.get('/api/v2/companies', params=filters).json()['data']['items']
        assert [r['id'] for r in result] == [data['keys'][0]]
    assert client.get('/api/v2/companies', params={'market': 'US'}).json()['data']['items'] == []


def test_legacy_map_return_is_release_scoped_and_absent_without_mapping(v2):
    client,data=v2
    segment=client.get('/api/v2/segments/segment-thermal',params={'release_id':data['release']}).json()['data']
    assert segment['legacy_return']=={'url':'/?layer=ai-server&segment=thermal','label':'回到「thermal」產業地圖'}
    assert client.get('/api/v2/products/'+data['product']).json()['data']['legacy_return'] is None
    assert client.get('/api/v2/segments/segment-thermal',params={'release_id':data['ready']}).status_code==404


def test_reading_trail_runs_from_map_segment_to_supply_chain(v2):
    client,data=v2
    # Published releases are immutable, so author a separate release with a full map → chain → product path.
    connection=data['session'].connection()
    connection.execute(text('RESET ROLE'))
    release,token=uuid.uuid4(),uuid.uuid4().hex
    insert(connection,'research_releases',{'release_id':release,'git_commit':uuid.uuid4().hex+'00000000','schema_version':'research-v1',
        'content_hash':uuid.uuid4().hex*2,'status':'ready','reason':'trail test'})
    application,role,product='application-trail-'+token,'role-trail-'+token,'product-trail-'+token
    for key,kind,name,content in [('segment-thermal','segment','散熱',{'layer':'ai-server','segment':'thermal'}),(application,'application','合成供應鏈',{}),
                                  (role,'role','合成角色',{}),(product,'product','合成產品',{}),(data['keys'][0],'company','合成公司',{})]:
        insert(connection,'entities',{'entity_id':key,'kind':kind},True)
        insert(connection,'entity_snapshots',{'release_id':release,'entity_id':key,'kind':kind,'name':name,'summary':'測試',
            'markdown':'測試','data':content,'semantic_hash':'e'*64})
    for parent,child in [('segment-thermal',application),(application,role),(role,product),(role,data['keys'][0])]:
        insert(connection,'taxonomy_links',{'release_id':release,'link_id':'trail-'+child,'parent_id':parent,'child_id':child})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':release})
    connection.execute(text('SET LOCAL ROLE research_reader'))
    pinned={'release_id':str(release)}
    assert client.get('/api/v2/products/'+product,params=pinned).json()['data']['trail']==[
        {'id':'segment-thermal','kind':'segment','name':'散熱','url':'/?layer=ai-server&segment=thermal'},
        {'id':application,'kind':'application','name':'合成供應鏈','url':None}]
    assert client.get('/api/v2/applications/'+application,params=pinned).json()['data']['trail']==[
        {'id':'segment-thermal','kind':'segment','name':'散熱','url':'/?layer=ai-server&segment=thermal'}]
    # A company can sit in several chains, so it gets no single trail.
    assert client.get('/api/v2/companies/'+data['keys'][0],params=pinned).json()['data']['trail']==[]


def test_database_failure_is_retryable_and_does_not_leak_details(v2):
    from sqlalchemy.exc import OperationalError
    client, _ = v2
    def unavailable():
        raise OperationalError('private SQL', {}, Exception('private connection detail'))
    app.dependency_overrides[get_research_session] = unavailable
    response = client.get('/api/v2/manifest')
    assert response.status_code == 503 and response.json()['retryable']
    assert response.headers['Retry-After'] == '5'
    assert 'private' not in response.text and response.json()['request_id']
