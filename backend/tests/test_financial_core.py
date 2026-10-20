from dataclasses import replace
from datetime import date
from decimal import Decimal
import uuid
import pytest
from app.financial_core import (FinancialContext,FinancialValue,RawFact,FinancialGap,
    decimal_value,decimal_text,gross_margin,single_quarter,revenue_yoy,source_priority)


def context(metric='revenue',basis='quarterly',start='2026-02-01',end='2026-04-30',**kwargs):
    unit='per-share' if metric.startswith('eps-') else 'percent' if metric in ('gross-margin','revenue-yoy') else 'amount'
    return FinancialContext('company-test','sec',metric,date.fromisoformat(start),date.fromisoformat(end),basis,
        unit=unit,currency='USD',**kwargs)


def value(ctx,number,statement='filing-one',fy=2027,fq=1):
    return FinancialValue(ctx,Decimal(number),uuid.uuid4(),statement,fy,fq)


@pytest.mark.parametrize('number',['9999999999999999999999999999.1234567890','0','-12.0000000001','1.00000000000'])
def test_exact_decimal_and_no_float_roundtrip(number):
    assert Decimal(decimal_text(decimal_value(number)))==Decimal(number)


@pytest.mark.parametrize('number',[0.1,True,'NaN','Infinity','1e28','0.00000000001','not-a-number'])
def test_unrepresentable_values_are_rejected(number):
    with pytest.raises(ValueError):decimal_value(number)


def test_raw_identity_keeps_filing_and_context_group_excludes_filing():
    ctx=context()
    fact=RawFact(ctx,'accession-one','us-gaap:Revenues','USD',Decimal('10'),date(2026,5,1),'https://www.sec.gov/test')
    revised=replace(fact,accession='accession-two')
    assert revised.fact_id!=fact.fact_id and revised.context.group_id==fact.context.group_id
    assert replace(fact,context=replace(ctx,metric_id='gross-profit')).fact_id==fact.fact_id
    assert value(ctx,'10').semantic_hash==value(ctx,'10.00','filing-two').semantic_hash
    assert value(ctx,'11').semantic_hash!=value(ctx,'10').semantic_hash
    for changed in [replace(ctx,currency='TWD'),replace(ctx,scope='standalone'),replace(ctx,source_family='twse')]:
        assert changed.group_id!=ctx.group_id


def test_gross_margin_uses_exact_same_statement_and_has_lineage():
    revenue=value(context(),'3');gross=value(context('gross-profit'),'1')
    result=gross_margin(gross,revenue)
    assert result.value==Decimal('33.3333333333')
    assert result.input_ids==(gross.observation_id,revenue.observation_id)
    assert result==gross_margin(gross,revenue)
    with pytest.raises(FinancialGap):gross_margin(replace(gross,statement_id='different'),revenue)
    with pytest.raises(FinancialGap):gross_margin(gross,value(context(),'0'))


def test_non_calendar_q4_from_verified_same_year_cumulative():
    annual=value(context('operating-cash-flow','annual','2025-02-01','2026-01-31'),'300',fq=4)
    nine_month=value(context('operating-cash-flow','ytd','2025-02-01','2025-10-31'),'210',fq=3)
    result=single_quarter(annual,nine_month)
    assert result.value==Decimal('90') and result.context.period_start==date(2025,11,1)
    assert result.context.period_end==date(2026,1,31) and result.context.basis=='quarterly'
    assert result.input_ids==(annual.observation_id,nine_month.observation_id)


def test_distinct_filings_require_explicit_compatibility_review():
    current=value(context('capex','ytd','2026-01-01','2026-06-30'),'100','new')
    prior=value(context('capex','ytd','2026-01-01','2026-03-31'),'40','old')
    with pytest.raises(FinancialGap):single_quarter(current,prior)
    assert single_quarter(current,prior,verified_filings=frozenset(('new','old'))).value==Decimal('60')
    with pytest.raises(FinancialGap):single_quarter(current,replace(prior,context=replace(prior.context,currency='TWD')),verified_filings=frozenset(('new','old')))


@pytest.mark.parametrize('metric',['eps-basic','eps-diluted','gross-margin','cash-and-equivalents','total-liabilities'])
def test_eps_ratios_and_balances_cannot_be_subtracted(metric):
    instant=metric in ('cash-and-equivalents','total-liabilities')
    extra={'share_class':'ordinary'} if metric.startswith('eps-') else {}
    a=context(metric,'instant' if instant else 'ytd','2026-06-30' if instant else '2026-01-01','2026-06-30',**extra)
    b=context(metric,'instant' if instant else 'ytd','2026-03-31' if instant else '2026-01-01','2026-03-31',**extra)
    with pytest.raises(FinancialGap):single_quarter(value(a,'10'),value(b,'4'))


def test_non_calendar_revenue_yoy_requires_known_matching_fiscal_quarter():
    current=value(context('revenue','quarterly','2026-02-01','2026-04-30'),'120',fy=2027,fq=1)
    prior=value(context('revenue','quarterly','2025-02-01','2025-04-30'),'100',fy=2026,fq=1)
    assert revenue_yoy(current,prior).value==Decimal('20')
    with pytest.raises(FinancialGap):revenue_yoy(replace(current,fiscal_quarter=None),prior)
    with pytest.raises(FinancialGap):revenue_yoy(current,replace(prior,fiscal_quarter=2))
    with pytest.raises(FinancialGap):revenue_yoy(current,replace(prior,value=Decimal(0)))


def test_monthly_yoy_keeps_leap_month_and_source_scope():
    current=value(context('revenue','monthly','2025-02-01','2025-02-28'),'120')
    prior=value(context('revenue','monthly','2024-02-01','2024-02-29'),'100')
    assert revenue_yoy(current,prior).value==Decimal('20')
    with pytest.raises(FinancialGap):revenue_yoy(current,replace(prior,context=replace(prior.context,scope='standalone')))


def test_eps_share_class_and_source_priority_are_explicit():
    a=context('eps-basic',share_class='ordinary')
    assert a.group_id!=replace(a,share_class='adr').group_id
    assert a.group_id!=replace(a,metric_id='eps-diluted').group_id
    assert source_priority('sec','sec')<source_priority('sec','sec',provenance_kind='manual-official')<source_priority('twse','sec')
    assert source_priority('sec','sec',provenance_kind='derived')>source_priority('sec','sec',provenance_kind='legacy-import')
    with pytest.raises(FinancialGap):source_priority('sec','')


def test_original_unit_conversion_preserves_missing_and_zero():
    ctx=context()
    fact=RawFact(ctx,'filing-one','revenue','TWD thousand',Decimal('1.23'),date(2026,5,1),'https://example.org/official',multiplier=Decimal('1000'))
    assert fact.normalized_value==Decimal('1230')
    assert replace(fact,value=Decimal(0)).normalized_value==0
    assert replace(fact,value=None).normalized_value is None
