"""Financial history uses the real writer role in the disposable database."""
from datetime import date
from decimal import Decimal
from dataclasses import replace
import os
import uuid
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.exc import DBAPIError
from app.financial_core import FinancialContext,FinancialValue,RawFact,FinancialGap,gross_margin
from app.financial_store import register_metrics,save_official,save_derived,latest


@pytest.fixture
def storage():
    url=os.getenv('RESEARCH_PG_WRITER_URL')
    if not url:pytest.skip('Financial storage requires disposable PostgreSQL')
    engine=create_engine(url,hide_parameters=True)
    if engine.url.database!='industry_research_test':raise RuntimeError('Disposable financial test DB required')
    with engine.connect() as connection:
        transaction=connection.begin()
        register_metrics(connection)
        company='company-financial-'+uuid.uuid4().hex
        connection.execute(text("INSERT INTO research.entities VALUES(:id,'company')"),{'id':company})
        yield connection,company
        transaction.rollback()
    engine.dispose()


def pair(company,number,filing='one',filed=date(2026,5,1),metric='revenue',factor='1'):
    context=FinancialContext(company,'sec',metric,date(2026,2,1),date(2026,4,30),'quarterly',currency='USD')
    fact=RawFact(context,filing,'us-gaap:'+metric,'USD',Decimal(number),filed,'https://www.sec.gov/test/'+filing,multiplier=Decimal(factor))
    value=FinancialValue(context,fact.normalized_value,uuid.uuid4(),filing,2027,1)
    return value,(fact,)


def test_same_value_new_filing_adds_provenance_without_revision(storage):
    connection,company=storage
    value,facts=pair(company,'1000',factor='1000')
    one=save_official(connection,value,facts)
    repeated=save_official(connection,value,facts)
    changed,facts2=pair(company,'1000000.00','two',date(2026,6,1))
    same=save_official(connection,changed,facts2)
    assert one['new_revision'] and not repeated['new_revision'] and not same['new_revision']
    assert one['observation_id']==same['observation_id']
    assert latest(connection,value.context.group_id)['value']==Decimal('1000000')
    assert latest(connection,value.context.group_id)['filed_at']==date(2026,6,1)
    assert connection.execute(text('SELECT count(*) FROM research.observation_provenance WHERE observation_id=:id'),{'id':one['observation_id']}).scalar_one()==2


def test_restatement_then_late_history_does_not_replace_latest_filing(storage):
    connection,company=storage
    old,facts=pair(company,'100','original',date(2026,5,1))
    initial=save_official(connection,old,facts)
    new,facts=pair(company,'110','restated',date(2026,6,1))
    revised=save_official(connection,new,facts)
    assert revised['revision']==2 and revised['active_changed']
    late,facts=pair(company,'90','earlier',date(2026,4,30))
    history=save_official(connection,late,facts)
    assert history['revision']==3 and not history['active_changed']
    active=latest(connection,new.context.group_id)
    assert active['value']==Decimal('110') and active['observation_id']==revised['observation_id']
    assert active['supersedes']==initial['observation_id']
    back,facts=pair(company,'100','new-restatement',date(2026,7,1))
    returned=save_official(connection,back,facts)
    assert returned['revision']==4 and returned['active_changed']
    assert latest(connection,back.context.group_id)['observation_id']!=initial['observation_id']


def test_ambiguous_same_day_change_needs_explicit_correction_evidence(storage):
    connection,company=storage
    old,facts=pair(company,'100')
    initial=save_official(connection,old,facts)
    new,facts=pair(company,'110','amendment')
    pending=save_official(connection,new,facts)
    assert pending['status']=='needs-verification' and not pending['active_changed']
    confirmed=save_official(connection,new,facts,expected_supersedes=initial['observation_id'])
    assert confirmed['revision']==2 and latest(connection,new.context.group_id)['value']==Decimal('110')


def test_missing_is_not_zero_and_same_raw_identity_cannot_be_rewritten(storage):
    connection,company=storage
    zero,facts=pair(company,'0')
    save_official(connection,zero,facts)
    missing=replace(facts[0],value=None)
    with pytest.raises(FinancialGap):save_official(connection,zero,(missing,))
    altered=replace(facts[0],value=Decimal(1))
    with pytest.raises(FinancialGap):save_official(connection,replace(zero,value=Decimal(1)),(altered,))
    assert latest(connection,zero.context.group_id)['value']==0


def test_derived_lineage_is_persisted_and_repeated_derivation_is_stable(storage):
    connection,company=storage
    revenue,facts=pair(company,'3')
    revenue_saved=save_official(connection,revenue,facts)
    revenue=replace(revenue,observation_id=revenue_saved['observation_id'])
    profit,facts=pair(company,'1',metric='gross-profit')
    profit_saved=save_official(connection,profit,facts)
    profit=replace(profit,observation_id=profit_saved['observation_id'])
    derived=gross_margin(profit,revenue)
    first=save_derived(connection,derived,filed_at=date(2026,5,1))
    again=save_derived(connection,derived,filed_at=date(2026,5,1))
    assert first['new_revision'] and not again['new_revision']
    rows=connection.execute(text('SELECT input_id,formula_version FROM research.financial_derivations WHERE observation_id=:id ORDER BY ordinal'),{'id':first['observation_id']}).all()
    assert [row.input_id for row in rows]==list(derived.input_ids)
    assert all(row.formula_version=='financial-v1:gross-margin' for row in rows)
    with pytest.raises(DBAPIError):
        with connection.begin_nested():
            connection.execute(text('UPDATE research.financial_observations SET value=9 WHERE observation_id=:id'),{'id':first['observation_id']})
