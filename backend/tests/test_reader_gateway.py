import httpx
from fastapi.testclient import TestClient
from app.reader_gateway import app


def test_reader_rejects_admin_legacy_host_spoof_and_mutations():
    with TestClient(app, base_url='http://localhost:3015') as client:
        for path in ['/admin','/api/admin/session','/api/admin/drafts','/sources','/api/sources','/coverage','/api/coverage',
                     '/api/search?q=x','/api/theme-updates?ids=liquid-cooling','/api/companies/2330.TW','/api/compare','/watchlist','/compare',
                     '/api/docs','/api/openapi.json','/api/v2/%2e%2e/admin/session','/api/v2/%252e%252e/admin/session',
                     '/themes/liquid-cooling/extra','/companies/3324.TW/extra','/api/themes/../admin']:
            assert client.get(path).status_code==403, path
        assert client.get('/next', headers={'Host':'evil.example'}).status_code==403
        for method in ['POST','PATCH','DELETE','PUT']:
            assert client.request(method,'/next').status_code==403
            assert client.request(method,'/api/v2/companies').status_code==403
            assert client.request(method,'/api/themes').status_code==403


def test_map_themes_and_events_share_the_reader_entry():
    observed=[]
    async def upstream(request):
        observed.append(str(request.url))
        return httpx.Response(200, text='ok', headers={'Cache-Control':'no-store'})
    with TestClient(app, base_url='http://localhost:3015') as client:
        original=app.state.client
        app.state.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        try:
            for path in ['/','/?layer=ai-server&segment=thermal','/themes','/themes/liquid-cooling','/events','/events/12','/companies/3324.TW',
                         '/api/industries/ai-server/graph','/api/segments/thermal','/api/themes/liquid-cooling/assessment/versions?limit=20&offset=0',
                         '/api/themes/liquid-cooling/indicators','/api/events?limit=30','/api/technical-documents/ocp-cold-plate?limit=10&offset=0']:
                assert client.get(path,follow_redirects=False).status_code==200, path
            assert observed[1]=='http://web:3010/?layer=ai-server&segment=thermal'
        finally:
            import asyncio
            asyncio.run(app.state.client.aclose())
            app.state.client=original


def test_reader_uses_fixed_upstream_strips_credentials_and_preserves_release():
    observed=[]
    async def upstream(request):
        observed.append(request)
        return httpx.Response(200, json={'release_id':'synthetic-published','data':{}},
            headers={'ETag':'"one"','Age':'7','Set-Cookie':'must-not-escape=1','Cache-Control':'public,max-age=60'})
    with TestClient(app, base_url='http://localhost:3015') as client:
        original=app.state.client
        app.state.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        try:
            response=client.get('/api/v2/companies?release_id=synthetic-published',
                headers={'If-None-Match':'"one"','Cookie':'industryflow_owner=secret','Authorization':'Bearer secret','X-CSRF-Token':'secret','X-Forwarded-Host':'evil.example'})
            assert response.status_code==200 and response.headers['etag']=='"one"'
            assert response.headers['age']=='7'
            assert 'set-cookie' not in response.headers
            assert str(observed[0].url)=='http://web:3010/api/v2/companies?release_id=synthetic-published'
            assert observed[0].headers['if-none-match']=='"one"'
            for name in ['cookie','authorization','x-csrf-token','x-forwarded-host']:
                assert name not in observed[0].headers
        finally:
            import asyncio
            asyncio.run(app.state.client.aclose())
            app.state.client=original


def test_only_the_favourites_update_query_may_post():
    observed=[]
    async def upstream(request):
        observed.append(request)
        return httpx.Response(200, json={'data':{'items':[]}}, headers={'Cache-Control':'no-store'})
    with TestClient(app, base_url='http://localhost:3015') as client:
        original=app.state.client
        app.state.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        try:
            for path in ['/api/v2/updates','/api/v2/updates/query/extra','/api/v2/companies']:
                assert client.post(path,json={'items':[]}).status_code==403
            response=client.post('/api/v2/updates/query',json={'items':[]},headers={'Cookie':'industryflow_owner=secret'})
            assert response.status_code==200 and str(observed[-1].url)=='http://web:3010/api/v2/updates/query'
            assert 'cookie' not in observed[-1].headers
            assert client.post('/api/v2/updates/query',content=b'{"items":[]}'+b' '*(1024*1024)).status_code==413
        finally:
            import asyncio
            asyncio.run(app.state.client.aclose())
            app.state.client=original


def test_reader_upstream_outage_is_retryable_and_not_cached():
    async def offline(request):
        raise httpx.ConnectError('Synthetic outage')
    with TestClient(app, base_url='http://localhost:3015') as client:
        original=app.state.client
        app.state.client=httpx.AsyncClient(transport=httpx.MockTransport(offline))
        try:
            response=client.get('/next')
            assert response.status_code==503 and response.json()['retryable']
            assert response.headers['cache-control']=='no-store'
        finally:
            import asyncio
            asyncio.run(app.state.client.aclose())
            app.state.client=original
