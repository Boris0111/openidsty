import json
import re
import hashlib
from contextlib import contextmanager
from sqlalchemy import select, text, or_
from .db import Session
from .models import Source, Company, Event, Financial, IngestionRun, now
from .connectors import OfficialHttp, source_definitions, fetch_source
from .classify import classify_event, rules
from .event_dates import normalize_dates
from .industry_connectors import canonical_url
from .source_diagnostics import failure_details

def mentioned_companies(text,companies,primary):
    found=[]
    for c in companies:
        if c.ticker==primary:
            continue
        for alias in c.aliases:
            if not alias:
                continue
            # Chinese has no \b word boundary. ASCII aliases need lexical guards.
            pattern=re.escape(alias)
            if re.fullmatch(r'[\x00-\x7f]+',alias):
                pattern=r'(?<![A-Za-z0-9])'+pattern+r'(?![A-Za-z0-9])'
            if re.search(pattern,text,re.I):
                found.append(c.ticker)
                break
    return found

def register_sources(session):
    definitions=source_definitions(list(session.scalars(select(Company))))
    for d in definitions:
        row=session.get(Source,d['id'])
        if not row:
            row=Source(id=d['id'],status='not_run',new_count=0)
            session.add(row)
        row.name=d['name']; row.url=d['url']; row.data=dict(d, **{k:v for k,v in (row.data or {}).items() if k in ('fetch_meta','backfill_meta','backfill_completed_at','last_error_kind','last_http_status')})
        if d['adapter']=='manual': row.status='manual'
    session.commit()
    return definitions

def save_records(session,source_id,events,financials,companies):
    count=0
    source=session.get(Source,source_id)
    definition=source.data
    for data in events:
        data=normalize_dates(data,definition.get('adapter'))
        if data.get('ticker') and session.get(Company,data['ticker']) is None:
            raise ValueError('官方 issuer 無法對應地圖公司')
        data['mentioned']=mentioned_companies(data['title']+' '+data['body'],companies,data.get('ticker'))
        identity=None
        if data['kind'] in ('industry_news','official_stats'):
            provider=definition.get('provider',source_id)
            key='period:'+data['raw'].get('dataset',provider)+':'+data['period'] if data.get('period') else canonical_url(data['url'],provider)
            if data.get('period'):
                data['external_id']=key
            identity=hashlib.sha256((provider+':'+key).encode()).hexdigest()
        row=session.scalar(select(Event).where(Event.identity==identity)) if identity else session.scalar(select(Event).where(Event.source_id==source_id,Event.external_id==data['external_id']))
        if row:
            # Prefer a release with a real publication date over archive-only metadata.
            if not (row.published_at and data['raw'].get('metadata_only')):
                for key,value in data.items():
                    if key!='external_id': setattr(row,key,value)
            row.fetched_at=now()
            row.feeds=list(dict.fromkeys((row.feeds or [])+[source_id]))
        else:
            row=Event(source_id=source_id,identity=identity,feeds=[source_id],**data)
            session.add(row); count+=1
        session.flush()
        result=classify_event(session,row)
        if row.kind=='official_stats':
            from .models import EventSegment, EventTheme
            for model,field,scope in [(EventSegment,'segment_id','segments'),(EventTheme,'theme_id','themes')]:
                for key in definition.get(scope,[]):
                    if key not in result[scope]:
                        session.add(model(event_id=row.id,**{field:key},relevance='background',evidence=[{'term':'官方資料集範圍','matched':row.period or '未提供','excerpt':row.basis or row.body}]))
    for data in financials:
        data=dict(data)
        row=session.scalar(select(Financial).where(Financial.source_id==source_id,Financial.ticker==data['ticker'],Financial.period==data['period'],Financial.basis==data['basis']))
        if row:
            # Preserve previous version metadata when the official values actually changed.
            changed=any(getattr(row,k)!=data[k] for k in ('revenue','revenue_yoy','gross_margin','eps'))
            if changed:
                history=row.raw.get('previous_versions',[])[-4:]
                data['raw']=dict(data['raw'],previous_versions=history+[{'revenue':row.revenue,'revenue_yoy':row.revenue_yoy,'gross_margin':row.gross_margin,'eps':row.eps,'published_at':row.published_at.isoformat(),'raw':{k:v for k,v in row.raw.items() if k!='previous_versions'}}])
            elif row.raw.get('previous_versions'):
                data['raw']=dict(data['raw'],previous_versions=row.raw['previous_versions'])
            for key,value in data.items():
                setattr(row,key,value)
            row.fetched_at=now()
        else:
            session.add(Financial(source_id=source_id,**data)); count+=1
    session.flush()
    return count

