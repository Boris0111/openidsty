"""Synthetic boundary cases. Official capture verification is a separate check."""
from datetime import date
from decimal import Decimal
import json
import hashlib
from pathlib import Path
import pytest
from app.financial_sec import SecIssuer,parse_companyfacts,persist_sec
from app.financial_store import latest
from test_financial_store import storage
from sqlalchemy import text

OFFICIAL=Path(__file__).parent/'fixtures/official-sec-20261017'


@pytest.mark.parametrize('name,cik,end,revenue,eps,cfo',[
    ('vrt','1674101',date(2025,12,31),'10229900000','3.49','2113800000'),
    ('nvda','1045810',date(2026,1,25),'215938000000','4.93','102718000000')])
def test_official_annual_samples_preserve_exact_values_and_non_calendar_dates(name,cik,end,revenue,eps,cfo):
    payload=(OFFICIAL/(name+'.selected.json')).read_bytes()
    provenance=next(row for row in json.loads((OFFICIAL/'provenance.json').read_text()) if row['id']==name)
    assert hashlib.sha256(payload).hexdigest()==provenance['selected_sha256']
    result=parse_companyfacts(payload,SecIssuer('company-'+name,cik))
    assert not result.unresolved
    rows={row.value.context.metric_id:row for row in result.records if row.value.context.period_end==end and row.value.context.basis=='annual'}
    assert rows['revenue'].value.value==Decimal(revenue)
    assert rows['eps-basic'].value.value==Decimal(eps)
    assert rows['operating-cash-flow'].value.value==Decimal(cfo)
    if name=='nvda':assert rows['revenue'].value.context.period_start==date(2025,1,27)
    assert rows['revenue'].value.fiscal_year is None
    # ECD and other unmapped standard namespaces are not called issuer extensions.
    assert any(row['reason']=='unmapped-taxonomy' for row in result.gaps)


def test_official_comparative_eps_revisions_and_repeated_import(storage):
    connection,company=storage
    result=parse_companyfacts((OFFICIAL/'nvda.selected.json').read_bytes(),SecIssuer(company,'1045810'))
    imported=persist_sec(connection,result)
    assert imported['new_revisions']>0 and imported['needs_review']==0
    repeated=persist_sec(connection,result)
    assert repeated['new_revisions']==repeated['active_changes']==0 and repeated['needs_review']==0
    rows=[row for row in result.records if row.value.context.metric_id=='eps-basic' and
        row.value.context.period_end==date(2023,1,29) and row.value.context.basis=='annual']
    assert [row.value.value for row in sorted(rows,key=lambda row:row.fact.filed_at)]==[Decimal('1.76'),Decimal('1.76'),Decimal('0.18')]
    active=latest(connection,rows[0].value.context.group_id)
    assert active['value']==Decimal('0.18') and active['revision']==2
    count=connection.execute(text('SELECT count(*) FROM research.observation_provenance p JOIN research.financial_observations o USING(observation_id) WHERE o.group_id=:group'),{'group':rows[0].value.context.group_id}).scalar_one()
    assert count==3


def document(changes=None):
    facts={}
    data={'cik':1674101,'entityName':'SYNTHETIC TEST ISSUER','facts':{'us-gaap':facts}}
    metrics={'Revenues':100,'GrossProfit':40,'OperatingIncomeLoss':20,'NetIncomeLoss':12,'ProfitLoss':15,
        'EarningsPerShareBasic':'1.25','EarningsPerShareDiluted':'1.20',
        'NetCashProvidedByUsedInOperatingActivities':30,'PaymentsToAcquirePropertyPlantAndEquipment':5,
        'CashAndCashEquivalentsAtCarryingValue':50,'Liabilities':200}
    for tag,number in metrics.items():
        row={'end':'2025-04-30','val':number,'accn':'0001674101-25-000001','filed':'2025-06-01',
            'form':'10-Q','fy':2026,'fp':'Q1','frame':'CY2025Q1'}
        if tag not in ('Liabilities','CashAndCashEquivalentsAtCarryingValue'):row['start']='2025-02-01'
        facts[tag]={'units':{'USD/shares' if tag.startswith('Earnings') else 'USD':[row]}}
    if changes:changes(data)
    return json.dumps(data)


def parse(payload=None,company='company-synthetic-sec'):
    return parse_companyfacts(payload or document(),SecIssuer(company,'0001674101'))


def test_standard_metrics_preserve_actual_period_parent_total_eps_and_unknown_share_class():
    result=parse()
    assert len(result.records)==11 and not result.unresolved
    rows={item.value.context.metric_id:item for item in result.records}
    assert rows['net-income-parent'].value.value==12 and rows['net-income-total'].value.value==15
    assert rows['eps-basic'].value.value==Decimal('1.25') and rows['eps-diluted'].value.value==Decimal('1.20')
    assert rows['eps-basic'].value.context.share_class=='unspecified'
    assert rows['total-liabilities'].value.context.basis=='instant'
    revenue=rows['revenue']
    assert revenue.value.context.period_start==date(2025,2,1) and revenue.value.context.period_end==date(2025,4,30)
    assert revenue.value.fiscal_year is None and revenue.value.fiscal_quarter is None
    assert revenue.raw['fy']==2026 and revenue.fact.filed_at==date(2025,6,1)
    assert result.derived[0][0].value==40


