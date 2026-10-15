from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.models import Company, Source
from app.ingest import register_sources, save_records
from app.industry_connectors import record
from app.research_api import coverage, coverage_markdown


def test_30d_zero_does_not_disappear_with_old_event_or_http_success(db):
    definitions = register_sources(db)
    sid = 'technews-server'
    definition = next(d for d in definitions if d['id'] == sid)
    assert 'odm' in definition['segments']
    reference = datetime.now(timezone.utc)
    event = record('AI 伺服器出貨進度', '整機伺服器訂單', 'https://technews.tw/old-server/', reference - timedelta(days=45), 'day')
    save_records(db, sid, [event], [], list(db.scalars(select(Company))))
    source = db.get(Source, sid)
    source.status = 'success'; source.last_success = reference
    db.commit()
    data = coverage(db, reference)
    row = next(r for r in data['rows'] if r['id'] == 'odm')
    assert row['direct_30d'] == 0 and row['direct_90d'] == 1
    assert row['successful_sources'] > 0
    assert any('近 30 日' in gap for gap in row['gaps'])
    assert not any('近 90 日' in gap for gap in row['gaps'])
    report = coverage_markdown(data)
    assert '0／1' in report and '近 30 日' in report


def test_configuration_and_failed_source_are_separate_from_missing_events(db):
    register_sources(db)
    db.get(Source, 'technews-server').status = 'configuration_required'
    db.get(Source, 'semiengineering').status = 'failed'
    db.commit()
    row = next(r for r in coverage(db)['rows'] if r['id'] == 'odm')
    assert row['direct_30d'] == row['direct_90d'] == 0
    assert any('待設定' in gap for gap in row['gaps'])
    assert any('取得失敗' in gap for gap in row['gaps'])
    assert any('近 30 日' in gap for gap in row['gaps'])
    assert any('近 90 日' in gap for gap in row['gaps'])
