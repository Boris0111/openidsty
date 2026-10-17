"""TWSE/TPEx public summaries. Preserve source dates and unknown reporting scope."""
import calendar
import csv
from dataclasses import dataclass,replace
from datetime import date
from decimal import Decimal,InvalidOperation
import io,json,re,unicodedata,uuid
from urllib.parse import urlsplit
from .financial_core import (FinancialContext,FinancialValue,RawFact,FinancialGap,METRICS,
    decimal_value,decimal_text,gross_margin,revenue_yoy)

FAMILY='tw-mops-summary'
MAX_BYTES=25*1024*1024
ALIASES={'SecuritiesCompanyCode':'公司代號','CompanyCode':'公司代號','CompanyName':'公司名稱',
    'Date':'出表日期','Year':'年度','Season':'季別','基本每股盈餘':'基本每股盈餘(元)',
    '負債總額':'負債總計'}
FIELDS={'revenue':('營業收入',),'gross-profit':('營業毛利(毛損)淨額','營業毛利(毛損)'),
    'operating-income':('營業利益(損失)',),'net-income-parent':('淨利(淨損)歸屬於母公司業主',),
    'net-income-total':('本期淨利(淨損)',),'eps-basic':('基本每股盈餘(元)',)}


@dataclass(frozen=True)
class TwIssuer:
    company_id:str
    # Explicit verified calendar. None never becomes an invented January start.
    fiscal_year_end:tuple[int,int]|None=None
    scope:str='issuer-summary-unspecified'
    share_class:str='unspecified'


@dataclass(frozen=True)
class TwRecord:
    value:FinancialValue
    fact:RawFact
    raw:dict
    limitations:tuple[str,...]


@dataclass
class TwResult:
    records:list[TwRecord]
    derived:list
    gaps:list[dict]
    unresolved:list[dict]


def _key(value):return unicodedata.normalize('NFKC',str(value)).strip()


def fields(row):
    result={}
    for original,value in row.items():
        key=ALIASES.get(_key(original),_key(original))
        if key in result and str(result[key][1]).strip()!=str(value).strip():raise ValueError('官方欄位別名出現衝突。')
        result[key]=(original,value)
    return result


def number(raw):
    if raw is None:return None
    if isinstance(raw,(bool,float)):raise ValueError('來源數值不得先轉成 Float。')
    if isinstance(raw,Decimal):
        if not raw.is_finite():raise ValueError('來源數值不是有限數。')
        return raw
    value=_key(raw).replace(' ','')
    if len(value)>160:raise ValueError('來源數值超過長度限制。')
    if value in ('','-','--','—','N/A','NA','不適用'):return None
    if re.fullmatch(r'\([\d,.]+\)',value):value='-'+value[1:-1]
    if not re.fullmatch(r'[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?',value):
        raise ValueError('官方數值格式不正確。')
    try:result=Decimal(value.replace(',',''))
    except InvalidOperation:raise ValueError('官方數值格式不正確。') from None
    if not result.is_finite():raise ValueError('來源數值不是有限數。')
    return result


def rows(payload):
    if isinstance(payload,bytes):
        if len(payload)>MAX_BYTES:raise ValueError('官方資料超過 25 MiB。')
        try:payload=payload.decode('utf-8-sig')
        except UnicodeDecodeError:payload=payload.decode('cp950')
    if not isinstance(payload,str) or len(payload.encode('utf-8'))>MAX_BYTES:raise ValueError('官方資料格式或大小不正確。')
    payload=payload.lstrip('\ufeff').strip()
    if not payload or payload.startswith(('<','{')):raise ValueError('來源沒有可解析資料表，不接受 HTML 外殼或未知包裝。')
    if payload.startswith('['):
        data=json.loads(payload,parse_float=Decimal,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('無效數值')))
    else:
        reader=csv.DictReader(io.StringIO(payload))
        if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames):raise ValueError('CSV 缺少欄位或重複欄位。')
        data=list(reader)
    if not isinstance(data,list) or not 1<=len(data)<=5000 or any(not isinstance(row,dict) for row in data):
        raise ValueError('官方資料表為空、格式改變或超過列數限制。')
    return data


