"""Offline HTTP, durable retry and source isolation; never touches the app DB."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import asyncio,gzip,json,uuid,subprocess,sys,os
import httpx,pytest
from sqlalchemy import text
from app.source_http import SourceHttp,SourceDeferred,RetryExhausted,RequestBudget,check_url,retry_after
from app.source_updates import queue,process,get_job,interval
from app.source_ingestion import nature
from app.models import Event
from test_research_auth import owner,login,ORIGIN

UTC=timezone.utc
BODY=Path(__file__).parent/'fixtures/official-tw-20261017/twse-revenue.selected.json'


def dns(*args,**kwargs):return [(2,1,6,'',('93.184.216.34',443))]


class MemoryBudget:
    def __init__(self):self.count=0;self.delays=[];self.clock=datetime.now(UTC);self.until=None
    def reserve(self,url):
        if self.until and self.until>self.clock:raise SourceDeferred(self.until,503)
        if self.count>=4:raise RetryExhausted('Synthetic budget exhausted')
        self.count+=1;return self.count
    def delay(self,url,until,provider=False):self.until=until;self.delays.append((until,provider))
    def sleep(self,seconds):self.clock=max(self.clock+timedelta(seconds=seconds),self.until or self.clock)+timedelta(milliseconds=1)


@pytest.mark.parametrize('status,expected',[(403,1),(503,4)])
def test_http_attempt_budget_and_terminal_403(status,expected):
    budget=MemoryBudget();calls=[]
    def transport(request):calls.append(request);return httpx.Response(status)
    http=SourceHttp(budget,{'official.example'},client=httpx.Client(transport=httpx.MockTransport(transport)),resolve=dns,sleep=budget.sleep)
    with pytest.raises(httpx.HTTPStatusError):http.get('https://official.example/data')
    assert len(calls)==budget.count==expected
    assert len(budget.delays)==expected-1
    http.close()


def test_429_defers_without_waiting_or_resetting_budget():
    budget=MemoryBudget();http=SourceHttp(budget,{'official.example'},
        client=httpx.Client(transport=httpx.MockTransport(lambda _:httpx.Response(429,headers={'Retry-After':'120'}))),resolve=dns,sleep=budget.sleep)
    before=datetime.now(UTC)
    with pytest.raises(SourceDeferred) as caught:http.get('https://official.example/data')
    assert caught.value.until>=before+timedelta(seconds=120)
    assert budget.count==1 and budget.delays[0][1] is True
    http.close()


def test_compressed_response_is_not_decoded_twice():
    budget=MemoryBudget();body=b'{"official":"sample"}'
    http=SourceHttp(budget,{'official.example'},client=httpx.Client(transport=httpx.MockTransport(
        lambda _:httpx.Response(200,headers={'Content-Encoding':'gzip'},content=gzip.compress(body)))),resolve=dns,sleep=budget.sleep)
    assert http.get('https://official.example/data').content==body
    http.close()


def test_private_hosts_redirects_and_retry_after_not_shortened():
    with pytest.raises(ValueError):check_url('https://official.example/',{'official.example'},lambda *args,**kwargs:[(2,1,6,'',('127.0.0.1',443))])
    budget=MemoryBudget();calls=[]
    def transport(request):calls.append(request);return httpx.Response(302,headers={'Location':'https://127.0.0.1/private'})
    http=SourceHttp(budget,{'official.example'},client=httpx.Client(transport=httpx.MockTransport(transport)),resolve=dns,sleep=budget.sleep)
    with pytest.raises(ValueError):http.get('https://official.example/data')
    assert len(calls)==1
    now=datetime.now(UTC)
    assert retry_after('2592000',now)==now+timedelta(days=30)
    http.close()


def test_official_report_rumor_and_frequency_are_distinct():
    event=Event(title='傳出 AI 伺服器供應消息',body='尚未獲得官方確認')
    assert nature({'type':'industry_media'},event)=='rumor'
    assert nature({'type':'filings'},event)=='official'
    event.title='具名公司發布產品';assert nature({'type':'industry_media'},event)=='report'
    assert interval({'adapter':'tw','kind':'revenue'})==24
    assert interval({'adapter':'sec-submissions'})==1


@pytest.fixture
def published_company(owner):
    client,engine=owner
    identifier=uuid.uuid4();company='company-source-'+uuid.uuid4().hex
    with engine.begin() as connection:
        old=connection.execute(text('SELECT release_id FROM research.release_head')).scalar()
        connection.execute(text('''INSERT INTO research.research_releases(release_id,git_commit,schema_version,content_hash,status,reason)
            VALUES(:id,:commit,'research-v1',:hash,'preparing','Synthetic source baseline')'''),
            {'id':identifier,'commit':uuid.uuid4().hex+'0'*8,'hash':uuid.uuid4().hex*2})
        connection.execute(text("INSERT INTO research.entities VALUES(:id,'company')"),{'id':company})
        connection.execute(text('''INSERT INTO research.entity_snapshots(release_id,entity_id,kind,name,summary,markdown,data,semantic_hash)
            VALUES(:release,:id,'company','Synthetic company','Synthetic only','Synthetic only','{}',:hash)'''),
            {'release':identifier,'id':company,'hash':'a'*64})
        connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':identifier})
        connection.execute(text('''INSERT INTO research.release_head(singleton,release_id,generation) VALUES(true,:id,1)
            ON CONFLICT(singleton) DO UPDATE SET release_id=:id,generation=research.release_head.generation+1'''),{'id':identifier})
    response=login(client);assert response.status_code==200
    headers={'Origin':ORIGIN,'X-CSRF-Token':response.json()['csrf_token']}
    yield client,engine,company,headers
    with engine.begin() as connection:
        if old:connection.execute(text('UPDATE research.release_head SET release_id=:id WHERE singleton'),{'id':old})
        else:connection.execute(text('DELETE FROM research.release_head'))


def revenue_rows(connection,source_id):
    return connection.execute(text("SELECT count(*) FROM public.financials WHERE ticker='2330.TW' AND source_id=:id"),{'id':source_id}).scalar_one()


@pytest.fixture
def source_context(published_company,monkeypatch):
    client,engine,company,headers=published_company
    from app import source_updates
    monkeypatch.setattr(source_updates,'writer_engine',lambda:engine)
    monkeypatch.delenv('PREFECT_API_URL',raising=False)
    monkeypatch.setenv('SEC_USER_AGENT','SyntheticOfflineTest contact@example.invalid')
    with engine.begin() as connection:
        release=connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one()
        connection.execute(text("INSERT INTO public.companies(ticker,name,aliases,cik) VALUES('2330.TW','Synthetic TW issuer','[]',NULL) ON CONFLICT DO NOTHING"))
        # Setup belongs to this synthetic preparing release? The published mapping
        # is immutable, so use a new minimal version with the needed mapping.
        current=connection.execute(text('SELECT * FROM research.research_releases WHERE release_id=:id'),{'id':release}).mappings().one()
        new=uuid.uuid4()
        connection.execute(text("INSERT INTO research.research_releases(release_id,git_commit,schema_version,content_hash,status,reason) VALUES(:id,:git,'research-v1',:hash,'preparing','Synthetic source mappings')"),{'id':new,'git':uuid.uuid4().hex+'0'*8,'hash':uuid.uuid4().hex*2})
        connection.execute(text("INSERT INTO research.entity_snapshots SELECT :new,entity_id,kind,name,summary,markdown,data,semantic_hash,reviewed FROM research.entity_snapshots WHERE release_id=:old"),{'new':new,'old':release})
        connection.execute(text("INSERT INTO research.legacy_mappings VALUES(:release,'company','2330.TW',:company)"),{'release':new,'company':company})
        connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':new})
        connection.execute(text('UPDATE research.release_head SET release_id=:id WHERE singleton'),{'id':new})
        connection.execute(text("UPDATE research.source_provider_backoff SET not_before=now()-interval '1 day'"))
    identifiers=[]
    def make_source(adapter='tw',status=None,host='openapi.twse.com.tw',kind='revenue'):
        identifier=('twse-revenue-' if adapter=='tw' else 'source-')+uuid.uuid4().hex
        definition={'id':identifier,'adapter':adapter,'provider':'synthetic-test','name':'Synthetic source','url':'https://'+host+'/data','type':'filings' if adapter=='tw' else 'industry_media'}
        if adapter=='tw':definition['kind']=kind
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO public.sources(id,name,url,status,new_count,data) VALUES(:id,'Synthetic source',:url,'not_run',0,CAST(:data AS jsonb))"),{'id':identifier,'url':definition['url'],'data':json.dumps(definition)})
            job=queue(connection,definition,True)
        identifiers.append(identifier)
        return definition,job['job_id']
    def factory(status=200,body=None,headers=None):
        content=body if body is not None else BODY.read_bytes()
        def create(budget,hosts):return SourceHttp(budget,hosts,client=httpx.Client(transport=httpx.MockTransport(
            lambda request:httpx.Response(status,content=content,headers=headers or {}))),resolve=dns,sleep=lambda _:None)
        return create
    yield client,engine,company,headers,make_source,factory
    with engine.begin() as connection:
        connection.execute(text("UPDATE research.source_refresh_jobs SET status='failed' WHERE source_id=ANY(CAST(:ids AS text[])) AND status IN ('queued','running','deferred')"),{'ids':identifiers})
        connection.execute(text("UPDATE research.source_provider_backoff SET not_before=now()-interval '1 day'"))


def test_success_failure_due_and_official_records_do_not_publish_research(source_context):
    client,engine,company,headers,make,factory=source_context
    good,key=make();bad,bad_key=make()
    with engine.connect() as connection:head=connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one()
    result=process(key,engine,factory())
    assert result['status']=='success',result
    assert 'financial' not in result['result'] and result['result']['new_count']>0
    assert result['result']['mapping_release_id']==str(head)
    details=client.get('/api/admin/sources/'+good['id'])
    assert details.status_code==200 and details.json()['declared']['frequency_hours']==24
    assert process(bad_key,engine,factory(403))['status']=='failed'
    with engine.begin() as connection:
        assert queue(connection,good) is None
        assert connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one()==head
        rows=revenue_rows(connection,good['id']);assert rows>0
    # A later manual run sees the same values; no fake observation revisions.
    response=client.post('/api/admin/sources/'+good['id']+'/refresh',headers=headers)
    assert response.status_code==202,response.text
    duplicate=client.post('/api/admin/sources/'+good['id']+'/refresh',headers=headers)
    assert duplicate.json()['job_id']==response.json()['job_id']
    repeated=process(response.json()['job_id'],engine,factory())
    assert repeated['result']['new_count']==0
    with engine.connect() as connection:assert revenue_rows(connection,good['id'])==rows
    client.cookies.clear();assert client.get('/api/admin/source-jobs/'+str(key)).status_code==401
    assert client.get('/api/admin/sources/'+good['id']).status_code==401


def test_429_provider_backoff_survives_new_client_and_other_source_completes(source_context):
    _,engine,_,_,make,factory=source_context
    first,key=make(host='openapi.twse.com.tw')
    assert process(key,engine,factory(429,headers={'Retry-After':'120'}))['status']=='deferred'
    second,second_key=make(host='openapi.twse.com.tw')
    assert process(second_key,engine,factory())['status']=='deferred'
    good,good_key=make(adapter='rss',host='public.example')
    xml=('<rss><channel><item><title>Official test article</title><link>https://public.example/'+uuid.uuid4().hex+'</link><description>synthetic only</description></item></channel></rss>').encode()
    completed=process(good_key,engine,factory(body=xml))
    assert completed['status']=='partial' and completed['result']['new_count']==1 # Unknown date/history remain explicit.
    with engine.connect() as connection:
        assert sum(item['attempts'] for item in get_job(connection,key)['budget'].values())==1
        assert get_job(connection,second_key)['budget']=={}


def test_shell_failure_does_not_replace_last_valid_values(source_context):
    _,engine,_,_,make,factory=source_context
    definition,key=make();assert process(key,engine,factory())['status']=='success'
    with engine.begin() as connection:
        new=queue(connection,definition,True)
        before=revenue_rows(connection,definition['id'])
    assert process(new['job_id'],engine,factory(body=b'<html><script>shell</script></html>'))['status']=='failed'
    with engine.connect() as connection:
        assert revenue_rows(connection,definition['id'])==before


def test_exhausted_budget_is_not_reset_by_a_new_worker(source_context):
    _,engine,_,_,make,_=source_context
    definition,key=make()
    budget=RequestBudget(engine,key)
    assert [budget.reserve(definition['url']) for _ in range(4)]==[1,2,3,4]
    with pytest.raises(RetryExhausted):RequestBudget(engine,key).reserve(definition['url'])


def financial_store_counts(connection):
    # Empty once migration 0017 drops the store; revenue must never depend on it.
    tables=connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='research' AND table_name LIKE 'financial%'")).scalars().all()
    return {name:connection.execute(text(f'SELECT count(*) FROM research.{name}')).scalar_one() for name in tables}


def test_revenue_source_projects_theme_proxy_without_financial_store(source_context):
    _,engine,_,_,make,factory=source_context
    definition,key=make()
    theme,indicator='theme-proxy-'+uuid.uuid4().hex[:8],'proxy-revenue-'+uuid.uuid4().hex[:8]
    # Same shape as data/theme-indicators.yaml proxy definitions.
    data={'id':indicator,'name':'Synthetic proxy','kind':'proxy','entity':'2330.TW','scope':'公司整體單月營收','limitations':'合成測試',
        'unit':'amount','currency':'TWD','frequency':'monthly','basis':'monthly','source_id':definition['id'],
        'dataset':'synthetic-monthly-revenue','measure':'revenue'}
    with engine.begin() as connection:
        before=financial_store_counts(connection)
        connection.execute(text("INSERT INTO public.themes(id,data,prose,active) VALUES(:id,'{}','',true)"),{'id':theme})
        connection.execute(text("INSERT INTO public.indicators(id,name,kind,unit,frequency,basis,data) VALUES(:id,'Synthetic proxy','proxy','amount','monthly','monthly',CAST(:data AS json))"),
            {'id':indicator,'data':json.dumps(data)})
        connection.execute(text('INSERT INTO public.theme_indicators(theme_id,indicator_id) VALUES(:theme,:id)'),{'theme':theme,'id':indicator})
    try:
        result=process(key,engine,factory())
        assert result['status']=='success' and result['result']['indicator_changes']>=1,result
        with engine.connect() as connection:
            rows=connection.execute(text('SELECT entity,basis,currency FROM public.indicator_observations WHERE indicator_id=:id'),{'id':indicator}).all()
            assert rows and all(row==('2330.TW','monthly','TWD') for row in rows)
            assert financial_store_counts(connection)==before
    finally:
        # Every revenue run projects all proxy indicators; never leave this one for other tests.
        with engine.begin() as connection:
            for table,column in [('indicator_observations','indicator_id'),('theme_indicators','indicator_id'),('indicators','id')]:
                connection.execute(text(f'DELETE FROM public.{table} WHERE {column}=:id'),{'id':indicator})
            connection.execute(text('DELETE FROM public.themes WHERE id=:id'),{'id':theme})


def test_source_changed_to_manual_does_not_run_queued_definition(source_context):
    client,engine,_,headers,make,_=source_context
    source,key=make()
    with engine.begin() as connection:
        connection.execute(text("UPDATE public.sources SET status='manual',data=jsonb_set(data::jsonb,'{adapter}','\"manual\"') WHERE id=:id"),{'id':source['id']})
    def forbidden(*args):raise AssertionError('Manual source must not create HTTP client')
    result=process(key,engine,forbidden)
    assert result['status']=='failed' and result['requests']==0
    assert client.post('/api/admin/sources/'+source['id']+'/refresh',headers=headers).status_code==422
    with engine.connect() as connection:assert connection.execute(text('SELECT status FROM public.sources WHERE id=:id'),{'id':source['id']}).scalar_one()=='manual'


def test_retired_source_refuses_manual_refresh(source_context):
    client,engine,_,headers,make,_=source_context
    source,_=make()
    with engine.begin() as connection:
        connection.execute(text("UPDATE public.sources SET status='retired' WHERE id=:id"),{'id':source['id']})
    response=client.post('/api/admin/sources/'+source['id']+'/refresh',headers=headers)
    assert response.status_code==409 and response.json()['code']=='source-retired'


def test_dispatch_failure_keeps_outbox_then_reconciliation_delivers(source_context,monkeypatch):
    from app.source_updates import dispatch,reconcile
    from types import SimpleNamespace
    _,engine,_,_,make,_=source_context
    _,key=make();sent=[]
    monkeypatch.setenv('PREFECT_API_URL','http://synthetic-prefect.invalid/api')
    class Client:
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def read_deployment_by_name(self,name):
            assert name=='source-updates/refresh'
            if not sent:sent.append('transport-failure');raise ConnectionError('Synthetic transport failure')
            return SimpleNamespace(id=uuid.uuid4())
        async def create_flow_run_from_deployment(self,identifier,parameters):sent.append(parameters['job_id'])
    monkeypatch.setattr('prefect.client.orchestration.get_client',lambda:Client())
    assert asyncio.run(dispatch(key,engine)) is False
    with engine.begin() as connection:
        assert get_job(connection,key)['status']=='queued'
        connection.execute(text("UPDATE research.source_refresh_jobs SET dispatch_after=now()-interval '1 second' WHERE job_id=:id"),{'id':key})
    asyncio.run(reconcile(engine))
    assert str(key) in sent
    assert asyncio.run(dispatch(key,engine)) is False # Lease prevents redundant dispatch.


def test_rumor_linking_only_changes_event_links(source_context):
    from app.source_ingestion import link_events
    from sqlalchemy.orm import Session
    _,engine,company,_,make,_=source_context
    source,_=make(adapter='rss',host='public.example')
    with engine.begin() as connection:
        release=connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one()
        before=connection.execute(text('SELECT content_hash FROM research.research_releases WHERE release_id=:id'),{'id':release}).scalar_one()
        with Session(bind=connection,join_transaction_mode='create_savepoint') as session:
            started=datetime.now(UTC)
            event=Event(source_id=source['id'],external_id=uuid.uuid4().hex,ticker='2330.TW',title='傳出供應客戶消息',body='合成離線測試；未經證實',kind='news',url=source['url'],raw={})
            session.add(event);session.flush()
            link_events(session,source,started,{'2330.TW':company},release)
            assert connection.execute(text('SELECT relevance,source_nature FROM research.event_entity_links WHERE event_id=:id'),{'id':event.id}).one()==('direct','rumor')
            assert connection.execute(text('SELECT content_hash FROM research.research_releases WHERE release_id=:id'),{'id':release}).scalar_one()==before
            assert connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one()==release


def test_real_process_crash_after_data_commit_then_resume_same_job_and_budget(source_context):
    _,engine,company,_,make,_=source_context
    definition,key=make()
    code='''import os,sys,httpx
from pathlib import Path
from sqlalchemy import create_engine
from app.source_updates import process
from app.source_http import SourceHttp
engine=create_engine(os.environ['RESEARCH_PG_WRITER_URL'])
body=Path('tests/fixtures/official-tw-20261017/twse-revenue.selected.json').read_bytes()
def factory(budget,hosts):return SourceHttp(budget,hosts,client=httpx.Client(transport=httpx.MockTransport(lambda _:httpx.Response(200,content=body))),resolve=lambda *a,**k:[(2,1,6,'',('93.184.216.34',443))],sleep=lambda _:None)
def point(stage):
    if stage=='data-committed' and sys.argv[2]=='crash':os._exit(77)
result=process(sys.argv[1],engine,factory,point)
print(result['status'],result['requests'],flush=True)
'''
    crashed=subprocess.run([sys.executable,'-c',code,str(key),'crash'],capture_output=True,text=True,timeout=40)
    assert crashed.returncode==77,crashed.stderr
    with engine.connect() as connection:assert get_job(connection,key)['status']=='running'
    resumed=subprocess.run([sys.executable,'-c',code,str(key),'resume'],capture_output=True,text=True,timeout=40)
    assert resumed.returncode==0,resumed.stderr
    assert resumed.stdout.strip()=='success 2'
    with engine.connect() as connection:
        assert revenue_rows(connection,definition['id'])>0


def test_existing_event_reindex_is_bounded_repeatable_and_never_fetches(source_context):
    from app.source_links import reindex
    from sqlalchemy.orm import Session
    _,engine,company,_,make,_=source_context
    source,_=make(adapter='rss',host='public.example')
    with Session(engine) as session:
        item=Event(source_id=source['id'],external_id=uuid.uuid4().hex,ticker='2330.TW',title='Rumor in preserved history',
            body='Synthetic only',kind='news',url=source['url'],raw={})
        session.add(item);session.commit();identifier=item.id
    for _ in range(2):
        result=reindex(engine,after=identifier-1,limit=1)
        assert result['indexed']==1 and result['last_id']==identifier
    with engine.connect() as connection:
        assert connection.execute(text('SELECT entity_id,relevance,source_nature FROM research.event_entity_links WHERE event_id=:id'),{'id':identifier}).all()==[(company,'direct','rumor')]
