from datetime import date,timedelta
from decimal import Decimal
from app.indicator_api import indicators_payload
from app.indicator_definitions import import_definitions
from app.ingest import register_sources
from app.models import Theme,Source
from app.observations import save_observation


def setup(db):
    register_sources(db);import_definitions(db);db.commit()


def add(db,end,value,**changes):
    row=dict(indicator_id='aaon-liquid-cooling-revenue',source_id='aaon-earnings-metrics',document_identity='quarter',dataset='sales',entity='AAON',original_period=str(end),period_start=end.replace(month=end.month-2,day=1),period_end=end,basis='quarterly',scope='BASX product',unit='amount',currency='USD',value=Decimal(value),published_precision='unknown',date_semantics='unknown',url='https://investors.aaon.com/quarter',raw_excerpt='real sales',raw={})
    row.update(changes);save_observation(db,row);db.commit()


def test_decimal_revision_stale_and_failed_http_are_independent(db,client):
    setup(db);add(db,date(2025,12,31),'0');add(db,date(2026,3,31),'123.45678901')
    add(db,date(2026,3,31),'234.56789012')
    source=db.get(Source,'aaon-earnings-metrics');source.status='failed';source.error='HTTP 403';db.commit()
    payload=indicators_payload(db,db.get(Theme,'liquid-cooling'),reference=date(2026,10,14))
    item=next(i for i in payload['indicators'] if i['kind']=='direct')
    assert item['status']=='stale' and item['latest']['value']=='234.56789012'
    assert item['latest']['revision']==2 and len(item['revisions'])==3
    assert item['source']['status']=='failed' and item['comparison']['reason'].startswith('前期為零')
    assert len(item['trend'])==2
    assert client.get('/api/themes/liquid-cooling/indicators?limit=1').status_code==200
    for query in ('limit=0','limit=37','limit=x'):assert client.get('/api/themes/liquid-cooling/indicators?'+query).status_code==422
    assert client.get('/api/themes/missing/indicators').status_code==404
    assert client.post('/api/themes/liquid-cooling/indicators').status_code==405


def test_percent_points_and_scope_currency_basis_do_not_mix(db):
    setup(db)
    for end,value in [(date(2026,3,31),'1'),(date(2026,6,30),'3')]:
        add(db,end,value,indicator_id='tsmc-2nm-wafer-revenue-share',source_id='tsmc-node-metrics',entity='2330.TW',scope='wafer revenue',unit='percent',currency=None)
    item=indicators_payload(db,db.get(Theme,'advanced-node-2nm'),reference=date(2026,10,14))['indicators'][0]
    assert item['comparison']['value']=='2' and item['comparison']['unit']=='percentage-point'
    add(db,date(2026,6,30),'4',indicator_id='tsmc-2nm-wafer-revenue-share',source_id='tsmc-node-metrics',entity='2330.TW',scope='different denominator',unit='percent',currency=None)
    item=indicators_payload(db,db.get(Theme,'advanced-node-2nm'))['indicators'][0]
    assert item['comparison']['value'] is None and len(item['trend'])==1
    add(db,date(2026,6,30),'4',indicator_id='tsmc-2nm-wafer-revenue-share',source_id='tsmc-node-metrics',entity='2330.TW',scope='different denominator',unit='amount',currency='TWD',basis='annual',valid=False,invalid_reason='修正為不可用年度數據')
    item=indicators_payload(db,db.get(Theme,'advanced-node-2nm'))['indicators'][0]
    assert item['latest']['period_end']==date(2026,3,31) and any('修正為不可用' in g for g in item['gaps'])


def test_monthly_age_threshold_and_missing_value(db):
    setup(db);theme=db.get(Theme,'800vdc')
    item=indicators_payload(db,theme)['indicators'][0]
    assert item['status']=='unavailable' and item['latest'] is None and item['comparison']['value'] is None
    add(db,date(2026,8,31),'100',indicator_id='delta-monthly-revenue',source_id='twse-revenue',entity='2308.TW',period_start=date(2026,8,1),basis='monthly',currency='TWD')
    assert indicators_payload(db,theme,reference=date(2026,10,30))['indicators'][0]['status']=='available'
    assert indicators_payload(db,theme,reference=date(2026,10,31))['indicators'][0]['status']=='stale'
