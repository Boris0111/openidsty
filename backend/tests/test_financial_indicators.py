from datetime import datetime,timezone
from decimal import Decimal
from sqlalchemy import select
from app.models import Company,Financial,IndicatorObservation,Theme,Indicator
from app.ingest import register_sources,save_records
from app.connectors import parse_tw,parse_sec_facts
from app.indicator_definitions import import_definitions
from app.financial_indicators import project_financials
from pathlib import Path


def test_proxy_projection_uses_existing_values_dates_zero_and_no_refetch(db):
    definitions=register_sources(db);import_definitions(db)
    companies=list(db.scalars(select(Company)))
    text=(Path(__file__).parent/'fixtures/tw-revenue.json').read_text(encoding='utf-8')
    events,financials=parse_tw(text,'revenue','https://official.test/revenue',{'2330':'2330.TW'})
    save_records(db,'twse-revenue',events,financials,companies)
    expected=dict(db.get(Theme,'advanced-node-2nm').data)
    db.add(Indicator(id='retired',name='未關聯的歷史指標',kind='proxy',unit='amount',frequency='quarterly',basis='quarterly',data={}))
    db.flush()
    assert project_financials(db)==1
    assert project_financials(db)==0
    row=db.scalar(select(IndicatorObservation))
    assert row.indicator_id=='tsmc-monthly-revenue' and row.value==Decimal('100000000')
    assert row.published_at is None and row.reported_at is not None
    assert row.currency=='TWD' and row.basis=='monthly' and row.raw_excerpt
    financial=db.scalar(select(Financial));financial.revenue=0;db.flush()
    assert project_financials(db)==1
    assert db.get(Theme,'advanced-node-2nm').data==expected
    assert db.get(Company,'VRT').cik=='0001674101'
    assert any(d['id']=='sec-facts-vrt' for d in definitions)


def test_exact_sec_quarter_not_ytd_or_calendar_guessed(db):
    register_sources(db);import_definitions(db)
    def metric(value,start,end):return {'val':value,'start':start,'end':end,'filed':'2026-06-24','accn':'0000723125-26-000001','form':'10-Q'}
    facts={'cik':723125,'facts':{'us-gaap':{'Revenues':{'units':{'USD':[metric(123,'2026-02-27','2026-05-28'),metric(500,'2025-08-29','2026-05-28')]}}}}}
    _,financials=parse_sec_facts(facts,'MU','https://official.test',reference=datetime(2026,10,14).date())
    save_records(db,'sec-facts-mu',[],financials,list(db.scalars(select(Company))))
    assert project_financials(db)==1
    row=db.scalar(select(IndicatorObservation))
    assert row.period_start.isoformat()=='2026-02-27' and row.period_end.isoformat()=='2026-05-28'
    assert row.original_period=='2026-02-27/2026-05-28' and row.basis=='quarterly'
    assert row.published_at is not None and row.reported_at is None
