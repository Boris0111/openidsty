from datetime import date,datetime,timezone,timedelta
from decimal import Decimal
import pytest
from sqlalchemy import select
from app.indicator_definitions import import_definitions
from app.ingest import register_sources
from app.models import Indicator,IndicatorObservation,Theme
from app.observations import save_observation,latest_observations


def sample(db,**updates):
    register_sources(db);import_definitions(db)
    d=db.get(Indicator,'aaon-liquid-cooling-revenue').data
    row=dict(indicator_id=d['id'],source_id=d['source_id'],document_identity='official-quarter-report',dataset=d['dataset'],entity=d['entity'],original_period='2026 Q1',period_start=date(2026,1,1),period_end=date(2026,3,31),basis=d['basis'],scope=d['scope'],unit=d['unit'],currency=d['currency'],value=Decimal('100'),published_at=None,reported_at=None,url='https://official.test/quarter',raw_excerpt='明確產品數值',raw={},fetched_at=datetime(2026,5,1,tzinfo=timezone.utc))
    return dict(row,**updates)


def test_same_value_rerun_ignores_retrieval_and_preserves_revision(db):
    data=sample(db);assert save_observation(db,data)
    assert not save_observation(db,dict(data,value=Decimal('100.000'),fetched_at=data['fetched_at']+timedelta(days=1),raw_excerpt='重新取得的相同數值'))
    assert db.query(IndicatorObservation).count()==1
    row=db.query(IndicatorObservation).one()
    assert row.fetched_at.replace(tzinfo=timezone.utc)==data['fetched_at']


def test_value_unit_basis_and_scope_corrections_keep_all_previous_values(db):
    data=sample(db);save_observation(db,data)
    save_observation(db,dict(data,value=Decimal('200')))
    correction=dict(data,value=Decimal('300'),currency='TWD',valid=False,invalid_reason='官方更正幣別，與 USD 定義不適用')
    save_observation(db,correction)
    assert not save_observation(db,dict(correction,fetched_at=data['fetched_at']+timedelta(days=1)))
    scope_correction=dict(data,value=Decimal('400'),basis='ytd',scope='包含混合業務的累計收入',valid=False,invalid_reason='官方更正為累計／混合口徑')
    save_observation(db,scope_correction)
    rows=list(db.scalars(select(IndicatorObservation).order_by(IndicatorObservation.revision)))
    assert [r.value for r in rows]==list(map(Decimal,['100','200','300','400']))
    assert [r.revision for r in rows]==[1,2,3,4]
    assert len({r.identity for r in rows})==1
    latest=latest_observations(db,data['indicator_id'])
    assert len(latest)==1 and latest[0].valid is False and latest[0].invalid_reason


def test_zero_new_period_and_unknown_numbers_are_distinct(db):
    data=sample(db,value=Decimal('0'));expected=dict(db.get(Theme,'liquid-cooling').data)
    save_observation(db,data)
    save_observation(db,dict(data,period_start=date(2026,4,1),period_end=date(2026,6,30),original_period='2026 Q2',value=Decimal('123.45678901')))
    assert len(latest_observations(db,data['indicator_id']))==2
    assert db.get(Theme,'liquid-cooling').data==expected
    for value in (None,'NaN','Infinity'):
        with pytest.raises(ValueError):save_observation(db,dict(data,value=value))
    assert db.query(IndicatorObservation).count()==2


def test_wrong_unit_is_not_silently_accepted_as_valid_observation(db):
    data=sample(db)
    with pytest.raises(ValueError,match='單位／幣別／口徑'):
        save_observation(db,dict(data,unit='percent',currency=None))
    with pytest.raises(ValueError,match='理由'):
        save_observation(db,dict(data,valid=False))