def test_explicitly_verified_fiscal_labels_and_share_class_are_distinct():
    issuer=SecIssuer('company-synthetic-sec','1674101','ordinary-class-a',
        {(date(2025,2,1),date(2025,4,30)):(2026,1)})
    known=parse_companyfacts(document(),issuer)
    eps=next(row for row in known.records if row.value.context.metric_id=='eps-basic')
    assert eps.value.fiscal_year==2026 and eps.value.fiscal_quarter==1
    assert eps.fact.context.share_class=='ordinary-class-a'
    unknown=next(row for row in parse().records if row.value.context.metric_id=='eps-basic')
    assert eps.fact.fact_id!=unknown.fact.fact_id


def test_annual_ytd_cash_and_sign_constraints():
    def change(data):
        facts=data['facts']['us-gaap']
        facts['Revenues']['units']['USD'][0].update(start='2024-05-01')
        facts['NetCashProvidedByUsedInOperatingActivities']['units']['USD'][0].update(start='2024-11-01',val=-20)
        facts['PaymentsToAcquirePropertyPlantAndEquipment']['units']['USD'][0]['val']=-5
        facts['CashAndCashEquivalentsAtCarryingValue']['units']['USD'][0]['start']='2025-02-01'
    result=parse(document(change))
    rows={item.value.context.metric_id:item for item in result.records}
    assert rows['revenue'].value.context.basis=='annual'
    assert rows['operating-cash-flow'].value.context.basis=='ytd' and rows['operating-cash-flow'].value.value==-20
    assert 'capex' not in rows and 'cash-and-equivalents' not in rows and len(result.unresolved)==2


def test_missing_standard_custom_taxonomy_and_context_conflict_leave_gaps():
    def change(data):
        data['facts']['custom']={'AIRevenue':{'units':{'USD':[]}}}
        facts=data['facts']['us-gaap']
        del facts['NetIncomeLoss']
        first=facts['Revenues']['units']['USD'][0]
        facts['Revenues']['units']['USD'].append(dict(first,val=101))
        facts['GrossProfit']['units']['USD'][0]['dimensions']={'ProductAxis':'AI'}
    result=parse(document(change))
    assert any(row['reason']=='unmapped-taxonomy' and 'custom' in row['taxonomies'] for row in result.gaps)
    assert any(row.get('metric_id')=='net-income-parent' for row in result.gaps)
    assert any(row['reason']=='conflicting-standard-context' for row in result.unresolved)
    assert not any(row.value.context.metric_id in ('gross-profit','revenue','net-income-parent') for row in result.records)
    assert not result.derived


@pytest.mark.parametrize('payload',['{}','<html>shell</html>','{"cik":1674101,"facts":{},"facts":{}}',
    '{"cik":1674102,"facts":{}}'])
def test_bad_or_wrong_entity_payload_is_rejected(payload):
    with pytest.raises(ValueError):parse(payload)


def test_non_us_gaap_is_an_explicit_gap_not_a_zero():
    result=parse(json.dumps({'cik':1674101,'facts':{'ifrs-full':{'Revenue':{'units':{'TWD':[]}}}}}))
    assert not result.records and result.gaps[0]['reason']=='unsupported-taxonomy'


def test_same_filing_alternative_revenue_tags_cannot_silently_change_definition():
    def change(data):
        data['facts']['us-gaap']['SalesRevenueNet']={'units':{'USD':[
            dict(data['facts']['us-gaap']['Revenues']['units']['USD'][0],val=90)]}}
    result=parse(document(change))
    assert any(row['reason']=='conflicting-standard-tags' for row in result.unresolved)
    assert not any(row.value.context.metric_id=='revenue' for row in result.records)


def test_restatement_same_value_filing_and_repeat_have_exact_lineage(storage):
    connection,company=storage
    def change(data):
        for concept in data['facts']['us-gaap'].values():
            for rows in concept['units'].values():
                first=rows[0]
                # Same period in later filings: a changed number, then same value.
                second=dict(first,accn='0001674101-25-000002',filed='2025-07-01',val=str(Decimal(str(first['val']))+1))
                rows.extend([second,dict(second,accn='0001674101-25-000003',filed='2025-08-01')])
    result=parse(document(change),company)
    first=persist_sec(connection,result)
    assert first['new_revisions']==24 and first['needs_review']==0
    again=persist_sec(connection,result)
    assert again['new_revisions']==0 and again['active_changes']==0
    revenue=next(row for row in result.records if row.value.context.metric_id=='revenue')
    active=latest(connection,revenue.value.context.group_id)
    assert active['value']==101 and active['revision']==2 and active['filed_at']==date(2025,8,1)
    assert active['supersedes'] is not None and active['source_as_of'] is None
