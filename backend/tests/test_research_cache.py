"""Published reader cache contracts on a rollback-only, isolated PostgreSQL DB."""
from sqlalchemy import text
from app.main import app
from app.research_compile import insert
from app.research_db import get_research_session
from app.research_http import ResearchError
from test_research_dynamic import dynamic
from test_research_v2 import v2


def test_static_pins_conditionals_canonical_parameters_and_unpublished_denial(v2):
    client,data=v2
    path='/api/v2/companies/'+data['keys'][0]
    result=client.get(path,params={'release_id':data['release']})
    assert result.status_code==200 and 'max-age=86400' in result.headers['cache-control']
    tag=result.headers['etag']
    repeated=client.get(path,params={'release_id':data['release']},headers={'If-None-Match':'"other", '+tag})
    assert repeated.status_code==304 and not repeated.content and repeated.headers['etag']==tag
    assert client.get(path,params={'release_id':data['ready']},headers={'If-None-Match':'*'}).status_code==404
    assert client.get('/api/v2/manifest',headers={'If-None-Match':'*'}).headers['cache-control']=='no-store'
    assert client.get(path,headers={'If-None-Match':tag}).status_code==200
    assert client.get(path).headers['cache-control']=='no-store'
    a=client.get('/api/v2/companies',params=[('limit','1'),('release_id',data['release'])])
    b=client.get('/api/v2/companies',params=[('release_id',data['release']),('limit','1')],headers={'If-None-Match':a.headers['etag']})
    assert b.status_code==304
    for path in ['/api/admin/session','/api/admin/drafts']:
        result=client.get(path,headers={'If-None-Match':'*'})
        assert result.status_code!=304 and result.headers['cache-control']=='no-store'


def test_compare_is_pinned_research_and_long_cached(v2):
    client,data=v2
    params={'release_id':data['release'],'company_ids':','.join(data['keys'][:2])}
    result=client.get('/api/v2/compare',params=params)
    assert result.status_code==200 and 'max-age=86400' in result.headers['cache-control']
    assert client.get('/api/v2/compare',params=params,headers={'If-None-Match':result.headers['etag']}).status_code==304
    # Without a pinned release the reader must re-read the current head.
    assert client.get('/api/v2/compare',params={'company_ids':params['company_ids']}).headers['cache-control']=='no-store'


def test_head_publish_restore_keeps_pinned_profiles(dynamic):
    client,keys,release,ready,_,connection=dynamic
    path='/api/v2/companies/'+keys[0]
    original=client.get(path,params={'release_id':str(release)})
    connection.execute(text('RESET ROLE'))
    for key in keys:
        row=connection.execute(text('SELECT * FROM research.entity_snapshots WHERE release_id=:r AND entity_id=:id'),{'r':release,'id':key}).mappings().one()
        insert(connection,'entity_snapshots',{**dict(row),'release_id':ready,'name':'新版公司','semantic_hash':'d'*64})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':ready})
    connection.execute(text('UPDATE research.release_head SET release_id=:id,generation=generation+1'),{'id':ready})
    connection.execute(text('SET LOCAL ROLE research_reader'))
    assert client.get('/api/v2/manifest').json()['release_id']==str(ready)
    assert client.get(path,params={'release_id':str(release)},headers={'If-None-Match':original.headers['etag']}).status_code==304
    newer=client.get(path,params={'release_id':str(ready)})
    assert newer.json()['data']['name']=='新版公司' and newer.headers['etag']!=original.headers['etag']
    connection.execute(text('RESET ROLE'))
    connection.execute(text('UPDATE research.release_head SET release_id=:id,generation=generation+1'),{'id':release})
    connection.execute(text('SET LOCAL ROLE research_reader'))
    assert client.get('/api/v2/manifest').json()['release_id']==str(release)
    assert client.get(path,params={'release_id':str(ready)},headers={'If-None-Match':newer.headers['etag']}).status_code==304


def test_events_revalidate_and_failures_never_become_success_cache(dynamic):
    client,_,release,ready,event,_=dynamic
    params={'release_id':str(release)}
    result=client.get('/api/v2/events',params=params)
    event()
    updated=client.get('/api/v2/events',params=params,headers={'If-None-Match':result.headers['etag']})
    assert updated.status_code==200 and 'max-age=30' in updated.headers['cache-control']
    denied=client.get('/api/v2/events',params={'release_id':str(ready)},headers={'If-None-Match':updated.headers['etag']})
    assert denied.status_code==404 and denied.headers['cache-control']=='no-store' and 'etag' not in denied.headers


def test_conditional_read_cannot_hide_database_outage(v2):
    client,data=v2
    path='/api/v2/companies/'+data['keys'][0]
    response=client.get(path,params={'release_id':data['release']})
    def unavailable():
        raise ResearchError(503,'database-unavailable','目前無法讀取研究，請稍後再試。',True)
    app.dependency_overrides[get_research_session]=unavailable
    result=client.get(path,params={'release_id':data['release']},headers={'If-None-Match':response.headers['etag']})
    assert result.status_code==503 and result.json()['retryable']
    assert result.headers['cache-control']=='no-store' and 'etag' not in result.headers
