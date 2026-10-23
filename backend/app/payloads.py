"""Canonical JSON for request budgets, job results and raw source payloads."""
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
import json

QUANTUM=Decimal('0.0000000001')


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


def encoded(value):
    return json.dumps(_json(value),ensure_ascii=False,sort_keys=True,separators=(',',':'))


def raw_payload(value):
    # Original source cells may exceed canonical Numeric precision. Keep their
    # exact decimal text as evidence; this never makes them canonical values.
    if isinstance(value,Decimal):
        if not value.is_finite():raise ValueError('原始 payload 不得包含非有限數。')
        return str(value)
    if isinstance(value,dict):
        if any(not isinstance(key,str) for key in value):raise ValueError('原始 payload 欄位須為文字。')
        return {key:raw_payload(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [raw_payload(item) for item in value]
    return _json(value)
