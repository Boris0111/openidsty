import json
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
import pytest
from sqlalchemy import select, func
from app.models import Company, Event, EventSegment, EventTheme, Source, Segment, Theme
from app.classify import classify, rules
from app.registry import source_definitions
from app.industry_connectors import parse_rss, parse_technews_list, parse_tpca_list, parse_tpca_detail, parse_moea, parse_census, parse_eia, parse_census_archive, fetch_industry, record
from app.ingest import register_sources, save_records, ingest_one
from app.research_api import coverage
from app.event_dates import normalize_dates

F=Path(__file__).parent/'fixtures/industry'
CORPUS=json.loads((F/'classification-corpus.json').read_text(encoding='utf8'))
def fixture(name): return (F/name).read_text(encoding='utf8')

@pytest.mark.parametrize('sample',CORPUS,ids=[s['title'][:24] for s in CORPUS])
def test_real_article_classification(sample):
    result=classify(sample['title'],sample['body'],sample['kind'])
    if sample['negative']:
        assert result['segments']=={} and result['themes']=={}
    else:
        assert set(sample['segments'])<=result['segments'].keys()
        assert set(sample['themes'])<=result['themes'].keys()
        assert all(hit['term'] and hit['excerpt'] for group in ('segments','themes') for matches in result[group].values() for hit in matches['evidence'])

def test_corpus_covers_all_segments_and_themes(db):
    assert {key for s in CORPUS for key in s['segments']}==set(db.scalars(select(Segment.id)))
    assert {key for s in CORPUS for key in s['themes']}==set(db.scalars(select(Theme.id)))
    definitions=source_definitions(list(db.scalars(select(Company))))
    auto=[s for s in definitions if s['adapter']!='manual']
    assert set(db.scalars(select(Segment.id)))<=set(key for s in auto for key in s.get('segments',[]))
    assert set(db.scalars(select(Theme.id)))<=set(key for s in auto for key in s.get('themes',[]))

@pytest.mark.parametrize('title,body',[
    ('AMD與台積電更新合作名單','僅公司名稱，沒有技術或產品內容'),
    ('AMDOCS supplies software','the BHBM4X package has metadata and an update'),
    ('記憶體壓縮軟體更新','Linux uses DRAM for CRAM and swap'),
    ('NVIDIA 月營收公告','GPU HBM4 ASIC 800VDC 晶圓代工'),
    ('ATE dinner is served','the theatre is open'),
    ('2nm coating for a bottle','a thin film experiment'),
    ('全市供電瓶頸','電網維修，沒有資料中心或 AI 需求'),
])
def test_false_hits_and_context_exclusion(title,body):
    result=classify(title,body,'industry_news')
    if title.startswith('2nm'): assert not result['themes']
    elif title.startswith('全市'): assert 'power-bottleneck' not in result['themes']
    else: assert not result['segments'] and not result['themes']

def test_real_adapters_and_empty_shells():
    rss=parse_rss(fixture('tech-components.xml'),'https://technews.tw/category/component/feed/')
    assert rss and rss[0]['published_at'].tzinfo and rss[0]['ticker'] is None
    tpca=parse_tpca_list(fixture('tpca.html'),'https://www.tpca.org.tw/web/list_news.php?menu_no=182&mod_no=5')
    assert tpca[0]['published_precision']=='day'
    assert 'ABF' in parse_tpca_detail(fixture('tpca-detail.html'))
    moea=parse_moea(fixture('moea-detail.html'),'https://www.moea.gov.tw/test')
    assert moea['period']=='2026-08' and moea['published_at'].day==23
    census=parse_census(fixture('census-current.html'),'https://www.census.gov/test')
    assert census['period']=='2026-08' and census['published_at'].date()==date(2026,10,2)
    archive=parse_census_archive(fixture('census-history.html'),'https://www.census.gov/test',date(2026,10,8))
    assert archive and all(e['published_at'] is None and e['raw']['metadata_only'] for e in archive)
    eia=parse_eia(fixture('eia.html'),'https://www.eia.gov/test')
    assert eia['period']=='2026-07' and eia['published_at'].date()==date(2026,9,24)
    for parser in (parse_moea,parse_census,parse_eia,parse_tpca_list):
        with pytest.raises(ValueError): parser('<html><script>app()</script></html>','https://example.org')

def test_semantic_dates_preserve_unknown_and_day_precision():
    dt=datetime(2026,10,7,tzinfo=timezone.utc)
    data={'published_at':dt,'raw':{'出表日期':'1151007'},'kind':'financials','external_id':'2330.TW:2026-Q2:ytd'}
    result=normalize_dates(data,'tw')
    assert result['published_at'] is None and result['reported_at']==dt
    assert result['period']=='2026-Q2'
    assert normalize_dates({'published_at':dt,'raw':{},'kind':'earnings_call'},'tsmc')['activity_at']==dt
    assert normalize_dates({'published_at':dt,'raw':{},'kind':'filing'},'sec-submissions')['published_precision']=='day'
    assert normalize_dates({'published_at':dt,'raw':{}},'unknown')['published_at'] is None

