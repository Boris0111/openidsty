from datetime import date,datetime,timezone,timedelta
from sqlalchemy import select
from app.models import Theme,Source,Event,EventTheme,ThemeAssessmentVersion
from app.ingest import register_sources
from app.indicator_definitions import import_definitions
from app.theme_updates import updates_payload
from test_indicator_api import add


def snapshot(db):return updates_payload(db,['liquid-cooling'])['items'][0]


def test_tokens_ignore_http_and_fetched_but_capture_revisions_and_unknown_content(db,client):
    register_sources(db);import_definitions(db);db.commit()
    first=snapshot(db)
    source=db.get(Source,'aaon-earnings-metrics');source.status='failed';source.error='HTTP 403';source.last_attempt=datetime.now(timezone.utc);db.commit()
    assert snapshot(db)['indicator_token']==first['indicator_token'] and snapshot(db)['candidate_token']==first['candidate_token']
    add(db,date(2026,6,30),'1');second=snapshot(db)
    assert second['indicator_token']!=first['indicator_token'] and second['current_version_id']==first['current_version_id']
    add(db,date(2026,6,30),'1',fetched_at=datetime.now(timezone.utc)+timedelta(days=1))
    assert snapshot(db)['indicator_token']==second['indicator_token']
    add(db,date(2026,6,30),'2');assert snapshot(db)['indicator_token']!=second['indicator_token']
    event=Event(source_id='aaon-earnings-metrics',identity='new-unknown',external_id='unknown',title='液冷新收錄',body='發布日未知',kind='industry_news',lifecycle='published',published_at=None,url='https://example.org/event',mentioned=[],raw={});db.add(event);db.flush();db.add(EventTheme(event_id=event.id,theme_id='liquid-cooling',relevance='direct',evidence=[]));db.commit()
    third=snapshot(db);assert third['candidate_token']!=second['candidate_token'] and third['unknown_date_count']==1
    event.fetched_at=datetime.now(timezone.utc)+timedelta(days=1);db.commit();assert snapshot(db)['candidate_token']==third['candidate_token']
    event.body='內容修訂';db.commit();assert snapshot(db)['candidate_token']!=third['candidate_token']
    assert '不代表新發生' in third['pending_summary']
    assert client.post('/api/theme-updates').status_code==405


def test_unique_limit_and_unavailable_per_item(db,client):
    db.get(Theme,'hbm4').active=False;db.commit()
    data=client.get('/api/theme-updates?ids=liquid-cooling,missing,hbm4,liquid-cooling').json()['items']
    assert len(data)==3 and data[0]['available'] and not data[1]['available'] and not data[2]['available']
    assert client.get('/api/theme-updates?ids='+','.join('missing'+str(n) for n in range(21))).status_code==422
    assert client.get('/api/theme-updates?ids=').json()=={'items':[]}


def test_authored_version_changes_only_version_not_dynamic_tokens(db):
    import copy
    from app.assessment_versions import prepare_version
    first=snapshot(db);theme=db.get(Theme,'liquid-cooling');changed=copy.deepcopy(theme.data)
    changed['assessment']['summary']='重新核對成立條件';changed['assessment']['change_reason']='研究修訂'
    version=prepare_version(db,theme.id,changed,theme.checked);db.add(version);theme.data=changed;db.commit()
    second=snapshot(db)
    assert second['current_version_id']!=first['current_version_id']
    assert second['indicator_token']==first['indicator_token'] and second['candidate_token']==first['candidate_token']
