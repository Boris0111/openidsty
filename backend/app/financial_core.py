"""Exact financial identities and conservative, traceable Decimal derivations."""
from dataclasses import dataclass, asdict, replace
import calendar
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_EVEN
import hashlib
import json
import re
import uuid
from urllib.parse import urlsplit

FORMULA_VERSION='financial-v1'
QUANTUM=Decimal('0.0000000001')
METRICS={
    'revenue':('營收','amount',True,('monthly','quarterly','ytd','annual')),
    'revenue-yoy':('營收年增率','percent',False,('monthly','quarterly','annual')),
    'gross-profit':('毛利','amount',True,('quarterly','ytd','annual')),
    'gross-margin':('毛利率','percent',False,('quarterly','ytd','annual')),
    'operating-income':('營業利益','amount',True,('quarterly','ytd','annual')),
    'net-income-parent':('歸屬母公司／股東淨利','amount',True,('quarterly','ytd','annual')),
    'net-income-total':('淨利（總額）','amount',True,('quarterly','ytd','annual')),
    'eps-basic':('基本 EPS','per-share',False,('quarterly','ytd','annual')),
    'eps-diluted':('稀釋 EPS','per-share',False,('quarterly','ytd','annual')),
    'operating-cash-flow':('營業現金流','amount',True,('quarterly','ytd','annual')),
    'capex':('購置不動產廠房設備現金支出','amount',True,('quarterly','ytd','annual')),
    'cash-and-equivalents':('現金及約當現金','amount',False,('instant',)),
    'total-liabilities':('負債總額','amount',False,('instant',)),
}


class FinancialGap(ValueError):
    """A missing prerequisite is a gap, never a fabricated zero."""


def decimal_value(value):
    if isinstance(value,(float,bool)) or not isinstance(value,(str,int,Decimal)):
        raise ValueError('財務數值必須是十進位字串、整數或 Decimal。')
    if len(str(value))>120:
        raise ValueError('財務數值超過可保存精度。')
    try:
        number=Decimal(value)
        with localcontext() as context:
            context.prec=50
            if not number.is_finite() or number.adjusted()>27 or number!=number.quantize(QUANTUM):
                raise ValueError('財務數值超過 Numeric(38,10) 或不是有限數。')
    except InvalidOperation:
        raise ValueError('財務數值格式不正確。') from None
    return number


def decimal_text(value):
    number=decimal_value(value)
    return '0' if number==0 else format(number,'f').rstrip('0').rstrip('.') if number.as_tuple().exponent<0 else format(number,'f')