def test_cross_feed_dedup_and_statistics_periods(db):
    register_sources(db); companies=list(db.scalars(select(Company)))
    event=record('液冷冷板產品公布','AI 資料中心使用液冷','https://technews.tw/2026/10/07/cooling/?utm_source=x',datetime.now(timezone.utc),'day')
    assert save_records(db,'technews-server',[event],[],companies)==1
    same=dict(event,url='https://technews.tw/2026/10/07/cooling/#readmore',external_id='another-feed-guid')
    assert save_records(db,'technews-components',[same],[],companies)==0
    db.commit()
    assert db.scalar(select(func.count()).select_from(Event))==1
    assert set(db.scalar(select(Event)).feeds)=={'technews-server','technews-components'}
    stat=parse_eia(fixture('eia.html'),'https://www.eia.gov/electricity/monthly/')
    assert save_records(db,'eia-monthly',[stat],[],companies)==1
    assert save_records(db,'eia-monthly',[dict(stat,body='本期修訂',url='https://www.eia.gov/new-url')],[],companies)==0
    assert save_records(db,'eia-monthly',[dict(stat,period='2026-08')],[],companies)==1
    db.commit()
    assert all(link.relevance=='background' for link in db.scalars(select(EventSegment).where(EventSegment.event_id!=1)))

def test_backfill_bounds_unknown_dates_and_partial_failure():
    class Reply:
        text=fixture('tech-components.xml');url='https://technews.tw/category/component/feed/'
    class Http:
        def get(self,url):
            if 'paged=2' in url or '/page/2/' in url: raise ValueError('page 2 timeout')
            return Reply()
    d={'adapter':'rss','url':Reply.url,'provider':'technews','max_pages':3,'paged':True,'_backfill':True}
    output,_=fetch_industry(d,Http())
    assert output and output[0]['raw']['adapter_warnings']==['page 2 timeout']
    assert d['_fetch_meta']['pages']==1 and d['_fetch_meta']['requested_days']==90

def test_technews_public_listing_dates_and_bounded_backfill():
    rows=parse_technews_list(fixture('technews-category.html'),'https://technews.tw/category/semiconductor/page/2/')
    assert rows and rows[0]['published_at'].utcoffset()==timedelta(hours=8)
    assert rows[0]['published_at'].hour==10 and rows[0]['published_precision']=='minute'
    assert rows[0]['body'] and '繼續閱讀' not in rows[0]['body']
    class Reply:
        def __init__(self,text,url): self.text,self.url=text,url
    requested=[]
    class Http:
        def get(self,url):
            requested.append(url)
            return Reply(fixture('technews-category.html') if '/page/2/' in url else fixture('tech-semiconductor.xml'),url)
    definition={'adapter':'rss','provider':'technews','url':'https://technews.tw/category/semiconductor/feed/','max_pages':2,'paged':True,'_backfill':True}
    output,_=fetch_industry(definition,Http())
    assert requested[1].endswith('/category/semiconductor/page/2/')
    assert any('回補上限' in warning for warning in definition['_fetch_meta']['warnings'])
    assert output and output[0]['raw']['adapter_warnings']

def test_overlapping_articles_do_not_end_distinct_listing_pages():
    from unittest.mock import patch
    now=datetime.now(timezone.utc)
    recent=record('HBM4 new memory','chip','https://technews.tw/recent',now,'minute')
    older=record('HBM4 memory update','chip','https://technews.tw/older',now-timedelta(days=10),'day')
    oldest=record('HBM4 memory demand','chip','https://technews.tw/oldest',now-timedelta(days=91),'day')
    class Reply:
        def __init__(self,url): self.url,self.text=url,''
    class Http:
        def get(self,url):return Reply(url)
    definition={'adapter':'rss','provider':'technews','url':'https://technews.tw/category/semiconductor/feed/','max_pages':4,'paged':True,'_backfill':True}
    with patch('app.industry_connectors.parse_rss',return_value=[recent,older]),patch('app.industry_connectors.parse_technews_list',side_effect=[[older],[oldest]]):
        output,_=fetch_industry(definition,Http())
    assert len(output)==2 and definition['_fetch_meta']['pages']==3
    assert definition['_fetch_meta']['cutoff_reached'] and definition['_fetch_meta']['warnings']==[]

