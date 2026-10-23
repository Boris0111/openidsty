"""HTTP representation validators, not a server-side payload/authentication cache."""
import hashlib
import json
import re
from urllib.parse import urlencode
from starlette.responses import Response, StreamingResponse

STATIC = {'catalog','chains','search','resolve','companies','products','themes','concepts','research',
          'applications','roles','segments','documents','graphs','impact','compare'}
JSON_LIMIT = 8 * 1024 * 1024


def lifetime(path, query):
    if len(query.getlist('release_id')) != 1 or not query.get('release_id'):
        return 0
    parts = path.removeprefix('/api/v2/').split('/')
    if parts[0] in ('events','observations') or 'financials' in parts:
        # Observation details also contain the current effective ID and revision list.
        return 30
    return 86400 if parts[0] in STATIC else 0


def matches(condition, tag):
    if not condition or len(condition) > 4096:
        return False
    return any(value == '*' or value.removeprefix('W/') == tag.removeprefix('W/')
               for value in re.findall(r'(?:W/)?"[^"\r\n]*"|\*', condition))


async def reader_cache(request, response):
    if request.url.path.startswith('/api/admin/'):
        response.headers['Cache-Control'] = 'no-store'
        return response  # Draft ETags remain available for If-Match, never shared caching.
    if not request.url.path.startswith('/api/v2/') or request.method != 'GET':
        return response
    if response.status_code != 200:
        response.headers['Cache-Control'] = 'no-store'
        return response
    # Always execute the reader endpoint first: published-release and asset authorization
    # must succeed even when the caller supplies a matching validator.
    age = lifetime(request.url.path, request.query_params)
    if request.url.path.startswith('/api/v2/assets/'):
        age = 31536000 if request.query_params.get('release_id') and len(request.query_params.getlist('release_id')) == 1 else 0
        response.headers['Cache-Control'] = f'public,max-age={age},immutable' if age else 'no-store'
        tag = response.headers.get('ETag') if age else None
        if not age and 'ETag' in response.headers:
            del response.headers['ETag']
    elif age and response.headers.get('content-type','').startswith('application/json'):
        chunks, size = [], 0
        async for chunk in response.body_iterator:
            chunks.append(chunk)
            size += len(chunk)
            if size > JSON_LIMIT:
                async def remaining():
                    for part in chunks:
                        yield part
                    async for part in response.body_iterator:
                        yield part
                headers = dict(response.headers)
                headers['Cache-Control'] = 'no-store'
                return StreamingResponse(remaining(),status_code=200,headers=headers,background=response.background)
        body = b''.join(chunks)
        payload = json.loads(body)
        # Weak validator: a later read timestamp alone is not a new representation.
        if isinstance(payload.get('data'),dict):
            payload['data'].pop('as_of',None)
        key = request.url.path + '?' + urlencode(sorted(request.query_params.multi_items()))
        digest = hashlib.sha256(key.encode()+b'\0'+json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        tag = 'W/"'+digest+'"'
        headers = dict(response.headers)
        headers.update({'ETag':tag,'Cache-Control':f'public,max-age={age},must-revalidate'})
        response = Response(body,status_code=200,headers=headers,background=response.background)
    else:
        response.headers['Cache-Control'] = 'no-store'
        return response
    if tag and matches(request.headers.get('if-none-match'),tag):
        headers = {key:value for key,value in response.headers.items() if key.lower() not in ('content-length','content-type')}
        return Response(status_code=304,headers=headers,background=response.background)
    return response
