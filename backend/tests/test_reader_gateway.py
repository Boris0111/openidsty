import httpx
from fastapi.testclient import TestClient
from app.reader_gateway import app


def test_reader_rejects_admin_legacy_host_spoof_and_mutations():
    with TestClient(app, base_url='http://localhost:3015') as client:
        for path in ['/admin','/api/admin/session','/api/admin/drafts','/sources','/api/sources','/api/docs','/api/openapi.json','/api/v2/%2e%2e/admin/session','/api/v2/%252e%252e/admin/session']:
            assert client.get(path).status_code==403
        assert client.get('/next', headers={'Host':'evil.example'}).status_code==403
        for method in ['POST','PATCH','DELETE','PUT']:
            assert client.request(method,'/next').status_code==403
            assert client.request(method,'/api/v2/companies').status_code==403


def test_reader_uses_fixed_upstream_strips_credentials_and_preserves_release():
    observed=[]
    async def upstream(request):
        observed.append(request)
        return httpx.Response(200, json={'release_id':'synthetic-published','data':{}},
            headers={'ETag':'"one"','Set-Cookie':'must-not-escape=1','Cache-Control':'public,max-age=60'})
    with TestClient(app, base_url='http://localhost:3015') as client:
        original=app.state.client
        app.state.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        try:
            response=client.get('/api/v2/companies?release_id=synthetic-published',
                headers={'Cookie':'industryflow_owner=secret','Authorization':'Bearer secret','X-CSRF-Token':'secret','X-Forwarded-Host':'evil.example'})
            assert response.status_code==200 and response.headers['etag']=='"one"'
            assert 'set-cookie' not in response.headers
            assert str(observed[0].url)=='http://web:3010/api/v2/companies?release_id=synthetic-published'
            for name in ['cookie','authorization','x-csrf-token','x-forwarded-host']:
                assert name not in observed[0].headers
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