def roc_year(value):
    raw=_key(value)
    if not re.fullmatch(r'\d{1,4}',raw) or int(raw)==0:raise ValueError('年度格式不正確。')
    year=int(raw)
    return year+1911 if len(raw)<=3 else year


def snapshot_date(value):
    raw=re.sub(r'[/.-]','',_key(value))
    if not re.fullmatch(r'\d{7,8}',raw):raise ValueError('出表日期格式不正確。')
    return date(roc_year(raw[:-4]),int(raw[-4:-2]),int(raw[-2:]))


def month_period(value):
    raw=re.sub(r'[/.-]','',_key(value))
    if not re.fullmatch(r'\d{5,6}',raw):raise ValueError('資料年月格式不正確。')
    year,month=roc_year(raw[:-2]),int(raw[-2:])
    return date(year,month,1),date(year,month,calendar.monthrange(year,month)[1])


def capabilities(kind):
    if kind not in ('revenue','financials','balance'):raise ValueError('不支援的台灣摘要種類。')
    provided={'revenue':{'revenue','revenue-yoy'},'financials':set(FIELDS),'balance':{'total-liabilities'}}[kind]
    return {metric:{'provided':metric in provided,'derived':metric=='gross-margin' and kind=='financials',
        'history':'latest-provider-snapshot-only','frequency_hours':24,'currency':'TWD',
        'reporting_scope':'requires-confirmation','filing_date':'not-provided',
        'source_date':'provider-output-date','requires_calendar':kind!='revenue',
        'unsupported_reason':None if metric in provided or metric=='gross-margin' and kind=='financials' else 'not-in-this-dataset'} for metric in METRICS}


