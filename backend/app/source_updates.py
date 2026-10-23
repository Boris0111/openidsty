"""Durable, bounded source updates. No code path publishes authored research."""
import argparse,asyncio,json,os,re,uuid
from datetime import datetime,timedelta,timezone
from urllib.parse import urlsplit
from fastapi import APIRouter,Depends,BackgroundTasks
from sqlalchemy import text,select
from sqlalchemy.orm import Session
from .payloads import encoded,raw_payload
from .research_auth import require_owner,require_owner_write
from .research_db import writer_engine,get_admin_connection
from .research_http import ResearchError
from .research_drafts import respond
from .models import Source,Company,Event,now
from .registry import source_definitions
from .source_http import SourceHttp,RequestBudget,SourceDeferred

UTC=timezone.utc
router=APIRouter(prefix='/api/admin',tags=['source-updates'])
INFLIGHT=('queued','running','deferred')


def interval(definition):
    return 24 if definition.get('kind')=='revenue' or definition['adapter'] in (
        'sec-facts','aaon-metrics','tsmc-metrics','technical-documents') else 1


def refresh_registry(engine):
    with Session(engine,expire_on_commit=False) as session:
        definitions=source_definitions(list(session.scalars(select(Company))))
        for definition in definitions:
            row=session.get(Source,definition['id'])
            if row is None:row=Source(id=definition['id'],status='not_run',new_count=0);session.add(row)
            row.name=definition['name'];row.url=definition['url']
            row.data={**(row.data or {}),**definition}
            if definition['adapter']=='manual':row.status='manual'
            elif row.status=='manual':row.status='not_run'
        session.commit()
    return definitions


def queue(connection,definition,manual=False):
    if definition['adapter']=='manual':raise ResearchError(422,'source-manual-only','此來源僅供人工研究，沒有可執行 adapter。')
    sid=definition['id']
    connection.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:id,38109079))'),{'id':sid})
    current=connection.execute(text("SELECT * FROM research.source_refresh_jobs WHERE source_id=:id AND status IN ('queued','running','deferred')"),{'id':sid}).mappings().first()
    if current:return dict(current)
    source=connection.execute(text('SELECT * FROM public.sources WHERE id=:id'),{'id':sid}).mappings().first()
    if not source:raise ResearchError(404,'source-not-found','找不到這個來源。')
    runtime=source['data'].get('runtime',{})
    next_due=runtime.get('next_due')
    due=datetime.fromisoformat(next_due) if next_due else source['last_attempt']+timedelta(hours=interval(definition)) if source['last_attempt'] else None
    if not manual and due and due>datetime.now(UTC):return None
    config={key:value for key,value in definition.items() if key not in ('runtime','fetch_meta','backfill_meta','backfill_completed_at','last_error_kind','last_http_status')}
    requested=definition.get('_requested_backfill_days')
    payload={**config,'_backfill':requested is not None or not bool(source['data'].get('backfill_completed_at')),
        '_backfill_days':requested or 90,'_force_refresh':manual}
    identifier=uuid.uuid4()
    connection.execute(text('''INSERT INTO research.source_refresh_jobs(job_id,source_id,definition,status)
        VALUES(:id,:source,CAST(:definition AS jsonb),'queued')'''),{'id':identifier,'source':sid,'definition':encoded(payload)})
    if manual:connection.execute(text("INSERT INTO research.audit_log(actor,operation,detail) VALUES('owner','source-refresh',CAST(:detail AS jsonb))"),
        {'detail':encoded({'job_id':str(identifier),'source_id':sid})})
    return get_job(connection,identifier)


def get_job(connection,identifier):
    row=connection.execute(text('SELECT * FROM research.source_refresh_jobs WHERE job_id=:id'),{'id':identifier}).mappings().first()
    if not row:raise ResearchError(404,'source-job-not-found','找不到這份來源更新作業。')
    return dict(row)


def job_payload(row):
    return {'job_id':str(row['job_id']),'source_id':row['source_id'],'status':row['status'],
        'available_at':row['available_at'].isoformat(),'result':row['result'],'failure':row['failure'],
        'requests':sum(value['attempts'] for value in row['budget'].values())}


@router.post('/sources/{source_id}/refresh',status_code=202)
def request_refresh(source_id:str,background:BackgroundTasks,owner=Depends(require_owner_write),connection=Depends(get_admin_connection)):
    source=connection.execute(text('SELECT id,name,url,data FROM public.sources WHERE id=:id'),{'id':source_id}).mappings().first()
    if not source:raise ResearchError(404,'source-not-found','找不到這個來源。')
    definition={**source['data'],'id':source_id,'name':source['name'],'url':source['url'],'adapter':source['data'].get('adapter','manual')}
    result=queue(connection,definition,True)
    connection.commit()
    background.add_task(dispatch,result['job_id'])
    return respond(job_payload(result),status=202)


