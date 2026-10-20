"""Reader-role contracts on isolated PostgreSQL; all numbers and issuers synthetic."""
import calendar,os,uuid
from datetime import date,datetime,timezone
from decimal import Decimal
from dataclasses import replace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text,event as sqlalchemy_event
from sqlalchemy.orm import Session
from app.main import app
from app.research_db import get_research_session
from app.research_compile import insert
from app.financial_core import FinancialContext,FinancialValue,RawFact,METRICS,gross_margin
from app.financial_store import register_metrics,save_official,save_derived


@pytest.fixture
def dynamic(request):
    url=os.getenv('RESEARCH_PG_TEST_URL')
    if not url:pytest.skip('Dynamic reader contracts require isolated PostgreSQL')
    engine=create_engine(url,hide_parameters=True)
    if engine.url.database!='industry_research_test':raise RuntimeError('Refusing application financial fixtures')
    @sqlalchemy_event.listens_for(engine,'handle_error')
    def debug_database_error(context):print(str(context.original_exception),flush=True)
    connection=engine.connect();transaction=connection.begin();token=uuid.uuid4().hex
    release,ready=uuid.uuid4(),uuid.uuid4();keys=['company-dynamic-'+token+'-'+str(i) for i in range(4)]
    for identifier in (release,ready):insert(connection,'research_releases',{'release_id':identifier,'git_commit':uuid.uuid4().hex+'0'*8,
        'schema_version':'research-v1','content_hash':uuid.uuid4().hex*2,'status':'preparing','reason':'Synthetic dynamic reader test'})
    for index,key in enumerate(keys):
        insert(connection,'entities',{'entity_id':key,'kind':'company'})
        data={'roles':[{'segment-id':'segment-thermal','description':'合成角色'}],'gaps':['合成研究界線'],'research-depth':'basic'}
        if getattr(request,'param','verified')=='verified':data['financial-reporting']={'primary-source-family':'sec','confidence':'well-supported'}
        insert(connection,'entity_snapshots',{'release_id':release,'entity_id':key,'kind':'company','name':'合成公司'+str(index),
            'summary':'僅測試','markdown':'## 商業模式\n\n合成產品服務\n\n## 風險\n\n合成集中風險','data':data,'semantic_hash':'c'*64})
    source='dynamic-'+token
    connection.execute(text("INSERT INTO public.sources(id,name,url,status,data,new_count) VALUES(:id,'合成來源','https://official.example/','not_run','{}',0)"),{'id':source})
    insert(connection,'release_sources',{'release_id':release,'source_id':source,'name':'此版來源名稱','url':'https://official.example/','data':{}})
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"),{'id':release})
    connection.execute(text("UPDATE research.research_releases SET status='ready' WHERE release_id=:id"),{'id':ready})
    connection.execute(text('INSERT INTO research.release_head VALUES(true,:id,1,now()) ON CONFLICT(singleton) DO UPDATE SET release_id=:id'),{'id':release})
    register_metrics(connection)
    def write():connection.execute(text('RESET ROLE'))
    def reader():connection.execute(text('SET LOCAL ROLE research_reader'))
    def add(number='100',metric='revenue',index=0,**kwargs):
        write()
        start=kwargs.pop('start',date(2025,1,1));end=kwargs.pop('end',date(2025,12,31))
        filed=kwargs.pop('filed',date(2026,2,1));filing=kwargs.pop('filing',uuid.uuid4().hex)
        kind=kwargs.pop('kind','official')
        context=FinancialContext(keys[index],kwargs.pop('family','sec'),metric,start,end,kwargs.pop('basis','annual'),
            scope=kwargs.pop('scope','consolidated'),unit=METRICS[metric][1],currency=kwargs.pop('currency','USD'),
            share_class=kwargs.pop('share_class','ordinary' if metric.startswith('eps-') else ''))
        assert not kwargs,kwargs
        fact=RawFact(context,filing,'synthetic:'+metric,'synthetic original unit',Decimal(number),filed,'https://official.example/'+filing)
        value=FinancialValue(context,Decimal(number),uuid.uuid4(),filing)
        result=save_official(connection,value,(fact,),kind=kind,payloads={str(fact.fact_id):{'locator':'合成財報表格第 3 列','private_diagnostic':'must not leak'}})
        reader();return value,fact,result
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
        with TestClient(app) as client:yield client,keys,release,ready,add,event,connection
    finally:
        app.dependency_overrides.clear();session.close();transaction.rollback();connection.close();engine.dispose()


def values(client,key,**params):
    response=client.get('/api/v2/companies/'+key+'/financials',params=params)
    assert response.status_code==200,response.text
    return response.json()['data']


def comparison(client,keys,**params):
    response=client.get('/api/v2/compare',params={'company_ids':','.join(keys),**params})
    assert response.status_code==200,response.text
    return {item['metric_id']:item for item in response.json()['data']['metrics']}


