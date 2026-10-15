"""Read-only, scope-preserving observations and comparisons."""
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from .models import Indicator,ThemeIndicator,IndicatorObservation,Source
from .observations import latest_observations
from .financial_indicators import runtime_source_id


def decimal_text(value):
    return format(value,'f').rstrip('0').rstrip('.') if '.' in format(value,'f') else format(value,'f')


def comparable(a,b):
    return a.valid and b.valid and all(getattr(a,k)==getattr(b,k) for k in ('indicator_id','unit','currency','basis','scope')) and a.period_start>b.period_end


def comparison(latest,previous):
    reason=None;value=None
    if not latest:reason='尚無有效數值'
    elif not previous:reason='缺少前期'
    elif not comparable(latest,previous):reason='單位、幣別、口徑、範圍或期間不可比較'
    elif latest.unit=='percent':value=latest.value-previous.value
    elif previous.value==0:reason='前期為零，增幅無法計算'
    else:value=(latest.value-previous.value)/abs(previous.value)*Decimal(100)
    return {'value':decimal_text(value.quantize(Decimal('0.0001'))) if value is not None else None,'unit':'percentage-point' if latest and latest.unit=='percent' else 'percent','reason':reason,'previous_period':previous.original_period if previous else None}


def observation_payload(row):
    fields=('id','identity','revision','content_hash','source_id','original_period','period_start','period_end','basis','scope','unit','currency','published_at','reported_at','published_precision','date_semantics','fetched_at','url','raw_excerpt','valid','invalid_reason')
    return {**{key:getattr(row,key) for key in fields},'value':decimal_text(row.value)}


def indicators_payload(session,theme,limit=12,reference=None):
    reference=reference or date.today();items=[]
    definitions=list(session.scalars(select(Indicator).join(ThemeIndicator).where(ThemeIndicator.theme_id==theme.id).order_by(Indicator.id)))
    for definition in definitions:
        current=latest_observations(session,definition.id)[:limit]
        valid=[r for r in current if r.valid]
        latest=valid[0] if valid else None
        sid=definition.data['source_id'] if definition.kind=='direct' else runtime_source_id(definition.data)
        source=session.get(Source,sid)
        gaps=[]
        if not latest:gaps.append('尚未取得有效數值；不補零')
        invalid=[r for r in current if not r.valid]
        if invalid:gaps.extend(f'{r.original_period}：{r.invalid_reason}' for r in invalid)
        age=(reference-latest.period_end).days if latest else None
        stale=age is not None and age>(60 if definition.frequency=='monthly' else 180)
        if stale:gaps.append(f'最新期別已距今 {age} 日，資料過舊')
        warning=source.error if source and source.status in ('failed','partial','configuration_required') else None
        if not source:gaps.append('來源尚未註冊')
        if warning:gaps.append(f'來源 {sid}：{warning}')
        if definition.kind=='proxy':gaps.append('代理總營收未提供題材專屬收入')
        previous=current[current.index(latest)+1] if latest and current.index(latest)+1<len(current) else None
        history=list(session.scalars(select(IndicatorObservation).where(IndicatorObservation.identity.in_([r.identity for r in current])).order_by(IndicatorObservation.period_end.desc(),IndicatorObservation.revision.desc()))) if current else []
        items.append({**definition.data,'status':'unavailable' if not latest else 'stale' if stale else 'available','data_age_days':age,'source':{'id':sid,'status':source.status if source else 'unregistered','last_success':source.last_success if source else None,'error':warning},'latest':observation_payload(latest) if latest else None,'observations':[observation_payload(r) for r in current],'revisions':[observation_payload(r) for r in history],'comparison':comparison(latest,previous),'gaps':gaps,'trend':[observation_payload(r) for r in reversed(valid) if latest and (r.identity==latest.identity or comparable(latest,r))]})
    return {'theme_id':theme.id,'as_of':reference,'indicators':items,'gaps':[] if items else ['尚無指標設定']}
