from datetime import datetime,timezone,date,timedelta
from sqlalchemy import select
from app.models import Event,EventTheme,Company,Theme
from app.ingest import register_sources
from app.assessments import candidate_events
from app.theme_updates import updates_payload
from app.indicator_definitions import import_definitions
from test_indicator_api import add

def test_complete_candidate_counts_bounded_samples_and_tokens(client,db,monkeypatch):
    import app.assessments as assessment
    reference=datetime(2026,10,16,tzinfo=timezone.utc);monkeypatch.setattr(assessment,'now',lambda:reference)
    register_sources(db)
    for n in range(14):
        event=Event(source_id='aaon-earnings-metrics',external_id=f'bounded-{n}',title=f'液冷資訊 {n}',body='候選數量與完整 token 集合測試',kind='industry_news',lifecycle='published',published_at=reference-timedelta(days=1) if n<12 else None,url=f'https://example.org/{n}',mentioned=[],raw={})
        db.add(event);db.flush();db.add(EventTheme(event_id=event.id,theme_id='liquid-cooling',relevance='direct',evidence=[]))
    db.commit()
    payload=client.get('/api/themes/liquid-cooling/assessment').json();assert payload['candidate_count']==12 and len(payload['candidates'])==8 and payload['unknown_date_count']==2
    assert all(event['source_name'] for event in payload['candidates'])
    first=updates_payload(db,['liquid-cooling'])['items'][0]
    sampled={e['id'] for e in payload['candidates']};event=db.scalar(select(Event).where(Event.id.not_in(sampled),Event.published_at.is_not(None)))
    event.body='未出現在八筆樣本中的實質修訂';db.commit()
    assert updates_payload(db,['liquid-cooling'])['items'][0]['candidate_token']!=first['candidate_token']

def test_revisions_are_paginated_and_invalid_latest_never_restores_old_value(client,db):
    register_sources(db);import_definitions(db);db.commit()
    for value in range(25):add(db,date(2026,6,30),str(value))
    add(db,date(2026,6,30),'24',valid=False,invalid_reason='更正為不適用')
    data=client.get('/api/themes/liquid-cooling/indicators').json()['indicators'][0]
    assert data['latest'] is None and data['observations'][0]['revision']==26 and not data['observations'][0]['valid']
    assert data['revisions_total']==26 and len(data['revisions'])==20
    tail=client.get('/api/themes/liquid-cooling/indicators/aaon-liquid-cooling-revenue/revisions?offset=20&limit=20').json()
    assert tail['total']==26 and len(tail['items'])==6
    assert client.get('/api/themes/hbm4/indicators/aaon-liquid-cooling-revenue/revisions').status_code==404