def test_exact_decimal_latest_restatement_provenance_and_revision_pagination(dynamic):
    client,keys,release,_,add,_,_=dynamic
    original,_,one=add('12345678901234567890.1234567890',filed=date(2026,1,20))
    revised,_,two=add('12345678901234567891.1234567890',filed=date(2026,2,20))
    same,_,three=add('12345678901234567891.1234567890',filed=date(2026,3,20))
    late,_,four=add('99',filed=date(2026,1,1))
    rows=values(client,keys[0])['items'];assert len(rows)==1
    row=rows[0];assert row['value']=='12345678901234567891.123456789'
    assert row['observation_id']==str(revised.observation_id) and row['revision']==2 and len(row['sources'])==2
    assert row['sources'][0]['locator']=='合成財報表格第 3 列'
    assert 'private_diagnostic' not in str(row)
    assert not three['new_revision'] and four['revision']==3
    detail=client.get(row['detail_url'],params={'limit':1}).json()['data']
    assert detail['active_observation_id']==str(revised.observation_id)
    assert detail['revisions'][0]['observation_id']==str(late.observation_id) and detail['has_more']
    older=client.get(row['detail_url'],params={'before_revision':detail['next_before_revision']}).json()['data']['revisions']
    assert [item['revision'] for item in older]==[2,1]
    assert older[0]['supersedes']==str(original.observation_id)
    assert client.get('/api/v2/companies/'+keys[1]+'/financials/observations/'+str(revised.observation_id)).status_code==404


def test_derivation_retains_formula_inputs_and_reachable_originals(dynamic):
    client,keys,_,_,add,_,connection=dynamic
    revenue,_,_=add('200',filing='same-report');gross,_,_=add('80',metric='gross-profit',filing='same-report')
    connection.execute(text('RESET ROLE'));save_derived(connection,gross_margin(gross,revenue),filed_at=date(2026,2,1));connection.execute(text('SET LOCAL ROLE research_reader'))
    row=values(client,keys[0],metric='gross-margin')['items'][0]
    assert row['value']=='40' and row['derived'] and row['formula']=='input[0] / input[1] * 100'
    assert [part['value'] for part in row['lineage']]==['80','200']
    assert all(client.get(part['url']).status_code==200 for part in row['lineage'])
    assert values(client,keys[0],metric='eps-basic')['items']==[]


@pytest.mark.parametrize('currency,scope,start,share,metric,expected',[
    ('USD','consolidated',date(2025,1,1),'','revenue',True),
    ('TWD','consolidated',date(2025,1,1),'','revenue',False),
    ('USD','issuer-summary-unspecified',date(2025,1,1),'','revenue',False),
    ('USD','consolidated',date(2025,2,1),'','revenue',False),
    ('USD','consolidated',date(2025,1,1),'adr','eps-basic',False),
    ('USD','consolidated',date(2025,1,1),'unspecified','eps-basic',False),
    ('TWD','consolidated',date(2025,1,1),'','gross-margin',True)
])
def test_compare_compatible_and_incompatible_currency_period_scope_and_eps(dynamic,currency,scope,start,share,metric,expected):
    client,keys,_,_,add,_,_=dynamic
    first=add('0',metric=metric)
    add('25',metric=metric,index=1,currency=currency,scope=scope,start=start,share_class=share)
    row=comparison(client,keys[:2])[metric]
    assert row['comparable']==expected,row
    assert bool(row['reasons'])!=expected
    assert row['values'][0]['value']=='0' # A valid zero is never replaced by a gap.
    other=comparison(client,keys[:2])['capex'];assert not other['comparable'] and not other['values']


def test_basic_and_diluted_eps_are_separate_and_primary_source_is_not_spliced(dynamic):
    client,keys,_,_,add,_,_=dynamic
    add('4',metric='eps-basic');add('3',metric='eps-diluted',index=1)
    add('200',index=1,family='other-official')
    result=comparison(client,keys[:2])
    assert result['eps-basic']['missing_company_ids']==[keys[1]]
    assert result['eps-diluted']['missing_company_ids']==[keys[0]]
    assert result['revenue']['values']==[] # No preferred-family value; retain auxiliary data via financials.
    assert values(client,keys[1],source_family='other-official')['items'][0]['value']=='200'


@pytest.mark.parametrize('dynamic',['unverified'],indirect=True)
def test_missing_primary_source_is_explicit_not_automatic_ranking(dynamic):
    client,keys,_,_,add,_,_=dynamic
    add();add(index=1)
    row=comparison(client,keys[:2])['revenue']
    assert not row['comparable'] and any('主要申報來源' in reason for reason in row['reasons'])
    assert values(client,keys[0])['source_selection_gap']