def parse_taiwan(payload,source_id,kind,url,issuers:dict[str,TwIssuer]):
    capabilities(kind)
    location=urlsplit(url)
    hosts={'openapi.twse.com.tw','mopsfin.twse.com.tw'} if source_id.startswith('twse-') else {'www.tpex.org.tw','tpex.org.tw'} if source_id.startswith('tpex-') else set()
    if (not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',source_id) or location.scheme!='https' or
        location.hostname not in hosts or location.username or location.password or location.port not in (None,443)):
        raise ValueError('來源須為已登錄的 TWSE／TPEx HTTPS 入口。')
    result=TwResult([],[],[],[])
    required={'公司代號','出表日期'}|({'資料年月','營業收入-當月營收'} if kind=='revenue' else {'年度','季別','營業收入' if kind=='financials' else '負債總計'})
    data=rows(payload)
    if not required<=fields(data[0]).keys():raise ValueError('官方摘要欄位變動。')
    for raw in data:
        values=fields(raw)
        if '公司代號' not in values:raise ValueError('官方摘要缺少公司識別。')
        code=_key(values['公司代號'][1])
        issuer=issuers.get(code)
        if not issuer:continue
        if not required<=values.keys():raise ValueError('官方公司資料缺少必要欄位。')
        asof=snapshot_date(values['出表日期'][1])
        if kind=='revenue':
            start,end=month_period(values['資料年月'][1]);basis='monthly';quarter=None
        else:
            year=roc_year(values['年度'][1]);season=_key(values['季別'][1])
            if not re.fullmatch('[1-4]',season):raise ValueError('季別須為 1–4。')
            quarter=int(season)
            if issuer.fiscal_year_end!=(12,31):
                result.unresolved.append({'company_id':issuer.company_id,'source_id':source_id,'reason':'calendar-unverified',
                    'reported_year':values['年度'][1],'reported_quarter':season,'source_as_of':asof,'raw':raw})
                continue
            month=quarter*3;end=date(year,month,calendar.monthrange(year,month)[1])
            start=end if kind=='balance' else date(year,1,1)
            basis='instant' if kind=='balance' else 'annual' if quarter==4 else 'ytd'
        statement=f'{source_id}:{code}:{start.isoformat()}/{end.isoformat()}:{asof.isoformat()}'
        limitations=['出表日期是來源彙整日，未提供公司正式申報日。']
        if issuer.scope=='issuer-summary-unspecified':limitations.append('此摘要未明列合併／個體旗標，口徑仍需核對。')
        row_values={}
        def record(metric,choices,*,period_start=start,period_end=end,reported_basis=basis):
            chosen=None
            for key in choices:
                if key in values:
                    original,raw_number=values[key];parsed=number(raw_number)
                    if parsed is not None:chosen=(original,parsed);break
            if chosen is None:
                result.gaps.append({'company_id':issuer.company_id,'metric_id':metric,'reason':'missing-value'});return
            field,parsed=chosen
            unit=METRICS[metric][1];factor=Decimal(1000) if unit=='amount' else Decimal(1)
            context=FinancialContext(issuer.company_id,FAMILY,metric,period_start,period_end,reported_basis,
                scope=issuer.scope,unit=unit,currency='TWD',share_class=issuer.share_class if metric.startswith('eps-') else '')
            try:
                fact=RawFact(context,statement,str(field),'TWD thousand' if unit=='amount' else 'TWD/share' if unit=='per-share' else 'percent',
                    parsed,None,url,multiplier=factor,source_as_of=asof)
                normalized=fact.normalized_value
            except ValueError:
                result.gaps.append({'company_id':issuer.company_id,'metric_id':metric,'reason':'precision-not-supported','raw_field':field});return
            value=FinancialValue(context,normalized,uuid.uuid5(uuid.NAMESPACE_URL,'tw-value:'+str(fact.fact_id)+':'+decimal_text(normalized)),statement,
                start.year if kind!='revenue' else None,quarter)
            result.records.append(TwRecord(value,fact,raw,tuple(limitations)))
            row_values[metric]=value
        if kind=='revenue':
            record('revenue',('營業收入-當月營收',))
            record('revenue-yoy',('營業收入-去年同月增減(%)',))
            # Comparative facts are explicitly supplied in this same monthly row.
            previous_start=date(start.year-1,start.month,1)
            previous_end=date(start.year-1,start.month,calendar.monthrange(start.year-1,start.month)[1])
            current=row_values.get('revenue')
            record('revenue',('營業收入-去年當月營收',),period_start=previous_start,period_end=previous_end)
            prior=row_values.get('revenue')
            if current and prior and current is not prior and 'revenue-yoy' not in row_values:
                try:result.derived.append((revenue_yoy(current,prior),asof,tuple(limitations)))
                except FinancialGap as error:result.gaps.append({'company_id':issuer.company_id,'metric_id':'revenue-yoy','reason':str(error)})
        elif kind=='financials':
            for metric,choices in FIELDS.items():record(metric,choices)
            if row_values.get('gross-profit') and row_values.get('revenue'):
                try:result.derived.append((gross_margin(row_values['gross-profit'],row_values['revenue']),asof,tuple(limitations)))
                except FinancialGap as error:result.gaps.append({'company_id':issuer.company_id,'metric_id':'gross-margin','reason':str(error)})
        else:record('total-liabilities',('負債總計',))
    return result


def persist_taiwan(connection,result:TwResult):
    from .financial_store import register_metrics,save_official,save_derived,lock_groups
    register_metrics(connection)
    lock_groups(connection,[row.value.context.group_id for row in result.records]+[item.context.group_id for item,_,_ in result.derived])
    mapped={};saved=[]
    for record in result.records:
        outcome=save_official(connection,record.value,(record.fact,),limitations=' '.join(record.limitations),
            payloads={str(record.fact.fact_id):{'row':record.raw,'snapshot_as_of':record.fact.source_as_of}})
        if outcome['observation_id']:mapped[record.value.observation_id]=outcome['observation_id']
        saved.append(outcome)
    for derived,asof,limitations in result.derived:
        if all(key in mapped for key in derived.input_ids):
            output=replace(derived,input_ids=tuple(mapped[key] for key in derived.input_ids))
            saved.append(save_derived(connection,output,source_as_of=asof,limitations=' '.join(limitations)))
    return {'new_revisions':sum(item['new_revision'] for item in saved),'active_changes':sum(item['active_changed'] for item in saved),
        'needs_review':sum(item['status']=='needs-verification' for item in saved)+len(result.unresolved),'gaps':result.gaps,'items':saved}
