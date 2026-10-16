"""Private bounded maintenance views; no anonymous diagnostics."""
from test_research_auth import owner, login


def test_private_maintenance_views_are_bounded_paginated_and_no_store(owner):
    client, _ = owner
    paths = ['/api/admin/releases', '/api/admin/sources', '/api/admin/audit']
    for path in paths:
        assert client.get(path).status_code == 401
    assert login(client).status_code == 200
    for path in paths:
        response = client.get(path, params={'limit':1})
        assert response.status_code == 200, response.text
        assert response.headers['cache-control'] == 'no-store'
        data = response.json()
        assert len(data['items']) <= 1
        if data['has_more']:
            next_page = client.get(path, params={'limit':1,'cursor':data['next_cursor']}).json()
            assert next_page['items'] != data['items']
        assert client.get(path, params={'limit':101}).status_code == 422
