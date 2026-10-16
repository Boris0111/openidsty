from test_research_v2 import v2


def test_chinese_alias_prefix_ticker_and_product(v2):
    client, data = v2
    for q in ('臺積電', '台積電', '台積', '1234.TW', 'NVIDIA'):
        response = client.get('/api/v2/search', params={'q': q})
        assert response.status_code == 200
        assert [item['id'] for item in response.json()['data']['items']] == [data['keys'][0]]
    product = client.get('/api/v2/search', params={'q': '冷板'}).json()['data']['items']
    assert product[0]['id'] == data['product'] and product[0]['kind'] == 'product'
    assert client.get('/api/v2/search', params={'q': '熱阻'}).json()['data']['items'][0]['kind'] == 'concept'


def test_english_token_boundary_and_unpublished_exclusion(v2):
    client, data = v2
    assert [r['id'] for r in client.get('/api/v2/search', params={'q': 'AMD'}).json()['data']['items']] == [data['keys'][0]]
    assert [r['id'] for r in client.get('/api/v2/search', params={'q': 'AMDOCS'}).json()['data']['items']] == [data['keys'][1]]
    assert client.get('/api/v2/search', params={'q': '未發布搜尋'}).json()['data']['items'] == []
    assert client.get('/api/v2/search', params={'q': '%'}).json()['data']['items'] == []


def test_same_alias_keeps_distinct_legal_candidates_and_cursor(v2):
    client, data = v2
    first = client.get('/api/v2/search', params={'q': '同名候選', 'limit': 1}).json()['data']
    second = client.get('/api/v2/search', params={'q': '同名候選', 'limit': 1, 'cursor': first['next_cursor']}).json()['data']
    assert {first['items'][0]['id'], second['items'][0]['id']} == set(data['keys'][:2])
    assert client.get('/api/v2/search', params={'q': 'AMD', 'cursor': first['next_cursor']}).status_code == 409
    assert client.get('/api/v2/search', params={'q': ' '}).status_code == 422
    assert client.get('/api/v2/search', params={'q': 'a' * 101}).status_code == 422
