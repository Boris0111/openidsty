"""SEC companyfacts: exact entity facts, with explicit gaps for missing contexts."""
from dataclasses import dataclass,field,replace
from datetime import date
from decimal import Decimal
import json,re,uuid
from .financial_core import (METRICS,FinancialContext,FinancialValue,RawFact,FinancialGap,
    decimal_value,decimal_text,gross_margin)

FAMILY='sec'
# Deliberately omit custom tags and broader cash/debt concepts.
TAGS={
    'revenue':('RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'),
    'gross-profit':('GrossProfit',),
    'operating-income':('OperatingIncomeLoss',),
    'net-income-parent':('NetIncomeLoss',),
    'net-income-total':('ProfitLoss',),
    'eps-basic':('EarningsPerShareBasic',),
    'eps-diluted':('EarningsPerShareDiluted',),
    'operating-cash-flow':('NetCashProvidedByUsedInOperatingActivities',),
    'capex':('PaymentsToAcquirePropertyPlantAndEquipment',),
    'cash-and-equivalents':('CashAndCashEquivalentsAtCarryingValue',),
    'total-liabilities':('Liabilities',),
}
FORMS={'10-K','10-Q','10-K/A','10-Q/A','20-F','20-F/A','40-F','40-F/A','6-K'}
MAX_BYTES=25*1024*1024


@dataclass(frozen=True)
class SecIssuer:
    company_id:str
    cik:str
    eps_share_class:str='unspecified'
    # Only explicitly verified actual-date ranges may acquire fiscal labels.
    fiscal_periods:dict=field(default_factory=dict)

    def __post_init__(self):
        if not re.fullmatch(r'\d{1,10}',self.cik) or int(self.cik)==0:raise ValueError('公司 CIK 不正確。')


@dataclass(frozen=True)
class SecRecord:
    value:FinancialValue
    fact:RawFact
    raw:dict
    limitations:tuple[str,...]


@dataclass
class SecResult:
    records:list[SecRecord]
    derived:list
    gaps:list[dict]
    unresolved:list[dict]


def capabilities():
    return {metric:{'provided':metric in TAGS,'derived':metric in ('gross-margin','revenue-yoy'),
        'taxonomy':'us-gaap','tags':list(TAGS.get(metric,())),
        'frequency_hours':24,'history':'available-companyfacts-periods-only',
        'scope':'whole-filing-entity','custom_tags':False,'xml_context_id':False,
        'eps_share_class':'requires-confirmation' if metric.startswith('eps-') else None} for metric in METRICS}


def _no_duplicates(pairs):
    data={}
    for key,value in pairs:
        if key in data:raise ValueError('SEC JSON 欄位重複。')
        data[key]=value
    return data


def _payload(payload):
    if isinstance(payload,bytes):
        if len(payload)>MAX_BYTES:raise ValueError('SEC 資料超過 25 MiB。')
        payload=payload.decode('utf-8-sig')
    if not isinstance(payload,str) or len(payload.encode())>MAX_BYTES:raise ValueError('SEC 資料須為有界原始 JSON。')
    data=json.loads(payload,parse_float=Decimal,object_pairs_hook=_no_duplicates,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('SEC 無效數值。')))
    if not isinstance(data,dict) or not isinstance(data.get('facts'),dict):raise ValueError('SEC companyfacts 格式改變。')
    return data


def _period(row,metric):
    end=date.fromisoformat(row['end'])
    if metric in ('cash-and-equivalents','total-liabilities'):
        if row.get('start'):raise FinancialGap('期末值意外包含期間起點。')
        return end,end,'instant'
    start=date.fromisoformat(row['start']);days=(end-start).days+1
    basis='quarterly' if 70<=days<=110 else 'annual' if 335<=days<=385 else 'ytd' if 160<=days<=320 else None
    if not basis:raise FinancialGap('來源期間不是可確認的單季／累計／年度長度。')
    return start,end,basis


