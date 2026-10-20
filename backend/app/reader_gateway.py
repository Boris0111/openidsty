"""Credential-free reader entry; fixed upstream and explicit paths/methods only."""
from contextlib import asynccontextmanager
import os
from urllib.parse import quote
import re
import uuid
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

UPSTREAM = 'http://web:3010'
MAX_BODY = 1024 * 1024
MAX_RESPONSE = 32 * 1024 * 1024


@asynccontextmanager
async def lifespan(application):
    async with httpx.AsyncClient(timeout=httpx.Timeout(20, connect=3), follow_redirects=False,
                                 limits=httpx.Limits(max_connections=20, max_keepalive_connections=10), trust_env=False) as client:
        application.state.client = client
        yield


app = FastAPI(lifespan=lifespan, docs_url=None, openapi_url=None, redoc_url=None)


def denied(status, message):
    return JSONResponse({'code':'reader-entry-denied' if status<500 else 'reader-unavailable',
        'message':message,'request_id':uuid.uuid4().hex,'retryable':status==503}, status_code=status,
        headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})


SEGMENT = re.compile(r'[A-Za-z0-9._:-]{1,120}')
# The map, themes and events share the reading shell with /next; coverage, sources and admin stay unreachable.
LEGACY_READS = ('industries', 'segments', 'themes', 'events', 'technical-documents')


def reader_page(path):
    parts = path.split('/')
    if parts[0] in ('themes', 'events'):
        return len(parts) == 1 or len(parts) == 2 and bool(SEGMENT.fullmatch(parts[1]))
    # Old company URLs resolve to the new company research in the browser.
    return parts[0] == 'companies' and len(parts) == 2 and bool(SEGMENT.fullmatch(parts[1]))


def legacy_read(path):
    parts = path.split('/')
    return (len(parts) >= 2 and parts[0] == 'api' and parts[1] in LEGACY_READS and
            all(SEGMENT.fullmatch(part) for part in parts[2:]))


@app.api_route('/{path:path}', methods=['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS'])
async def reader(path: str, request: Request):
    allowed = os.getenv('READER_ALLOWED_HOSTS', '127.0.0.1:3015,localhost:3015,localhost:8000').split(',')
    if request.headers.get('host') not in allowed:
        return denied(403, '此主機名稱不在讀者入口設定中。')
    if path == 'health' and request.method == 'GET':
        return JSONResponse({'status':'ok'}, headers={'Cache-Control':'no-store'})
    if len(path)>2048 or len(request.url.query)>4096 or '\\' in path or '%' in path or any(ord(char)<32 for char in path) or any(part in ('.','..') for part in path.split('/')):
        return denied(403, '此路徑無法由讀者入口存取。')
    readable = path in ('', 'next', 'favicon.ico') or path.startswith(('_next/static/', 'api/v2/')) or reader_page(path) or legacy_read(path)
    permitted = request.method in ('GET','HEAD') and readable or request.method == 'POST' and path == 'api/v2/updates/query'
    if not permitted:
        return denied(403, '讀者入口僅提供已發布研究。')
    content = bytearray()
    if request.method == 'POST':
        async for chunk in request.stream():
            content.extend(chunk)
            if len(content)>MAX_BODY:
                return denied(413, '更新查詢超過大小限制。')
    headers = {name:request.headers[name] for name in ('accept','content-type','if-none-match','rsc','next-router-state-tree','next-router-prefetch') if name in request.headers}
    # Never pass cookies, Authorization, CSRF, forwarding or caller Host headers.
    url = UPSTREAM + '/' + quote(path, safe='/') + ('?'+request.url.query if request.url.query else '')
    try:
        async with request.app.state.client.stream(request.method, url, headers=headers,
                content=bytes(content) if request.method=='POST' else None) as upstream:
            data = bytearray()
            async for chunk in upstream.aiter_bytes():
                data.extend(chunk)
                if len(data)>MAX_RESPONSE:
                    return denied(503, '研究回應超過讀者入口限制，請縮小查詢。')
            forwarded = {name:upstream.headers[name] for name in ('content-type','cache-control','etag','age','content-security-policy','x-request-id','retry-after','vary') if name in upstream.headers}
            forwarded['X-Content-Type-Options'] = 'nosniff'
            if request.method=='HEAD' and upstream.headers.get('content-length'):
                forwarded['Content-Length'] = upstream.headers['content-length']
            # An upstream redirect cannot turn this entry into an arbitrary gateway.
            if 300<=upstream.status_code<400 and upstream.status_code!=304:
                return denied(503, '研究入口暫時無法取得完整回應。')
            if upstream.status_code>=400:
                forwarded['Cache-Control']='no-store'
            return Response(bytes(data), status_code=upstream.status_code, headers=forwarded)
    except httpx.HTTPError:
        return denied(503, '研究服務暫時無法連線，請稍後重試。')
