"""Reader-role contracts for events, observations and comparison on isolated PostgreSQL; all synthetic."""
import os,uuid
from datetime import datetime,timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text,event as sqlalchemy_event
from sqlalchemy.orm import Session
from app.main import app
from app.research_db import get_research_session
from app.research_compile import insert


@pytest.fixture
def dynamic():
    url=os.getenv('RESEARCH_PG_TEST_URL')
    if not url:pytest.skip('Dynamic reader contracts require isolated PostgreSQL')
    engine=create_engine(url,hide_parameters=True)
    if engine.url.database!='industry_research_test':raise RuntimeError('Refusing application dynamic fixtures')
    @sqlalchemy_event.listens_for(engine,'handle_error')
    def debug_database_error(context):print(str(context.original_exception),flush=True)
    connection=engine.connect();transaction=connection.begin();token=uuid.uuid4().hex
    release,ready=uuid.uuid4(),uuid.uuid4();keys=['company-dynamic-'+token+'-'+str(i) for i in range(4)]
    for identifier in (release,ready):insert(connection,'research_releases',{'release_id':identifier,'git_commit':uuid.uuid4().hex+'0'*8,
        'schema_version':'research-v1','content_hash':uuid.uuid4().hex*2,'status':'preparing','reason':'Synthetic dynamic reader test'})
    for index,key in enumerate(keys):
        insert(connection,'entities',{'entity_id':key,'kind':'company'})
        data={'roles':[{'segment-id':'segment-thermal','description':'合成角色'}],'gaps':['合成研究界線'],'research-depth':'basic'}
        insert(connection,'entity_snapshots',{'release_id':release,'entity_id':key,'kind':'company','name':'合成公司'+str(index),
            'summary':'僅測試','markdown':'## 商業模式\n\n合成產品服務\n\n## 風險\n\n合成集中風險','data':data,'semantic_hash':'c'*64})
    source='dynamic-'+token
    connection.execute(text("INSERT INTO public.sources(id,name,url,status,data,new_count) VALUES(:id,'合成來源','https://official.example/','not_run','{}',0)"),{'id':source})
    insert(connection,'release_sources',{'release_id':release,'source_id':source,'name':'此版來源名稱','url':'https://official.example/','data':{}})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':release})
    connection.execute(text("UPDATE research.research_releases SET status='ready' WHERE release_id=:id"),{'id':ready})
    connection.execute(text('INSERT INTO research.release_head VALUES(true,:id,1,now()) ON CONFLICT(singleton) DO UPDATE SET release_id=:id'),{'id':release})
    def write():connection.execute(text('RESET ROLE'))
    def reader():connection.execute(text('SET LOCAL ROLE research_reader'))
    def event(nature='official',relevance='direct',index=0,known=True):
        write();day=datetime(2026,10,15,8,tzinfo=timezone.utc) if known else None
        identifier=connection.execute(text('''INSERT INTO public.events(source_id,external_id,title,body,kind,lifecycle,
            published_at,published_precision,date_semantics,routine,fetched_at,url,mentioned,raw,feeds)
            VALUES(:source,:external,'合成事件','合成事件內容','industry_news','published',:day,:precision,:semantics,false,now(),
                'https://official.example/event','[]','{}','[]') RETURNING id'''),
            {'source':source,'external':uuid.uuid4().hex,'day':day,'precision':'day' if known else 'unknown','semantics':'published' if known else 'unknown'}).scalar_one()
        insert(connection,'event_entity_links',{'event_id':identifier,'entity_id':keys[index],'relevance':relevance,'source_nature':nature})
        reader();return identifier
    session=Session(bind=connection,expire_on_commit=False,join_transaction_mode='create_savepoint')
    app.dependency_overrides[get_research_session]=lambda:session
    reader()
    try:
        with TestClient(app) as client:yield client,keys,release,ready,event,connection
    finally:
        app.dependency_overrides.clear();session.close();transaction.rollback();connection.close();engine.dispose()


def test_two_to_four_profiles_and_missing_research_remain_reachable(dynamic):
    client,keys,release,ready,_,_=dynamic
    result=client.get('/api/v2/compare',params={'company_ids':','.join(keys)});assert result.status_code==200
    assert len(result.json()['data']['companies'])==4 and 'metrics' not in result.json()['data']
    assert result.json()['data']['companies'][0]['risks']=='合成集中風險'
    assert result.headers['cache-control']=='no-store'
    for selected in [keys[:1],[keys[0],keys[0]],keys+[keys[0]]]:
        assert client.get('/api/v2/compare',params={'company_ids':','.join(selected)}).status_code==422
    assert client.get('/api/v2/compare',params={'company_ids':keys[0]+',company-missing'}).status_code==404
    assert client.get('/api/v2/compare',params={'company_ids':','.join(keys[:2]),'release_id':str(ready)}).status_code==404
    # Company financial statements were removed; the reader API no longer serves them.
    assert client.get('/api/v2/companies/'+keys[0]+'/financials',params={'release_id':str(release)}).status_code==404


def test_events_observations_dates_relevance_and_cursor_do_not_mix(dynamic):
    client,keys,_,ready,event,_=dynamic
    official=event();report=event('report','mention');rumor=event('rumor');unknown=event('report','background',known=False)
    data=client.get('/api/v2/events',params={'entity_id':keys[0],'limit':1}).json()['data']
    assert data['items'][0]['id']==report and data['has_more']
    second=client.get('/api/v2/events',params={'entity_id':keys[0],'cursor':data['next_cursor']}).json()['data']['items']
    assert [row['id'] for row in second]==[official,unknown]
    assert second[-1]['date_unknown'] and second[-1]['published_at'] is None
    assert second[0]['source_name']=='此版來源名稱' and 'raw' not in second[0]
    observations=client.get('/api/v2/observations',params={'entity_id':keys[0]}).json()['data']['items']
    assert [row['id'] for row in observations]==[rumor] and observations[0]['source_nature']=='rumor'
    only_mentions=client.get('/api/v2/events',params={'entity_id':keys[0],'relevance':'mention'}).json()['data']['items']
    assert [row['id'] for row in only_mentions]==[report]
    assert client.get('/api/v2/events',params={'source_nature':'rumor'}).status_code==422
    assert client.get('/api/v2/observations',params={'source_nature':'official'}).status_code==422
    assert client.get('/api/v2/events',params={'entity_id':keys[1],'cursor':data['next_cursor']}).status_code==409
    assert client.get('/api/v2/events',params={'release_id':str(ready)}).status_code==404
    assert client.get('/api/v2/events',params={'period_from':'2026-10-16','include_unknown':False}).json()['data']['items']==[]