@router.get('/source-jobs/{job_id}')
def read_job(job_id:uuid.UUID,owner=Depends(require_owner),connection=Depends(get_admin_connection)):
    return respond(job_payload(get_job(connection,job_id)))


async def dispatch(identifier,engine=None):
    engine=engine or writer_engine()
    if not os.getenv('PREFECT_API_URL'):return False
    with engine.begin() as connection:
        row=connection.execute(text("""UPDATE research.source_refresh_jobs SET dispatch_after=now()+interval '2 minutes'
            WHERE job_id=:id AND status IN ('queued','running','deferred') AND available_at<=now()
            AND (dispatch_after IS NULL OR dispatch_after<=now()) RETURNING job_id"""),{'id':identifier}).first()
        if not row:return False
    try:
        from prefect.client.orchestration import get_client
        async with asyncio.timeout(5):
            async with get_client() as client:
                deployment=await client.read_deployment_by_name('source-updates/refresh')
                await client.create_flow_run_from_deployment(deployment.id,parameters={'job_id':str(identifier)})
        return True
    except Exception:return False # DB outbox and due time survive transport failure.


async def reconcile(engine=None):
    engine=engine or writer_engine()
    with engine.connect() as connection:
        keys=connection.execute(text("""SELECT job_id FROM research.source_refresh_jobs WHERE status IN ('queued','running','deferred')
            AND available_at<=now() AND (dispatch_after IS NULL OR dispatch_after<=now()) ORDER BY available_at LIMIT 50""")).scalars().all()
    for key in keys:await dispatch(key,engine)
    return {'examined':len(keys)}


def enqueue_due(engine=None,only=None,backfill_days=None):
    engine=engine or writer_engine();definitions=refresh_registry(engine);keys=[]
    if only:
        definitions=[row for row in definitions if row['id'] in only]
        if not definitions:raise ValueError('指定來源不存在。')
    with engine.begin() as connection:
        for definition in definitions:
            if definition['adapter']=='manual':continue
            if backfill_days is not None:definition={**definition,'_requested_backfill_days':backfill_days}
            row=queue(connection,definition,manual=bool(only) or backfill_days is not None)
            if row:keys.append(str(row['job_id']))
    return keys


def allowed_hosts(definition):
    hosts={urlsplit(definition[key]).hostname for key in ('url','fallback','registry_url') if definition.get(key)}
    hosts.update(definition.get('allowed-hosts',[]))
    if hosts&{'sec.gov','www.sec.gov','data.sec.gov'}:hosts.update(('sec.gov','www.sec.gov','data.sec.gov'))
    return hosts-{None}


def describe_capabilities(definition):
    adapter=definition.get('adapter','manual')
    return {'can_refresh':adapter!='manual','frequency_hours':interval({**definition,'adapter':adapter}),
        'source_nature':'report' if definition.get('type')=='industry_media' else 'official',
        'history_limit':'營收依官方實際提供的期間；事件首次嘗試 90 日，受 feed／分頁與可讀範圍限制。',
        'classification_limit':'媒體文字涉及匿名／傳聞時另列觀察；自動分類不提升研究主張確定性。'}


@router.get('/sources/{source_id}')
def read_source(source_id:str,owner=Depends(require_owner),connection=Depends(get_admin_connection)):
    source=connection.execute(text('SELECT * FROM public.sources WHERE id=:id'),{'id':source_id}).mappings().first()
    if not source:raise ResearchError(404,'source-not-found','找不到這個來源。')
    recent=connection.execute(text('SELECT * FROM research.source_refresh_jobs WHERE source_id=:id ORDER BY created_at DESC LIMIT 1'),{'id':source_id}).mappings().first()
    return respond({'source_id':source_id,'name':source['name'],'declared':describe_capabilities(source['data']),
        'last_result':source['data'].get('runtime',{}).get('result'),'last_job':job_payload(recent) if recent else None,
        'last_success':source['last_success'],'last_attempt':source['last_attempt'],'status':source['status'],'error':source['error']})


