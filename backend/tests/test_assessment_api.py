from datetime import datetime, timezone
from sqlalchemy import select
from app.models import Theme, Company, Event, EventTheme, Source
from app.ingest import register_sources, save_records
from app.industry_connectors import record


def test_read_only_assessment_preserves_old_fields_and_source_warning(client, db):
    register_sources(db)
    original = dict(db.get(Theme, 'hbm4').data)
    response = client.get('/api/themes/hbm4/assessment')
    assert response.status_code == 200
    data = response.json()
    assert data['available'] and data['checked'] == data['assessment']['reviewed'] == '2026-10-07'
    assert data['evidence_sources']['micron-hbm4-remarks']['name']
    assert any(w['kind'] == 'unverified' for w in data['source_warnings'])
    assert all(p['confidence'] == 'inference' for p in data['assessment']['paths'])
    assert db.get(Theme, 'hbm4').data == original
    legacy = client.get('/api/themes/hbm4').json()
    assert {'prose', 'checked', 'milestones', 'events', 'status'} <= legacy.keys()
    assert legacy['assessment_summary']['available']
    assert client.get('/api/themes/missing/assessment').status_code == 404
    assert client.post('/api/themes/hbm4/assessment', json={}).status_code == 405


def test_missing_assessment_is_explicit_and_research_remains_readable(client, db):
    theme = db.get(Theme, 'hbm4')
    theme.data = {k: v for k, v in theme.data.items() if k != 'assessment'}; db.commit()
    data = client.get('/api/themes/hbm4/assessment').json()
    assert data['available'] is False and data['assessment'] is None
    assert data['checked'] == '2026-10-07'
    assert 'https://' in client.get('/api/themes/hbm4').json()['prose']
    coverage = client.get('/api/coverage').json()
    theme_row = next(r for r in coverage['rows'] if r['id'] == 'hbm4')
    segment_row = next(r for r in coverage['rows'] if r['kind'] == 'segment')
    assert theme_row['assessment_available'] is False and theme_row['research_available']
    assert segment_row['assessment_available'] is None and segment_row['indicator_gaps'] == []
    assert theme_row['indicator_count'] == 0 and theme_row['indicator_gaps']
    report = client.get('/api/coverage/report').text
    assert '題材判讀與指標覆蓋' in report and '直接 30／90 日' in report


def test_candidates_require_direct_nonroutine_published_and_taipei_date(client, db, monkeypatch):
    import app.assessments as assessments
    reference = datetime(2026, 10, 14, tzinfo=timezone.utc)
    monkeypatch.setattr(assessments, 'now', lambda: reference)
    register_sources(db); companies = list(db.scalars(select(Company)))
    def article(slug, published, title='液冷冷板新規格', lifecycle='published'):
        return dict(record(title, '液冷產品', f'https://technews.tw/{slug}/', published, 'minute' if published else 'unknown'), lifecycle=lifecycle)
    items = [
        article('same-day', datetime(2026, 10, 7, 15, 59, tzinfo=timezone.utc)),
        article('next-taipei-day', datetime(2026, 10, 7, 16, 1, tzinfo=timezone.utc)),
        article('unknown', None),
        article('routine', datetime(2026, 10, 9, tzinfo=timezone.utc), '液冷月營收'),
        article('preview', datetime(2026, 10, 10, tzinfo=timezone.utc), lifecycle='preview'),
        article('future', datetime(2026, 11, 10, tzinfo=timezone.utc)),
    ]
    save_records(db, 'technews-components', items, [], companies)
    # Even an erroneous routine/background link cannot become candidate evidence.
    routine = db.scalar(select(Event).where(Event.url.endswith('/routine/')))
    db.add(EventTheme(event_id=routine.id, theme_id='liquid-cooling', relevance='direct', evidence=[]))
    background = article('background', datetime(2026, 10, 9, tzinfo=timezone.utc))
    background['kind'] = 'official_stats'
    save_records(db, 'technews-components', [background], [], companies); db.commit()
    data = client.get('/api/themes/liquid-cooling/assessment').json()
    assert [e['url'] for e in data['candidates']] == ['https://technews.tw/next-taipei-day/']
    assert data['candidate_count'] == 1 and data['unknown_date_count'] == 1
    assert data['undated_candidates'][0]['published_at'] is None
    assert data['assessment']['reviewed'] == '2026-10-07'
