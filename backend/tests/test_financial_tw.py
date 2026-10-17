from pathlib import Path
from decimal import Decimal
from dataclasses import replace
from datetime import date
import csv,io,json
from sqlalchemy import text
import pytest
from app.financial_tw import TwIssuer,parse_taiwan,number,capabilities,persist_taiwan
from app.financial_store import latest,save_official
from app.financial_core import FinancialGap
from test_financial_store import storage

FIXTURES=Path(__file__).parent/'fixtures/official-tw-20261017'
PROVENANCE=json.loads((FIXTURES/'provenance.json').read_text(encoding='utf-8'))


def sample(provider,kind):
    return (FIXTURES/f'{provider}-{kind}.selected.json').read_bytes()


def parse(provider,kind,payload=None,issuer=None):
    key=provider+'-'+kind
    source=next(item for item in PROVENANCE if item['id']==key)
    code='2330' if provider=='twse' else '3324'
    identifier='company-tsmc' if provider=='twse' else 'company-auras'
    return parse_taiwan(payload if payload is not None else sample(provider,kind),
        provider+'-'+('financials' if kind=='income' else kind),'financials' if kind=='income' else kind,source['url'],
        {code:issuer or TwIssuer(identifier,(12,31))})


@pytest.mark.parametrize('provider,expected_revenue,expected_eps,expected_parent,expected_total',[
    ('twse','2404483690000','49.33','1279041690000','1279582227000'),
    ('tpex','17251778000','23.01','2132961000','2304320000')])
def test_actual_income_aliases_units_eps_and_distinct_net_income(provider,expected_revenue,expected_eps,expected_parent,expected_total):
    result=parse(provider,'income')
    values={row.value.context.metric_id:row.value.value for row in result.records}
    assert values['revenue']==Decimal(expected_revenue)
    assert values['eps-basic']==Decimal(expected_eps)
    assert values['net-income-parent']==Decimal(expected_parent)!=values['net-income-total']==Decimal(expected_total)
    assert all(row.value.context.basis=='ytd' and row.value.context.period_end==date(2026,6,30) for row in result.records)
    assert all(row.fact.filed_at is None and row.fact.source_as_of==date(2026,10,16) for row in result.records)
    assert all(row.value.context.scope=='issuer-summary-unspecified' for row in result.records)
    assert len(result.derived)==1 and result.derived[0][0].context.metric_id=='gross-margin'


@pytest.mark.parametrize('provider,expected',[('twse','2901183746000'),('tpex','20049278000')])
def test_actual_balance_is_total_liabilities_not_debt_or_cash(provider,expected):
    result=parse(provider,'balance')
    assert len(result.records)==1
    row=result.records[0]
    assert row.value.context.metric_id=='total-liabilities' and row.value.value==Decimal(expected)
    assert row.value.context.basis=='instant' and row.value.context.period_start==row.value.context.period_end==date(2026,6,30)
    assert not capabilities('balance')['cash-and-equivalents']['provided']


@pytest.mark.parametrize('provider,current,previous,expected_yoy',[
    ('twse','511857399000','330980920000','54.6486120711'),
    ('tpex','2884061000','2340447000','23.2269305821')])
def test_actual_monthly_precision_uses_traceable_derivation(provider,current,previous,expected_yoy):
    result=parse(provider,'revenue')
    revenues=[row for row in result.records if row.value.context.metric_id=='revenue']
    assert [row.value.value for row in revenues]==[Decimal(current),Decimal(previous)]
    assert revenues[0].value.context.period_start==date(2026,9,1)
    assert revenues[1].value.context.period_start==date(2025,9,1)
    assert result.derived[0][0].value==Decimal(expected_yoy)
    assert result.derived[0][0].input_ids==tuple(row.value.observation_id for row in revenues)
    assert any(gap['reason']=='precision-not-supported' for gap in result.gaps)
    assert all(row.fact.filed_at is None for row in result.records)