def ingest_one(session,definition,http,companies,fetcher=fetch_source):
    sid=definition['id']; source=session.get(Source,sid)
    source.last_attempt=now(); source.new_count=0
    session.commit()
    try:
        tracked={c.ticker.split('.')[0]:c.ticker for c in companies if re.match(r'^\d{4}\.TW(O)?$',c.ticker)}
        events,financials=fetcher(definition,http,tracked)
        count=save_records(session,sid,events,financials,companies)
        warnings=list(dict.fromkeys(w for e in events for w in e['raw'].get('adapter_warnings',[])))
        source.status='partial' if warnings else 'success'
        source.error='；'.join(warnings)[:1200] if warnings else None
        source.data=dict(source.data,last_error_kind='partial' if warnings else None,last_http_status=None)
        source.last_success=now(); source.new_count=count
        meta=definition.get('_fetch_meta')
        if meta:
            source.data=dict(source.data,fetch_meta=meta)
            if definition.get('_backfill'):
                source.data=dict(source.data,backfill_meta=meta)
            if definition.get('_backfill') and not warnings:
                source.data=dict(source.data,backfill_completed_at=now().isoformat())
        session.commit()
    except Exception as exc:
        session.rollback()
        source=session.get(Source,sid)
        details=failure_details(exc)
        source.status='configuration_required' if details['last_error_kind']=='configuration' else 'failed'
        source.data=dict(source.data,**details)
        source.error=f'{type(exc).__name__}: {str(exc)}'[:1200]
        source.new_count=0
        session.commit()
    return {'status':source.status,'new_count':source.new_count,'error':source.error}

@contextmanager
def ingestion_lock(engine):
    if engine.dialect.name!='postgresql':
        # Tests only. Runtime always uses PostgreSQL.
        yield True
        return
    with engine.connect() as connection:
        acquired=bool(connection.scalar(text('SELECT pg_try_advisory_lock(729310181)')))
        try:
            yield acquired
        finally:
            if acquired:
                connection.execute(text('SELECT pg_advisory_unlock(729310181)'))

def run_ingestion(only=None,backfill_days=None):
    from .db import engine
    with ingestion_lock(engine) as acquired:
        if not acquired:
            return {'status':'skipped_overlap'}
        with Session() as session:
            definitions=register_sources(session)
            from .indicator_definitions import import_definitions
            from .financial_indicators import project_financials
            from .metric_ingest import ingest_metric_source
            import_definitions(session);session.commit()
            definitions=[d for d in definitions if d['adapter']!='manual']
            # Preserve serial old-source ingestion, then add metrics under the same lock.
            definitions.sort(key=lambda d:d['adapter'] in ('aaon-metrics','tsmc-metrics'))
            if only:
                definitions=[d for d in definitions if d['id'] in only]
                if not definitions:
                    raise ValueError('來源不存在；請先查詢 /api/sources')
            run=IngestionRun(results={}); session.add(run); session.commit()
            companies=list(session.scalars(select(Company)))
            http=OfficialHttp(); results={}
            try:
                for d in definitions:
                    source=session.get(Source,d['id'])
                    d['_backfill']=backfill_days is not None or not source.data.get('backfill_completed_at')
                    d['_backfill_days']=backfill_days or 90
                    d['_requested_backfill_days']=backfill_days
                    if d['adapter'] in ('aaon-metrics','tsmc-metrics'):
                        results[d['id']]=ingest_metric_source(session,d,http)
                    else:
                        results[d['id']]=ingest_one(session,d,http,companies)
                    print(json.dumps({'source':d['id'],**results[d['id']]},ensure_ascii=False),flush=True)
                try:
                    count=project_financials(session);session.commit()
                    results['financial-indicator-projection']={'status':'success','new_count':count,'error':None}
                except Exception as exc:
                    session.rollback()
                    results['financial-indicator-projection']={'status':'failed','new_count':0,'error':f'{type(exc).__name__}: {exc}'[:1200]}
                run.finished_at=now(); run.results=results; session.commit()
            finally:
                http.close()
            return results

def reclassify_events(only_stale=False):
    from .db import engine
    with ingestion_lock(engine) as acquired:
        if not acquired:
            return {'status':'skipped_overlap'}
        with Session() as session:
            register_sources(session)
            companies=list(session.scalars(select(Company)))
            query=select(Event)
            if only_stale: query=query.where(or_(Event.rules_version.is_(None),Event.rules_version!=rules()['version']))
            rows=list(session.scalars(query))
            for event in rows:
                fetched_at=event.fetched_at
                data={c.name:getattr(event,c.name) for c in Event.__table__.columns if c.name not in ('id','source_id','identity','feeds','routine','rules_version','mentioned','fetched_at')}
                if event.published_precision=='unknown' and event.date_semantics=='unknown':
                    data.pop('published_precision')
                save_records(session,event.source_id,[data],[],companies)
                event.fetched_at=fetched_at  # Reclassification did not contact the source.
            session.commit()
            return {'reclassified':len(rows),'total_events':session.query(Event).count()}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',action='append',help='只更新指定來源，可重複指定')
    parser.add_argument('--backfill-days',type=int,choices=range(1,366),metavar='1..365',help='強制嘗試來源可提供的歷史回補')
    parser.add_argument('--reclassify',action='store_true',help='正規化既有事件日期並重新分類，不呼叫外部來源')
    parser.add_argument('--only-stale',action='store_true',help='重分類只處理缺少分類或規則版本過期的事件，供初始化使用')
    args=parser.parse_args()
    if args.only_stale and not args.reclassify:
        parser.error('--only-stale 需搭配 --reclassify')
    if args.reclassify:
        print(json.dumps(reclassify_events(args.only_stale),ensure_ascii=False))
    else:
        print(json.dumps(run_ingestion(args.source,args.backfill_days),ensure_ascii=False))