def test_two_to_four_profiles_and_missing_research_remain_reachable(dynamic):
    client,keys,release,ready,add,_,_=dynamic
    result=client.get('/api/v2/compare',params={'company_ids':','.join(keys)});assert result.status_code==200
    assert len(result.json()['data']['companies'])==4
    assert result.json()['data']['companies'][0]['risks']=='合成集中風險'
    assert result.headers['cache-control']=='no-store'
    for selected in [keys[:1],[keys[0],keys[0]],keys+[keys[0]]]:
        assert client.get('/api/v2/compare',params={'company_ids':','.join(selected)}).status_code==422
    assert client.get('/api/v2/compare',params={'company_ids':keys[0]+',company-missing'}).status_code==404
    assert client.get('/api/v2/compare',params={'company_ids':','.join(keys[:2]),'release_id':str(ready)}).status_code==404
    assert client.get('/api/v2/companies/company-missing/financials').status_code==404


def test_financial_pagination_and_window_are_sql_bounded(dynamic):
    client,keys,_,ready,add,_,_=dynamic
    for year in range(2021,2026):add(str(year),start=date(year,1,1),end=date(year,12,31),filed=date(2026,2,year-2000))
    first=values(client,keys[0],limit=1)
    assert first['has_more'] and first['items'][0]['value']=='2025'
    second=values(client,keys[0],limit=100,cursor=first['next_cursor'])
    assert [row['value'] for row in second['items']]==['2024','2023'] and not second['has_more']
    path='/api/v2/companies/'+keys[0]+'/financials'
    assert client.get(path,params={'cursor':first['next_cursor'],'metric':'capex'}).status_code==409
    for params in [{'cursor':'!bad'},{'metric':'debt-guessed'},{'limit':101},{'period_from':'2026-01-01','period_to':'2025-01-01'}]:assert client.get(path,params=params).status_code==422
    assert client.get(path,params={'release_id':str(ready)}).status_code==404


def test_events_observations_dates_relevance_and_cursor_do_not_mix(dynamic):
    client,keys,_,ready,_,event,_=dynamic
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


def test_same_period_multiple_scopes_cannot_be_chosen_arbitrarily(dynamic):
    client,keys,_,_,add,_,_=dynamic
    add(scope='individual');add(scope='whole-filing-entity');add(index=1)
    row=comparison(client,keys[:2])['revenue']
    assert not row['comparable'] and row['ambiguous_company_ids']==[keys[0]]
    assert len(row['values'])==3


def test_monthly_and_quarter_windows_and_citations_do_not_grant_raw_access(dynamic):
    client,keys,_,_,add,_,connection=dynamic
    for index in range(40):
        year=2022+index//12;month=index%12+1
        add(str(index),basis='monthly',start=date(year,month,1),end=date(year,month,calendar.monthrange(year,month)[1]))
    for index in range(10):
        year=2023+index//4;month=index%4*3+1;end_month=month+2
        add(str(index),basis='quarterly',start=date(year,month,1),end=date(year,end_month,calendar.monthrange(year,end_month)[1]))
    assert len(values(client,keys[0],basis='monthly',limit=100)['items'])==36
    assert len(values(client,keys[0],basis='quarterly',limit=100)['items'])==8
    assert not connection.execute(text("SELECT has_table_privilege(current_user,'research.financial_raw_facts','SELECT')")).scalar_one()
    columns=connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='research' AND table_name='financial_fact_citations'")).scalars().all()
    assert 'payload' not in columns and 'locator' in columns


def test_non_calendar_quarters_and_total_net_income_are_not_substituted(dynamic):
    client,keys,_,_,add,_,_=dynamic
    add('100',basis='quarterly',start=date(2025,10,1),end=date(2025,12,31))
    add('200',index=1,basis='quarterly',start=date(2025,11,1),end=date(2026,1,31))
    row=comparison(client,keys[:2],basis='quarterly')['revenue']
    assert not row['comparable'] and any('實際期間' in reason for reason in row['reasons'])
    add('50',metric='net-income-parent');add('60',index=1,metric='net-income-total')
    row=comparison(client,keys[:2])['net-income-parent']
    assert row['missing_company_ids']==[keys[1]]


def test_consolidated_default_keeps_other_scopes_available_explicitly(dynamic):
    client,keys,_,_,add,_,_=dynamic
    add('100',scope='individual');add('200');add('300',scope='whole-filing-entity')
    assert [row['value'] for row in values(client,keys[0])['items']]==['200']
    assert len(values(client,keys[0],all_scopes=True)['items'])==3
    assert values(client,keys[0],scope='individual')['items'][0]['value']=='100'


def test_comparison_scope_preference_precedes_candidate_limit(dynamic):
    client,keys,_,_,add,_,_=dynamic
    for index in range(12):add(str(index),scope='alternative-'+str(index))
    add('100');add('200',index=1)
    result=comparison(client,keys[:2])['revenue']
    assert result['comparable'] and [row['value'] for row in result['values']]==['100','200']


def test_same_end_with_two_actual_starts_is_ambiguous_not_latest_start_wins(dynamic):
    client,keys,_,_,add,_,_=dynamic
    add('100');add('200',start=date(2025,2,1));add('300',index=1,start=date(2025,2,1))
    result=comparison(client,keys[:2])['revenue']
    assert not result['comparable'] and result['ambiguous_company_ids']==[keys[0]]
