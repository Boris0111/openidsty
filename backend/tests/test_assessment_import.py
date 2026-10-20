from pathlib import Path
import shutil
import pytest
from sqlalchemy import select, func
from app.models import Theme, Financial
from app.config import MAP_DIR
from app.import_map import import_map, read_doc


def test_assessment_projection_idempotence_and_original_baseline(db):
    original = db.get(Theme, 'liquid-cooling')
    expected = original.data['assessment']
    assert expected['reviewed'] == original.checked == '2026-10-07'
    assert original.prose == read_doc(MAP_DIR / 'themes/liquid-cooling.md')[1]
    import_map(db)
    assert db.get(Theme, original.id).data['assessment'] == expected
    assert db.scalar(select(func.count()).select_from(Theme)) == 7


def test_invalid_assessment_does_not_modify_existing_projection(db, tmp_path):
    copied = tmp_path / 'map'; shutil.copytree(MAP_DIR, copied)
    theme = db.get(Theme, 'liquid-cooling')
    expected_data, expected_prose = dict(theme.data), theme.prose
    file = copied / 'themes/liquid-cooling.md'
    text = file.read_text(encoding='utf-8').replace('source_id: aaon-liquid-cooling-filing', 'source_id: missing-source')
    file.write_text(text, encoding='utf-8')
    with pytest.raises(ValueError, match='source_id 引用不存在'):
        import_map(db, copied)
    assert db.get(Theme, theme.id).data == expected_data
    assert db.get(Theme, theme.id).prose == expected_prose


def test_optional_assessment_legacy_theme_remains_readable(db, tmp_path):
    # Model a pre-version legacy import, rather than deleting a reviewed history.
    from sqlalchemy import delete
    from app.models import ThemeAssessmentVersion
    db.execute(delete(ThemeAssessmentVersion).where(ThemeAssessmentVersion.theme_id=='liquid-cooling'));db.commit()
    import yaml
    copied = tmp_path / 'map'; shutil.copytree(MAP_DIR, copied)
    file = copied / 'themes/liquid-cooling.md'
    _, header, body = file.read_text(encoding='utf-8').split('---', 2)
    data = yaml.safe_load(header); data.pop('assessment'); data.pop('technical-profile',None)
    for milestone in data['milestones']: milestone.pop('id')
    file.write_text('---\n' + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + '---' + body, encoding='utf-8')
    import_map(db, copied)
    theme = db.get(Theme, 'liquid-cooling')
    assert 'assessment' not in theme.data
    assert theme.checked == '2026-10-07' and 'https://' in theme.prose


def test_new_events_and_financial_values_do_not_modify_authored_assessment(db):
    from app.ingest import register_sources, save_records
    from app.models import Company
    from app.industry_connectors import record
    from datetime import datetime, timezone
    from app.connectors import parse_tw
    import json
    register_sources(db)
    theme = db.get(Theme, 'liquid-cooling'); expected = dict(theme.data)
    event = record('液冷設備新規格', '新的產業消息', 'https://technews.tw/assessment-new/', datetime.now(timezone.utc), 'day')
    save_records(db, 'technews-components', [event], [], list(db.scalars(select(Company))))
    payload=json.loads((Path(__file__).parent/'fixtures/tw-revenue.json').read_text(encoding='utf-8'))
    companies=list(db.scalars(select(Company)))
    events,financials=parse_tw(json.dumps(payload),'revenue','https://official.test',{'2330':'2330.TW'})
    save_records(db,'twse-revenue',events,financials,companies)
    original_value=db.scalar(select(Financial)).revenue
    payload[0]['營業收入-當月營收']=str(int(str(payload[0]['營業收入-當月營收']).replace(',', ''))+1)
    events,financials=parse_tw(json.dumps(payload),'revenue','https://official.test',{'2330':'2330.TW'})
    save_records(db,'twse-revenue',events,financials,companies)
    db.commit()
    assert db.get(Theme, theme.id).data == expected
    assert db.get(Theme, theme.id).checked == '2026-10-07'
    assert db.scalar(select(Financial)).revenue != original_value
