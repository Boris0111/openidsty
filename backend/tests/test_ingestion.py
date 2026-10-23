from datetime import date, datetime, timezone
from pathlib import Path
from sqlalchemy import select, func
import pytest
from app.config import ROOT
from app.models import Company, Event, Financial, Source
from app.connectors import parse_tw, parse_sec_facts, parse_sec_submissions, parse_delta, parse_tsmc, parse_nvidia_rss, parse_microsoft, official_page_links
from app.ingest import register_sources, ingest_one, save_records, mentioned_companies

FIXTURES=Path(__file__).parent/'fixtures'
def fixture(name):
    return (FIXTURES/name).read_text(encoding='utf-8')

def test_tw_json_csv_basis_zero_and_shell():
    events,financials=parse_tw(fixture('tw-revenue.json'),'revenue','https://official.test/revenue',{'2330':'2330.TW'})
    assert financials[0]['revenue']==100_000_000
    assert financials[0]['basis']=='monthly'
    assert financials[0]['gross_margin'] is None and financials[0]['eps'] is None
    assert events[0]['kind']=='financials' and events[0]['title'].endswith('月營收')
    # Quarterly statements were removed with company financials; only revenue remains.
    with pytest.raises(ValueError,match='公司財報已移除'):
        parse_tw(fixture('tpex-financial.csv'),'financials','https://official.test/fin',{'6488':'6488.TWO'})
    with pytest.raises(ValueError,match='外殼'):
        parse_tw('<html><div id="root"></div></html>','revenue','https://test',{})

def test_ir_content_preview_and_shell():
    ref=date(2026,10,8)
    assert parse_delta(fixture('delta.html'),'https://delta.test',ref)[0][0]['lifecycle']=='published'
    assert parse_tsmc(fixture('tsmc-preview.html'),'https://tsmc.test',ref)[0][0]['lifecycle']=='preview'
    nvidia=parse_nvidia_rss(fixture('nvidia.xml'),'https://nvidia.test',ref)[0]
    assert [r['lifecycle'] for r in nvidia]==['published','preview']
    assert 'Microsoft' in parse_microsoft(fixture('microsoft.html'),'https://microsoft.test',ref)[0][0]['body']
    for parser in (parse_delta,parse_tsmc,parse_microsoft):
        with pytest.raises(ValueError):
            parser('<html><script>hydrate()</script></html>','https://test',ref)

def test_aliases_chinese_and_ascii_boundaries(db):
    companies=list(db.scalars(select(Company)))
    assert set(mentioned_companies('台積電與臺積電、NVIDIA合作；AMD提供晶片',companies,'2308.TW'))>={'2330.TW','NVDA','AMD'}
    assert 'AMD' not in mentioned_companies('AMDOCS提供軟體',companies,'NVDA')
    assert 'NVDA' not in mentioned_companies('NVIDIA是發行主體',companies,'NVDA')

def test_idempotence_source_isolation_and_primary_issuer(db):
    defs=register_sources(db); companies=list(db.scalars(select(Company)))
    good=next(d for d in defs if d['id']=='twse-revenue')
    bad=next(d for d in defs if d['id']=='tpex-revenue')
    def fetch_good(*args):
        return parse_tw(fixture('tw-revenue.json'),'revenue','https://official.test',{'2330':'2330.TW'})
    assert ingest_one(db,good,None,companies,fetch_good)['new_count']==2
    assert ingest_one(db,good,None,companies,fetch_good)['new_count']==0
    original_success=db.get(Source,good['id']).last_success
    def fail(*args):
        raise ValueError('逾時')
    assert ingest_one(db,bad,None,companies,fail)['status']=='failed'
    assert db.get(Source,good['id']).last_success==original_success
    assert db.scalar(select(func.count()).select_from(Event))==1
    assert db.scalar(select(func.count()).select_from(Financial))==1
    e=db.scalar(select(Event)); assert e.ticker=='2330.TW'
    # Cross-source titles are not silently merged.
    assert ingest_one(db,bad,None,companies,fetch_good)['new_count']==2

def test_failure_preserves_history_and_nulls(db):
    defs=register_sources(db); d=next(d for d in defs if d['id']=='twse-revenue'); companies=list(db.scalars(select(Company)))
    revenue=fixture('tw-revenue.json').replace('"20.5"','""')
    def fetch(*args):return parse_tw(revenue,'revenue','https://official.test',{'2330':'2330.TW'})
    ingest_one(db,d,None,companies,fetch)
    f=db.scalar(select(Financial)); assert f.revenue_yoy is None
    def changed(*args):return parse_tw(revenue.replace('100,000','200,000'),'revenue','https://official.test',{'2330':'2330.TW'})
    ingest_one(db,d,None,companies,changed)
    assert f.raw['previous_versions'][0]['revenue']==100_000_000
    assert db.scalar(select(func.count()).select_from(Financial))==1
    def fail(*args):raise ValueError('格式改變')
    ingest_one(db,d,None,companies,fail)
    assert db.get(Source,d['id']).last_success is not None
    assert db.scalar(select(func.count()).select_from(Financial))==1

def test_sec_exact_ranges_and_restated_values():
    def r(value,start,end,acc='0000000000-26-000001'):
        return {'val':value,'start':start,'end':end,'filed':'2026-08-01','accn':acc,'form':'10-Q'}
    facts={'cik':1045810,'facts':{'us-gaap':{
        'Revenues':{'units':{'USD':[r(200,'2026-04-01','2026-06-30'),r(100,'2025-04-01','2025-06-30'),r(350,'2026-01-01','2026-06-30')]}},
        'GrossProfit':{'units':{'USD':[r(150,'2026-04-01','2026-06-30')]}},
        'EarningsPerShareDiluted':{'units':{'USD/shares':[r(2,'2026-04-01','2026-06-30','DIFFERENT-ACCESSION')]}}
    }}}
    records=parse_sec_facts(facts,'NVDA','https://sec.test',date(2026,10,8))[1]
    quarter=next(f for f in records if f['period']=='2026-04-01/2026-06-30')
    assert quarter['revenue_yoy']==100
    assert any(f['basis']=='ytd' for f in records)
    # Gross profit and EPS are ignored: only revenue feeds theme proxy indicators.
    assert all(f['gross_margin'] is None and f['eps'] is None for f in records)
    # The EPS-only accession no longer produces its own record for the same quarter.
    assert len([f for f in records if f['period']=='2026-04-01/2026-06-30'])==1

def test_sec_submissions_date_and_issuer():
    payload={'cik':1045810,'name':'NVIDIA','filings':{'recent':{'form':['8-K','4'],'filingDate':['2026-10-07','2026-10-07'],'accessionNumber':['0001045810-26-000001','0002'],'primaryDocument':['announcement.htm','insider.xml']}}}
    events,_=parse_sec_submissions(payload,'NVDA','https://sec.test',date(2026,10,8))
    assert len(events)==1 and events[0]['ticker']=='NVDA'
    assert '000104581026000001/announcement.htm' in events[0]['url']

def test_ir_navigation_ignores_mailto_queries_and_external_hosts():
    url='https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast'
    html=f'<a href="/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast">Quarter</a><a href="mailto:?body={url.replace("2026-q4","2027-q1")}">Share</a><a href="https://example.com/en-us/investor/earnings/fy-2028-q1/press-release-webcast">External</a><a href="/?body={url}">Share URL</a>'
    assert official_page_links(html,url,'www.microsoft.com',r'/en-us/investor/earnings/fy-\d{4}-q[1-4]/press-release-webcast/?')=={url}
