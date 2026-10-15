from datetime import date,datetime,timezone
from decimal import Decimal
from sqlalchemy import select,func
import pytest
from app.models import Company,Source,IndicatorObservation,Event,Financial,Theme
from app.ingest import register_sources,ingest_one,ingestion_lock
from app.indicator_definitions import import_definitions
from app.metric_ingest import ingest_metric_source
from app.metric_connectors import parse_aaon,fetch_aaon
from pathlib import Path


def test_metric_failure_isolation_history_and_unchanged_research(db):
    definitions=register_sources(db);import_definitions(db);db.commit()
    metric=next(d for d in definitions if d['id']=='aaon-earnings-metrics');metric['_backfill']=True
    original=dict(db.get(Theme,'liquid-cooling').data)
    html=(Path(__file__).parent/'fixtures/metrics/aaon-q1-2026.html').read_text(encoding='utf-8')
    def good(d,http):
        d['_fetch_meta']={'requested_days':730,'pages':1,'warnings':['部分歷史欄位未揭露']}
        return parse_aaon(html,'https://investors.aaon.com/investor-news/quarter')
    assert ingest_metric_source(db,metric,None,good)['new_count']==1
    assert ingest_metric_source(db,metric,None,good)['new_count']==0
    source=db.get(Source,metric['id']);last_success=source.last_success
    assert source.status=='partial' and source.data['backfill_completed_at']
    def bad(*args):raise ValueError('官方格式已變動')
    assert ingest_metric_source(db,metric,None,bad)['status']=='failed'
    assert source.last_success==last_success and db.query(IndicatorObservation).count()==1
    news=next(d for d in definitions if d['id']=='technews-components')
    from app.industry_connectors import record
    def success(*args):return [record('液冷冷板新規格','新事件','https://technews.tw/isolated/',datetime.now(timezone.utc),'day')],[]
    assert ingest_one(db,news,None,list(db.scalars(select(Company))),success)['status']=='success'
    assert db.query(Event).count()==1 and db.get(Theme,'liquid-cooling').data==original


def test_metric_empty_http_content_is_failure_not_fake_success(db):
    definitions=register_sources(db);import_definitions(db);db.commit()
    metric=next(d for d in definitions if d['id']=='aaon-earnings-metrics')
    assert ingest_metric_source(db,metric,None,lambda *args:[])['status']=='failed'
    assert db.query(IndicatorObservation).count()==0


def test_bounded_aaon_discovery_latest_checks_and_partial_parse():
    urls=[f'https://investors.aaon.com/investor-news/aaon-reports-{quarter}-quarter-2026-results' for quarter in ('second','first')]
    index=''.join(f'<a href="{url}">quarter</a>' for url in urls)
    html=(Path(__file__).parent/'fixtures/metrics/aaon-q1-2026.html').read_text(encoding='utf-8')
    class Reply:
        def __init__(self,text,url):self.text,self.url=text,url
    requested=[]
    class Http:
        def get(self,url):
            requested.append(url)
            if url in urls:return Reply(html if url==urls[1] else '<article>no disclosure</article>',url)
            return Reply(index,url)
    definition={'url':'https://investors.aaon.com/investor-news','_backfill':True,'max_pages':5,'max_reports':8,'history_days':730}
    rows=fetch_aaon(definition,Http(),date(2026,10,14))
    assert rows and definition['_fetch_meta']['warnings']
    assert len(requested)<=5+8
    definition['_backfill']=False;requested.clear()
    rows=fetch_aaon(definition,Http(),date(2026,10,14))
    # Old data remains readable; the API labels its age independently of HTTP health.
    assert rows[0]['period_end']==date(2026,3,31)
    assert len(requested)<=3


def test_pg_overlap_lock_releases_and_second_attempt_is_blocked():
    class Connection:
        def __init__(self):self.calls=[]
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def scalar(self,statement):self.calls.append(str(statement));return False
        def execute(self,statement):self.calls.append(str(statement))
    class Engine:
        dialect=type('Dialect',(),{'name':'postgresql'})()
        def __init__(self):self.connection=Connection()
        def connect(self):return self.connection
    engine=Engine()
    with ingestion_lock(engine) as acquired:assert acquired is False
    assert len(engine.connection.calls)==1 and 'pg_try_advisory_lock' in engine.connection.calls[0]
