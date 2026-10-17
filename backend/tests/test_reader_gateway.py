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


def test_map_return_redirect_does_not_open_legacy_or_copy_untrusted_query():
    with TestClient(app,base_url='http://localhost:3015') as client:
        response=client.get('/?layer=ai-server&segment=thermal&next=https://evil.invalid&relation=internal',follow_redirects=False)
        assert response.status_code==307 and response.headers['location']=='/next?focus=segment-thermal'
        for query in ['layer=wrong&segment=thermal','layer=ai-server&segment=../../admin','next=https://evil.invalid']:
            assert client.get('/?'+query,follow_redirects=False).headers['location']=='/next'


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