def update_health(engine,row,status,result,error=None,available=None):
    with Session(engine,expire_on_commit=False) as session:
        source=session.get(Source,row['source_id']);source.last_attempt=row.get('attempt_started',now());source.new_count=result.get('new_count',0)
        source.status=status;source.error=error
        if status in ('success','partial'):source.last_success=now()
        runtime={**source.data.get('runtime',{}),'next_due':(available or now()+timedelta(hours=interval(row['definition']))).isoformat(),
            'last_job_id':str(row['job_id']),'result':result,'frequency_hours':interval(row['definition'])}
        source.data={**source.data,'runtime':runtime,'last_http_status':result.get('http_status'),
            'last_error_kind':result.get('error_kind') if error else None}
        failure={'message':error,'retryable':status=='deferred'} if error else None
        session.execute(text('''UPDATE research.source_refresh_jobs SET status=:status,result=CAST(:result AS jsonb),
            failure=CAST(:failure AS jsonb),available_at=COALESCE(:available,available_at),updated_at=now() WHERE job_id=:id'''),
            {'status':'failed' if status=='configuration_required' else status,'result':encoded(raw_payload(result)),'failure':encoded(failure),'available':available,'id':row['job_id']})
        session.commit()


def process(identifier,engine=None,http_factory=SourceHttp,point=lambda _:None):
    engine=engine or writer_engine();identifier=uuid.UUID(str(identifier))
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as guard:
        locked=guard.execute(text('SELECT pg_try_advisory_lock(hashtextextended(:id,38109080))'),{'id':str(identifier)}).scalar_one()
        if not locked:return {'status':'skipped_overlap'}
        http=None;row=None
        try:
            with engine.begin() as connection:
                row=get_job(connection,identifier)
                if row['status'] not in INFLIGHT or row['available_at']>datetime.now(UTC):return job_payload(row)
                adapter=connection.execute(text("SELECT data->>'adapter' FROM public.sources WHERE id=:id"),{'id':row['source_id']}).scalar_one()
                if adapter=='manual':
                    connection.execute(text("UPDATE research.source_refresh_jobs SET status='failed',failure=CAST(:failure AS jsonb),updated_at=now() WHERE job_id=:id"),
                        {'id':identifier,'failure':encoded({'message':'來源已改為人工維護，未發出請求。','retryable':False})})
                    return job_payload(get_job(connection,identifier))
                connection.execute(text("UPDATE research.source_refresh_jobs SET status='running',dispatch_after=now()+interval '2 minutes',updated_at=now() WHERE job_id=:id"),{'id':identifier})
            point('claimed')
            row['attempt_started']=datetime.now(UTC)
            http=http_factory(RequestBudget(engine,identifier),allowed_hosts(row['definition']))
            from .source_ingestion import ingest_definition
            try:
                with engine.connect() as connection:
                    transaction=connection.begin()
                    try:
                        with Session(bind=connection,expire_on_commit=False,join_transaction_mode='create_savepoint') as session:
                            result=ingest_definition(session,row['definition'],http)
                            result.update(http_status=http.last_status,error_kind=http.error_kind or ('parse' if result.get('error') else None))
                        if http.deferred:raise SourceDeferred(http.deferred)
                        if result['status'] in ('failed','configuration_required'):transaction.rollback()
                        else:transaction.commit()
                    except BaseException:transaction.rollback();raise
                point('data-committed')
                update_health(engine,row,result['status'],result,result.get('error'))
            except SourceDeferred as error:
                update_health(engine,row,'deferred',{'new_count':0},str(error),error.until)
            except Exception:
                update_health(engine,row,'failed',{'new_count':0},'來源更新未完成；有效資料已保留，請檢閱來源能力與重試紀錄。')
            with engine.connect() as connection:return job_payload(get_job(connection,identifier))
        except Exception:
            if row is None:raise
            update_health(engine,row,'failed',{'new_count':0},'來源作業未完成；已保存原資料，其他來源可繼續。')
            with engine.connect() as connection:return job_payload(get_job(connection,identifier))
        finally:
            if http:http.close()
            try:guard.execute(text('SELECT pg_advisory_unlock(hashtextextended(:id,38109080))'),{'id':str(identifier)})
            except Exception:guard.invalidate()


def run_due(only=None,engine=None,backfill_days=None):
    engine=engine or writer_engine();keys=enqueue_due(engine,only,backfill_days)
    # Existing interrupted/queued jobs are included even when no new source is due.
    with engine.connect() as connection:
        keys=connection.execute(text("""SELECT job_id FROM research.source_refresh_jobs WHERE status IN ('queued','running','deferred')
            AND available_at<=now() AND (:all_sources OR source_id=ANY(CAST(:only AS text[]))) ORDER BY available_at LIMIT 200"""),
            {'all_sources':not bool(only),'only':only or []}).scalars().all()
    results={}
    for key in keys:
        try:results[str(key)]=process(key,engine)
        except Exception:results[str(key)]={'status':'unavailable','retryable':True,'message':'來源作業暫時無法完成；持久作業仍保留。'}
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',action='append');parser.add_argument('--job',type=uuid.UUID)
    args=parser.parse_args()
    print(json.dumps(process(args.job) if args.job else run_due(args.source),ensure_ascii=False))


if __name__=='__main__':main()