def _json(value):
    if isinstance(value,Decimal):return decimal_text(value)
    if isinstance(value,date):return value.isoformat()
    if isinstance(value,float):raise ValueError('身分不可包含 float。')
    if isinstance(value,dict):
        if any(not isinstance(key,str) for key in value):raise ValueError('身分欄位名稱必須是文字。')
        return {key:_json(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [_json(item) for item in value]
    if value is None or isinstance(value,(str,int,bool)):return value
    raise ValueError('身分包含不支援的值。')


def fingerprint(value):
    return hashlib.sha256(json.dumps(_json(value),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class FinancialContext:
    company_id:str
    source_family:str
    metric_id:str
    period_start:date
    period_end:date
    basis:str
    scope:str='consolidated'
    unit:str='amount'
    currency:str=''
    share_class:str=''

    def __post_init__(self):
        if not re.fullmatch(r'company-[a-z0-9]+(?:-[a-z0-9]+)*',self.company_id):raise ValueError('公司身分不正確。')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',self.source_family):raise ValueError('來源族不正確。')
        if self.metric_id not in METRICS:raise ValueError('不支援的財務指標。')
        _,unit,_,bases=METRICS[self.metric_id]
        if self.unit!=unit or self.basis not in bases:raise ValueError('指標單位或期間口徑不相容。')
        if type(self.period_start) is not date or type(self.period_end) is not date or self.period_end<self.period_start:
            raise ValueError('原始期間不正確。')
        if self.basis=='instant' and self.period_start!=self.period_end:raise ValueError('期末餘額須保留同一期末日期。')
        if self.basis!='instant' and self.period_start==self.period_end:raise ValueError('流量須保留實際起迄日期。')
        if self.basis=='monthly' and (self.period_start.day!=1 or self.period_start.year!=self.period_end.year or
            self.period_start.month!=self.period_end.month or self.period_end.day!=calendar.monthrange(self.period_end.year,self.period_end.month)[1]):
            raise ValueError('月營收須保留完整原始月份。')
        if self.currency and not re.fullmatch('[A-Z]{3}',self.currency):raise ValueError('幣別必須是三碼原幣代碼。')
        if self.unit in ('amount','per-share') and not self.currency:raise ValueError('金額與 EPS 不得缺少原幣。')
        if not self.scope or len(self.scope)>100 or len(self.share_class)>100:raise ValueError('報表範圍或股別不正確。')
        if self.metric_id.startswith('eps-') and not self.share_class:raise ValueError('EPS 必須明列股別或 unspecified。')

    @property
    def group_id(self):
        return fingerprint({'schema':'financial-identity-v1',**asdict(self)})


@dataclass(frozen=True)
class RawFact:
    context:FinancialContext
    accession:str
    tag:str
    raw_unit:str
    value:Decimal|None
    filed_at:date|None
    source_url:str
    dimensions:tuple=()
    multiplier:Decimal=Decimal(1)

    def __post_init__(self):
        for value in (self.accession,self.tag,self.raw_unit):
            if not isinstance(value,str) or not value or len(value)>500:raise ValueError('原始 fact 身分不正確。')
        url=urlsplit(self.source_url)
        if url.scheme!='https' or not url.hostname or url.username or url.password or any(ord(char)<33 for char in self.source_url):
            raise ValueError('原始 fact 必須保留不含帳密的 HTTPS 官方文件來源。')
        if self.filed_at is not None and type(self.filed_at) is not date:raise ValueError('申報日須保留日期精度。')
        if self.value is not None:object.__setattr__(self,'value',decimal_value(self.value))
        object.__setattr__(self,'multiplier',decimal_value(self.multiplier))
        if not self.multiplier or abs(self.multiplier)>Decimal('1000000000'):raise ValueError('原始單位換算不正確。')
        if len(dict(self.dimensions))!=len(self.dimensions):raise ValueError('原始 context 不得重複維度。')

    @property
    def context_hash(self):
        # A taxonomy-to-metric mapping or derived period label is not raw XBRL context.
        context=self.context
        return fingerprint({'start':context.period_start,'end':context.period_end,'scope':context.scope,
            'currency':context.currency,'share_class':context.share_class,'raw_unit':self.raw_unit,
            'dimensions':sorted(self.dimensions)})

    @property
    def fact_id(self):
        key={'company_id':self.context.company_id,'source_family':self.context.source_family,
            'accession':self.accession,'tag':self.tag,'context_hash':self.context_hash}
        return uuid.uuid5(uuid.NAMESPACE_URL,'financial-fact-v1:'+fingerprint(key))

    @property
    def normalized_value(self):
        if self.value is None:return None
        with localcontext() as context:
            context.prec=50
            return decimal_value(self.value*self.multiplier)


@dataclass(frozen=True)
class FinancialValue:
    context:FinancialContext
    value:Decimal
    observation_id:uuid.UUID
    statement_id:str
    fiscal_year:int|None=None
    fiscal_quarter:int|None=None

    def __post_init__(self):
        object.__setattr__(self,'value',decimal_value(self.value))
        if not self.statement_id or len(self.statement_id)>500:raise ValueError('數值必須保留申報身分。')
        if not isinstance(self.observation_id,uuid.UUID):raise ValueError('觀測身分須為 UUID。')
        if self.context.metric_id=='capex' and self.value<0:raise ValueError('Capex 須正規化為正值購置支出，不可直接取絕對值猜測。')
        if self.fiscal_quarter is not None and self.fiscal_quarter not in (1,2,3,4):raise ValueError('財季不正確。')

    @property
    def semantic_hash(self):
        # Filing and fetch times are provenance, not a numerical change.
        return fingerprint({'group_id':self.context.group_id,'value':self.value})


@dataclass(frozen=True)
class Derivation:
    context:FinancialContext
    value:Decimal
    formula_version:str
    input_ids:tuple[uuid.UUID,...]


def _compatible(left,right,*,same_period=True,same_statement=True):
    a,b=left.context,right.context
    for field in ('company_id','source_family','scope','currency','share_class'):
        if getattr(a,field)!=getattr(b,field):raise FinancialGap('公司、來源、幣別、會計範圍或股別不一致。')
    if same_period and (a.period_start,a.period_end,a.basis)!=(b.period_start,b.period_end,b.basis):
        raise FinancialGap('原始期間或單季／累計口徑不同。')
    if same_statement and left.statement_id!=right.statement_id:raise FinancialGap('無法確認來自相容申報，保留原值。')


def _rounded(value):
    return decimal_value(value.quantize(QUANTUM,rounding=ROUND_HALF_EVEN))


def gross_margin(gross_profit,revenue):
    _compatible(gross_profit,revenue)
    if (gross_profit.context.metric_id,revenue.context.metric_id)!=('gross-profit','revenue'):
        raise FinancialGap('毛利率只能由同期間毛利與營收計算。')
    if revenue.value<=0:raise FinancialGap('營收不是正值，無法產生可比較毛利率。')
    with localcontext() as context:
        context.prec=50
        value=_rounded(gross_profit.value/revenue.value*100)
    return Derivation(replace(revenue.context,metric_id='gross-margin',unit='percent'),value,
        FORMULA_VERSION+':gross-margin',(gross_profit.observation_id,revenue.observation_id))


def single_quarter(current,previous,*,verified_filings:frozenset[str]|None=None):
    _compatible(current,previous,same_period=False,same_statement=False)
    a,b=current.context,previous.context
    if a.metric_id!=b.metric_id or not METRICS[a.metric_id][2] or a.unit!='amount':
        raise FinancialGap('EPS、比率與期末餘額不可由累計相減。')
    if a.basis not in ('ytd','annual') or b.basis!='ytd' or a.period_start!=b.period_start:
        raise FinancialGap('需要同會計年度起點的相容累計。')
    if current.statement_id!=previous.statement_id and verified_filings!=frozenset((current.statement_id,previous.statement_id)):
        raise FinancialGap('不同申報的累計須先核對是否重編，不能自動相減。')
    start=b.period_end+timedelta(days=1)
    if not 70<=(a.period_end-start).days+1<=110:raise FinancialGap('相減後不是已核對的單季長度。')
    with localcontext() as context:
        context.prec=50
        value=_rounded(current.value-previous.value)
    if a.metric_id=='capex' and value<0:raise FinancialGap('累計支出下降，須核對重編或符號定義。')
    return Derivation(replace(a,period_start=start,basis='quarterly'),value,
        FORMULA_VERSION+':ytd-difference',(current.observation_id,previous.observation_id))


def revenue_yoy(current,previous):
    _compatible(current,previous,same_period=False,same_statement=False)
    a,b=current.context,previous.context
    if a.metric_id!='revenue' or b.metric_id!='revenue' or a.basis!=b.basis or a.basis not in ('monthly','quarterly','annual'):
        raise FinancialGap('營收年增需要相同期間口徑。')
    if a.basis=='quarterly' and (current.fiscal_quarter is None or previous.fiscal_quarter!=current.fiscal_quarter
        or current.fiscal_year is None or previous.fiscal_year!=current.fiscal_year-1):
        raise FinancialGap('未確認相同財季，不能按曆年季度猜測。')
    if a.basis=='monthly' and (a.period_end.year!=b.period_end.year+1 or a.period_end.month!=b.period_end.month):
        raise FinancialGap('月營收年增需要同一月份。')
    if not 350<=(a.period_end-b.period_end).days<=380 or abs((a.period_end-a.period_start).days-(b.period_end-b.period_start).days)>14:
        raise FinancialGap('期間無法對齊，不能視為同財季年增。')
    if previous.value<=0:raise FinancialGap('前期營收非正值，年增率不適用。')
    with localcontext() as context:
        context.prec=50
        value=_rounded((current.value/previous.value-1)*100)
    return Derivation(replace(a,metric_id='revenue-yoy',unit='percent'),value,
        FORMULA_VERSION+':revenue-yoy',(current.observation_id,previous.observation_id))


def source_priority(source_family,preferred_family,*,provenance_kind='official'):
    if not preferred_family:raise FinancialGap('公司主要申報來源尚未設定。')
    if provenance_kind not in ('official','manual-official','derived','legacy-import'):raise ValueError('來源性質不正確。')
    if provenance_kind=='derived':return 4
    if provenance_kind=='legacy-import':return 3
    if source_family==preferred_family:return 1 if provenance_kind=='manual-official' else 0
    return 2