def test_csv_aliases_missing_zero_and_unknown_calendar():
    row=json.loads(sample('tpex','income'))[0]
    row['營業收入']='0';row['淨利（淨損）歸屬於母公司業主']=''
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(row));writer.writeheader();writer.writerow(row)
    result=parse('tpex','income',stream.getvalue())
    values={item.value.context.metric_id:item.value.value for item in result.records}
    assert values['revenue']==0 and 'net-income-parent' not in values and values['net-income-total']==Decimal('2304320000')
    assert not result.derived
    unknown=parse('tpex','income',issuer=TwIssuer('company-auras'))
    assert not unknown.records and unknown.unresolved[0]['reason']=='calendar-unverified'
    assert parse('tpex','revenue',issuer=TwIssuer('company-auras')).records


@pytest.mark.parametrize('body',['<html>JavaScript shell</html>','[]','{}','not,a,valid,table\n1,2,3,4'])
def test_shell_empty_or_changed_shape_is_rejected(body):
    with pytest.raises(ValueError):parse('twse','income',body)


@pytest.mark.parametrize('raw',['1,2','NaN','Infinity',True,0.1,'<script>bad</script>'])
def test_bad_numeric_cells_are_not_fabricated_zero(raw):
    with pytest.raises(ValueError):number(raw)


def test_alias_collision_and_unverified_calendar_are_not_guessed():
    row=json.loads(sample('tpex','income'))[0];row['年度']='114'
    with pytest.raises(ValueError):parse('tpex','income',json.dumps([row],ensure_ascii=False))
    assert not parse('tpex','income',issuer=TwIssuer('company-auras',(1,31))).records


def test_big5_csv_and_annual_income_keep_original_period():
    row=json.loads(sample('tpex','income'))[0];row['Season']='4'
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(row));writer.writeheader();writer.writerow(row)
    result=parse('tpex','income',stream.getvalue().encode('cp950'))
    assert all(item.value.context.basis=='annual' and item.value.context.period_end==date(2026,12,31) for item in result.records)


def test_real_sample_storage_rerun_and_snapshot_history(storage):
    connection,company=storage
    issuer=TwIssuer(company,(12,31))
    result=parse('tpex','revenue',issuer=issuer)
    first=persist_taiwan(connection,result)
    assert first['new_revisions']==3
    assert persist_taiwan(connection,result)['new_revisions']==0
    current_group=result.records[0].value.context.group_id
    stored=latest(connection,current_group)
    assert stored['filed_at'] is None and stored['source_as_of']==date(2026,10,16)
    row=json.loads(sample('tpex','revenue'))[0]
    row['出表日期']='1151017'
    fresh=parse('tpex','revenue',json.dumps([row],ensure_ascii=False),issuer)
    assert persist_taiwan(connection,fresh)['new_revisions']==0
    assert latest(connection,current_group)['source_as_of']==date(2026,10,17)
    row['出表日期']='1151015';row['營業收入-當月營收']='1'
    historical=parse('tpex','revenue',json.dumps([row],ensure_ascii=False),issuer)
    assert persist_taiwan(connection,historical)['active_changes']==0
    assert latest(connection,current_group)['value']==Decimal('2884061000')


def test_numeric_json_precision_is_preserved_and_filing_dates_cannot_replace_snapshot_mode(storage):
    connection,company=storage
    # Some provider variants use JSON numbers, rather than quoted decimal cells.
    payload=sample('tpex','revenue').decode().replace('"23.226930582064025"','23.226930582064025')
    result=parse('tpex','revenue',payload,TwIssuer(company,(12,31)))
    persist_taiwan(connection,result)
    original=connection.execute(text('SELECT payload FROM research.financial_raw_facts WHERE fact_id=:id'),
        {'id':result.records[0].fact.fact_id}).scalar_one()['original']['row']
    assert original['營業收入-去年同月增減(%)']=='23.226930582064025'
    record=result.records[0]
    new_fact=replace(record.fact,accession='actual-filing',filed_at=date(2026,10,17),source_as_of=None)
    new_value=replace(record.value,statement_id='actual-filing')
    with pytest.raises(FinancialGap):save_official(connection,new_value,(new_fact,))
    assert latest(connection,record.value.context.group_id)['filed_at'] is None