def parse_companyfacts(payload,issuer:SecIssuer):
    data=_payload(payload)
    if isinstance(data.get('cik'),bool) or str(data.get('cik','')).lstrip('0')!=issuer.cik.lstrip('0'):
        raise ValueError('SEC CIK 與指定公司不一致。')
    result=SecResult([],[],[],[])
    gaap=data['facts'].get('us-gaap',{})
    if not isinstance(gaap,dict):raise ValueError('SEC US GAAP 格式改變。')
    if not gaap:result.gaps.append({'reason':'unsupported-taxonomy','available':list(data['facts'])})
    custom=[key for key in data['facts'] if key not in ('us-gaap','ifrs-full','dei','srt')]
    if custom:result.gaps.append({'reason':'custom-taxonomy-unmapped','taxonomies':custom})
    candidates={};count=0
    for metric,tags in TAGS.items():
        seen=False
        for priority,tag in enumerate(tags):
            concept=gaap.get(tag)
            if concept is None:continue
            if not isinstance(concept,dict) or not isinstance(concept.get('units'),dict):raise ValueError('SEC concept 格式改變。')
            for unit,rows in concept['units'].items():
                if not isinstance(rows,list):raise ValueError('SEC fact 清單格式改變。')
                count+=len(rows)
                if count>200000:raise ValueError('SEC facts 超過有界解析筆數。')
                unit_type=METRICS[metric][1]
                unit_match=re.fullmatch(r'([A-Z]{3})(/shares)?',unit)
                if not unit_match or bool(unit_match[2])!=(unit_type=='per-share'):
                    result.gaps.append({'metric_id':metric,'reason':'unsupported-unit','unit':unit});continue
                for raw in rows:
                    if not isinstance(raw,dict):raise ValueError('SEC fact 格式改變。')
                    if raw.get('form') not in FORMS:continue
                    try:
                        if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',raw.get('accn','')):raise ValueError('申報識別不正確。')
                        if raw.get('dimensions') or raw.get('segment'):raise FinancialGap('維度 fact 須另外核對，不能當整家公司數值。')
                        start,end,basis=_period(raw,metric)
                        filed=date.fromisoformat(raw['filed'])
                        if filed<end:raise ValueError('申報日早於數值期間。')
                        number=decimal_value(raw['val'])
                        if metric=='capex' and number<0:raise FinancialGap('購置支出 tag 出現負值，須核對符號。')
                        context=FinancialContext(issuer.company_id,FAMILY,metric,start,end,basis,
                            scope='whole-filing-entity',unit=unit_type,currency=unit_match[1],
                            share_class=issuer.eps_share_class if unit_type=='per-share' else '')
                        url=f'https://www.sec.gov/Archives/edgar/data/{int(issuer.cik)}/{raw["accn"].replace("-","")}/{raw["accn"]}-index.htm'
                        fact=RawFact(context,raw['accn'],'us-gaap:'+tag,unit,number,filed,url)
                        # fy/fp describe the filing, not necessarily this comparative fact.
                        fiscal=issuer.fiscal_periods.get((start,end),(None,None))
                        value=FinancialValue(context,number,uuid.uuid5(uuid.NAMESPACE_URL,
                            'sec-value:'+str(fact.fact_id)+':'+decimal_text(number)),raw['accn'],*fiscal)
                    except (KeyError,ValueError,TypeError) as error:
                        result.unresolved.append({'metric_id':metric,'tag':tag,'unit':unit,'raw':raw,'reason':str(error)});continue
                    seen=True
                    limitations=['Companyfacts 未提供原始 XML context ID；保存可取得的期間、單位、申報及 frame。']
                    if unit_type=='per-share' and issuer.eps_share_class=='unspecified':
                        limitations.append('來源未明列普通股／ADR 或股別，EPS 比較需核對。')
                    key=(context.group_id,raw['accn'])
                    candidates.setdefault(key,[]).append((priority,SecRecord(value,fact,raw,tuple(limitations))))
        if not seen:result.gaps.append({'metric_id':metric,'reason':'no-supported-standard-fact','tags':list(tags)})
    for key,options in sorted(candidates.items()):
        priority=min(item[0] for item in options)
        chosen=[row for rank,row in options if rank==priority]
        if len({(row.value.value,row.fact.filed_at) for row in chosen})!=1:
            result.unresolved.append({'reason':'conflicting-standard-context','records':[row.raw for row in chosen]});continue
        # Equal aliases keep provenance; conflicting alternative concepts need review.
        selected=chosen[0]
        if any(row.value.value!=selected.value.value for _,row in options):
            result.unresolved.append({'reason':'conflicting-standard-tags','records':[row.raw for _,row in options]});continue
        unique={row.fact.fact_id:row for _,row in options}
        result.records.extend(unique.values())
    statements={}
    for row in result.records:
        context=row.value.context
        key=(row.fact.accession,row.fact.filed_at,context.period_start,context.period_end,context.basis,context.currency)
        statements.setdefault(key,{})[context.metric_id]=row
    for group in statements.values():
        if 'gross-profit' in group and 'revenue' in group:
            profit,revenue=group['gross-profit'],group['revenue']
            try:result.derived.append((gross_margin(profit.value,revenue.value),revenue.fact.filed_at))
            except FinancialGap as error:result.gaps.append({'metric_id':'gross-margin','reason':str(error)})
    return result


def persist_sec(connection,result:SecResult):
    from .financial_store import register_metrics,save_official,save_derived
    register_metrics(connection)
    saved=[];mapped={}
    # Filing order makes the first import and a replay converge on the same head.
    for row in sorted(result.records,key=lambda row:(row.fact.filed_at,str(row.fact.fact_id))):
        outcome=save_official(connection,row.value,(row.fact,),limitations=' '.join(row.limitations),
            payloads={str(row.fact.fact_id):{'companyfacts':row.raw}})
        if outcome['observation_id']:mapped[row.value.observation_id]=outcome['observation_id']
        saved.append(outcome)
    for derived,filed in sorted(result.derived,key=lambda pair:pair[1]):
        if all(key in mapped for key in derived.input_ids):
            saved.append(save_derived(connection,replace(derived,input_ids=tuple(mapped[key] for key in derived.input_ids)),filed_at=filed))
    return {'new_revisions':sum(item['new_revision'] for item in saved),'active_changes':sum(item['active_changed'] for item in saved),
        'needs_review':sum(item['status']=='needs-verification' for item in saved)+len(result.unresolved),
        'gaps':result.gaps,'unresolved':result.unresolved,'items':saved}