def test_source_metadata_survives_register_and_failure(db):
    definitions=register_sources(db); companies=list(db.scalars(select(Company)))
    d=next(d for d in definitions if d['id']=='technews-components'); d['_backfill']=True
    def good(definition,*args):
        definition['_fetch_meta']={'requested_days':90,'pages':1}
        return [record('液冷冷板','真實樣本','https://technews.tw/sample/',datetime.now(timezone.utc),'day')],[]
    ingest_one(db,d,None,companies,good)
    register_sources(db)
    assert db.get(Source,d['id']).data['fetch_meta']['requested_days']==90
    def bad(*args):raise ValueError('format changed')
    assert ingest_one(db,d,None,companies,bad)['status']=='failed'
    assert db.get(Source,d['id']).last_success
    assert db.scalar(select(func.count()).select_from(Event))==1

def test_reclassification_preserves_acquisition_time_and_skips_current_rules(db,monkeypatch):
    import app.ingest as ingestion
    register_sources(db); companies=list(db.scalars(select(Company)))
    save_records(db,'technews-components',[record('液冷冷板新設計','AI server','https://technews.tw/time/',datetime.now(timezone.utc),'day')],[],companies)
    event=db.scalar(select(Event));event.rules_version='older-rules'
    fetched=datetime(2026,1,2,3,4);event.fetched_at=fetched;db.commit()
    monkeypatch.setattr(ingestion,'Session',lambda:db)
    assert ingestion.reclassify_events(only_stale=True)['reclassified']==1
    assert db.get(Event,event.id).fetched_at.replace(tzinfo=None)==fetched
    assert db.get(Event,event.id).rules_version==rules()['version']
    assert ingestion.reclassify_events(only_stale=True)['reclassified']==0
    assert ingestion.reclassify_events()['reclassified']==1
    assert db.get(Event,event.id).fetched_at.replace(tzinfo=None)==fetched

def test_readonly_api_filters_coverage_and_direct_impact(client,db):
    register_sources(db); companies=list(db.scalars(select(Company)))
    now=datetime.now(timezone.utc)
    direct=record('液冷冷板設備新規格','台積電的另一個角色不代表直接影響','https://technews.tw/direct/',now,'day')
    unknown=record('HBM4 技術','新記憶體','https://technews.tw/unknown/')
    routine=record('輝達月營收','GPU','https://technews.tw/routine/',now,'day')
    bg=record('資料中心電力需求統計','政府背景資料','https://www.eia.gov/bg/',now,'day','official_stats',period='2026-08',basis='美國總體電力')
    save_records(db,'technews-components',[direct,unknown,routine],[],companies)
    save_records(db,'eia-monthly',[bg],[],companies); db.commit()
    direct_row=db.scalar(select(Event).where(Event.url==direct['url']))
    detail=client.get(f'/api/events/{direct_row.id}').json()
    assert detail['ticker'] is None
    assert detail['impact']['seeds']==['thermal']
    assert 'foundry' not in detail['impact']['seeds']
    assert any(p['segment']=='pcb' and p['mechanism']=='sibling' for p in detail['impact']['paths'])
    thermal=client.get('/api/events?segment=thermal').json()
    assert [e['id'] for e in thermal]==[direct_row.id]
    assert client.get('/api/events?theme=hbm4').json()[0]['published_at'] is None
    assert len(client.get('/api/events?include_routine=true').json())==3
    assert len(client.get('/api/events').json())==2
    assert len(client.get('/api/events?relevance=background').json())==1
    assert len(client.get('/api/events?relevance=all&include_routine=true').json())==4
    assert len(client.get('/api/events?date_from='+now.date().isoformat()).json())==1
    assert client.get('/api/events?date_from=2026-10-08&date_to=2026-10-07').status_code==422
    assert client.get('/api/events?industry=unknown').status_code==422
    assert client.get('/api/events?relevance=unknown').status_code==422
    assert len(client.get('/api/themes').json())==7
    assert len(client.get('/api/segments').json())==17
    assert all(s['layer']=='semiconductor' for s in client.get('/api/segments?industry=semiconductor').json())
    assert client.get('/api/segments?industry=unknown').status_code==422
    assert 'https://' in client.get('/api/themes/liquid-cooling').json()['prose']
    assert {r['kind'] for r in client.get('/api/search?q=液冷').json()}=={'theme'}
    assert client.get('/api/search?q=臺積電').json()[0]['id']=='2330.TW'
    assert client.get('/api/search?q=thermal').json()[0]['kind']=='segment'
    data=client.get('/api/coverage').json(); assert len(data['rows'])==24
    thermal=next(r for r in data['rows'] if r['id']=='thermal')
    assert thermal['direct_90d']==1
    assert next(r for r in data['rows'] if r['id']=='hbm4')['unknown_date']==1
    assert next(r for r in data['rows'] if r['id']=='datacenter')['direct_90d']==0
    assert '近 90 日' in client.get('/api/coverage/report').text
    assert client.get('/api/compare?tickers=NVDA,AMD').status_code==200
