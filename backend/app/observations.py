"""Append actual revisions; retrieval timestamps never create new values."""
import hashlib,json
from decimal import Decimal,InvalidOperation
from datetime import date
from sqlalchemy import select,func
from .models import Indicator,IndicatorObservation


def save_observation(session,data):
    data=dict(data)
    definition=session.get(Indicator,data['indicator_id'])
    if definition is None:raise ValueError('指標定義不存在')
    try:value=Decimal(str(data['value']))
    except (InvalidOperation,KeyError):raise ValueError('觀測缺少有效數值')
    if not value.is_finite():raise ValueError('觀測值必須有限')
    data['value']=value
    for key in ('period_start','period_end'):
        if isinstance(data.get(key),str):data[key]=date.fromisoformat(data[key])
        if type(data.get(key)) is not date:raise ValueError('觀測必須有明確起迄')
    if data['period_start']>data['period_end']:raise ValueError('觀測期間順序錯誤')
    for key in ('document_identity','dataset','entity','original_period','basis','scope','unit','url','raw_excerpt'):
        if not isinstance(data.get(key),str) or not data[key].strip():raise ValueError(f'觀測缺少 {key}')
    if not data['url'].startswith('https://'):raise ValueError('觀測來源須為 HTTPS')
    valid=data.get('valid',True)
    mismatch=(data['basis']!=definition.basis or data['unit']!=definition.unit or data.get('currency')!=definition.data.get('currency'))
    if mismatch and valid:raise ValueError('觀測單位／幣別／口徑不符合定義；修正不適用值須明示 valid=false')
    if not valid and not data.get('invalid_reason'):raise ValueError('不適用修訂須有理由')
    if data['unit']=='percent' and valid and not Decimal(0)<=value<=Decimal(100):raise ValueError('比例超出有效範圍')
    identity_fields=[data['indicator_id'],data['source_id'],data['dataset'] or data['document_identity'],data['entity'],data['period_start'].isoformat(),data['period_end'].isoformat(),definition.basis]
    identity=hashlib.sha256(json.dumps(identity_fields,ensure_ascii=False).encode()).hexdigest()
    content={k:str(data.get(k)) for k in ('value','basis','scope','unit','currency','valid','invalid_reason')}
    content['value']=str(value.normalize())
    content['valid']=str(valid)
    digest=hashlib.sha256(json.dumps(content,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    latest=session.scalar(select(IndicatorObservation).where(IndicatorObservation.identity==identity).order_by(IndicatorObservation.revision.desc()).limit(1))
    if latest and latest.content_hash==digest:return False
    row=IndicatorObservation(**data,identity=identity,content_hash=digest,revision=latest.revision+1 if latest else 1)
    session.add(row);session.flush()
    return True


def latest_query(indicator_ids=None):
    ranked=select(IndicatorObservation.id,func.row_number().over(partition_by=IndicatorObservation.identity,order_by=(IndicatorObservation.revision.desc(),IndicatorObservation.id.desc())).label('rank'))
    if indicator_ids is not None:ranked=ranked.where(IndicatorObservation.indicator_id.in_(indicator_ids))
    ranked=ranked.subquery()
    return select(IndicatorObservation).join(ranked,ranked.c.id==IndicatorObservation.id).where(ranked.c.rank==1).order_by(IndicatorObservation.period_end.desc(),IndicatorObservation.id.desc())

def latest_observations(session,indicator_id,limit=None):
    q=latest_query([indicator_id])
    return list(session.scalars(q.limit(limit) if limit is not None else q))
