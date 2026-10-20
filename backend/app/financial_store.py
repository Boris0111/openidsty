"""Append financial values; same-value filings add provenance without fake updates."""
import argparse
from dataclasses import asdict
from datetime import date
from decimal import Decimal
import json
import uuid
from sqlalchemy import text
from .financial_core import METRICS,FORMULA_VERSION,FinancialGap,FinancialValue,RawFact,Derivation,_json,decimal_value
from .research_db import writer_engine


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


def register_metrics(connection):
    for key,(label,unit,additive,bases) in METRICS.items():
        definition={'identity_version':'financial-identity-v1','additive':additive,'bases':list(bases),
            'percent_scale':'percentage-points' if unit=='percent' else None,
            'capex_scope':'cash-purchases-of-property-plant-equipment-positive' if key=='capex' else None}
        connection.execute(text('''INSERT INTO research.financial_metric_definitions(metric_id,label,unit,definition,formula_version)
            VALUES(:key,:label,:unit,CAST(:definition AS jsonb),:formula) ON CONFLICT(metric_id) DO NOTHING'''),
            {'key':key,'label':label,'unit':unit,'definition':encoded(definition),'formula':FORMULA_VERSION})
        stored=connection.execute(text('SELECT unit,definition,formula_version FROM research.financial_metric_definitions WHERE metric_id=:key'),{'key':key}).mappings().one()
        if (stored['unit'],stored['definition'],stored['formula_version'])!=(unit,definition,FORMULA_VERSION):
            raise ValueError('財務指標定義不一致，需明確遷移，不可偷偷改變既有值的意義。')


def lock_groups(connection,groups):
    for group in sorted(set(groups)):
        connection.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,38109075))'),{'key':group})


def save_fact(connection,fact:RawFact,payload=None):
    key=fact.fact_id
    connection.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,38109076))'),{'key':str(key)})
    stored=connection.execute(text('SELECT value,filed_at FROM research.financial_raw_facts WHERE fact_id=:id'),{'id':key}).mappings().first()
    if stored:
        if stored['value']!=fact.value or stored['filed_at']!=fact.filed_at:
            raise FinancialGap('同一申報／tag／context 的原始值變動，須核對來源版本，不覆寫舊 fact。')
        return key
    data={'original':raw_payload(payload or {}),'context':asdict(fact.context),'raw_unit':fact.raw_unit,
        'normalization_multiplier':fact.multiplier,'dimensions':list(fact.dimensions),'source_as_of':fact.source_as_of}
    connection.execute(text('''INSERT INTO research.financial_raw_facts(fact_id,company_id,source_family,accession,tag,
        context_hash,value,filed_at,source_url,payload) VALUES(:id,:company,:family,:accession,:tag,:context,:value,:filed,:url,CAST(:payload AS jsonb))'''),
        {'id':key,'company':fact.context.company_id,'family':fact.context.source_family,'accession':fact.accession,
         'tag':fact.tag,'context':fact.context_hash,'value':fact.value,'filed':fact.filed_at,'url':fact.source_url,'payload':encoded(data)})
    return key


def _save(connection,value,filed_at,kind,limitations,fact_ids=(),derivation=None,expected_supersedes=None,source_as_of=None):
    if filed_at is not None and type(filed_at) is not date:raise ValueError('申報日必須保留日期精度。')
    if source_as_of is not None and type(source_as_of) is not date:raise ValueError('來源彙整日必須保留日期精度。')
    context=value.context
    group=context.group_id
    connection.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,38109075))'),{'key':group})
    fields={**asdict(context),'group_id':group}
    names=','.join(fields)
    connection.execute(text('INSERT INTO research.financial_groups('+names+') VALUES('+','.join(':'+key for key in fields)+') ON CONFLICT(group_id) DO NOTHING'),fields)
    rows=connection.execute(text('''SELECT * FROM research.financial_observations WHERE group_id=:group
        ORDER BY COALESCE(filed_at,source_as_of) DESC NULLS LAST,revision DESC FOR UPDATE'''),{'group':group}).mappings().all()
    mode='filing' if filed_at else 'snapshot' if source_as_of else 'unknown'
    existing_modes={'filing' if row['filed_at'] else 'snapshot' if row['source_as_of'] else 'unknown' for row in rows}-{'unknown'}
    if mode!='unknown' and existing_modes-{mode}:
        raise FinancialGap('申報與彙整快照須分開來源族，不可把兩種日期當成同一版本順序。')
    current=rows[0] if rows else None
    same=current if current and current['semantic_hash']==value.semantic_hash else None
    incoming_date=filed_at or source_as_of
    current_date=(current['filed_at'] or current['source_as_of']) if current else None
    older=bool(current_date and (incoming_date is None or incoming_date<current_date))
    if older:
        same=next((row for row in rows if row['semantic_hash']==value.semantic_hash),None)
    if same:
        observation=same['observation_id']
        if filed_at and (same['filed_at'] is None or filed_at>same['filed_at']):
            # Only supporting-filing metadata advances; the numerical revision stays put.
            connection.execute(text('UPDATE research.financial_observations SET filed_at=:filed WHERE observation_id=:id'),{'id':observation,'filed':filed_at})
        if source_as_of and (same['source_as_of'] is None or source_as_of>same['source_as_of']):
            connection.execute(text('UPDATE research.financial_observations SET source_as_of=:asof WHERE observation_id=:id'),{'id':observation,'asof':source_as_of})
        revision=same['revision']
        created=False
    else:
        conflict=next((row for row in rows if (row['filed_at'] or row['source_as_of'])==incoming_date and row['semantic_hash']!=value.semantic_hash),None)
        if conflict and expected_supersedes!=conflict['observation_id']:
            return {'status':'needs-verification','observation_id':None,'new_revision':False,'active_changed':False,
                'reason':'同日／未知申報日的衝突需要較精確的修訂證據。'}
        observation=value.observation_id
        revision=max((row['revision'] for row in rows),default=0)+1
        prior=next((row['observation_id'] for row in rows if (row['filed_at'] or row['source_as_of']) is not None and incoming_date is not None and (row['filed_at'] or row['source_as_of'])<incoming_date),None) if older else current['observation_id'] if current else None
        connection.execute(text('''INSERT INTO research.financial_observations(observation_id,group_id,revision,value,
            semantic_hash,filed_at,supersedes,provenance_kind,limitations,source_as_of)
            VALUES(:id,:group,:revision,:value,:hash,:filed,:prior,:kind,:limitations,:asof)'''),
            {'id':observation,'group':group,'revision':revision,'value':value.value,'hash':value.semantic_hash,
             'filed':filed_at,'prior':prior,'kind':kind,'limitations':limitations,'asof':source_as_of})
        created=True
    for key in fact_ids:
        connection.execute(text('''INSERT INTO research.observation_provenance(observation_id,fact_id)
            VALUES(:id,:fact) ON CONFLICT DO NOTHING'''),{'id':observation,'fact':key})
    if derivation and created:
        for index,key in enumerate(derivation.input_ids):
            connection.execute(text('''INSERT INTO research.financial_derivations(observation_id,input_id,formula_version,ordinal)
                VALUES(:id,:input,:formula,:ordinal)'''),{'id':observation,'input':key,'formula':derivation.formula_version,'ordinal':index})
    return {'status':'saved','observation_id':observation,'revision':revision,'new_revision':created,
        'active_changed':not older and (current is None or current['semantic_hash']!=value.semantic_hash)}


def save_official(connection,value:FinancialValue,facts:tuple[RawFact,...],*,kind='official',limitations='',payloads=None,expected_supersedes=None):
    if kind not in ('official','manual-official'):raise ValueError('官方觀測必須區分自動或人工核對來源。')
    if not facts:raise ValueError('官方觀測不得缺少原始 fact。')
    if len({fact.filed_at for fact in facts})!=1:raise FinancialGap('不同申報日期不得拼成一個觀測。')
    if len({fact.source_as_of for fact in facts})!=1:raise FinancialGap('不同彙整日期不得拼成一個觀測。')
    if any(fact.context.group_id!=value.context.group_id or fact.accession!=value.statement_id or fact.normalized_value!=value.value for fact in facts):
        raise FinancialGap('原始 fact、申報、換算值與觀測不一致。')
    lock_groups(connection,[value.context.group_id])
    ids=[save_fact(connection,fact,(payloads or {}).get(str(fact.fact_id))) for fact in sorted(facts,key=lambda item:str(item.fact_id))]
    return _save(connection,value,facts[0].filed_at,kind,limitations,ids,expected_supersedes=expected_supersedes,source_as_of=facts[0].source_as_of)


def save_derived(connection,derived:Derivation,*,filed_at=None,limitations='',source_as_of=None):
    if derived.formula_version not in {FORMULA_VERSION+':'+key for key in ('gross-margin','ytd-difference','revenue-yoy')} or len(derived.input_ids)!=2:
        raise ValueError('衍生公式與輸入不正確。')
    inputs=connection.execute(text('''SELECT o.observation_id,g.company_id,g.source_family,g.scope,g.currency,g.share_class
        FROM research.financial_observations o JOIN research.financial_groups g USING(group_id)
        WHERE o.observation_id=ANY(CAST(:ids AS uuid[]))'''),{'ids':list(derived.input_ids)}).mappings().all()
    if len(inputs)!=2 or any(any(row[key]!=getattr(derived.context,key) for key in ('company_id','source_family','scope','currency','share_class')) for row in inputs):
        raise FinancialGap('衍生輸入不存在或跨公司／來源／範圍。')
    observation=uuid.uuid5(uuid.NAMESPACE_URL,'financial-derivation:'+derived.context.group_id+':'+str(derived.value)+':'+','.join(map(str,derived.input_ids)))
    value=FinancialValue(derived.context,decimal_value(derived.value),observation,'derived')
    previous=latest(connection,derived.context.group_id)
    expected=previous['observation_id'] if previous and previous['provenance_kind']=='derived' else None
    return _save(connection,value,filed_at,'derived',limitations,derivation=derived,expected_supersedes=expected,source_as_of=source_as_of)


def latest(connection,group_id):
    return connection.execute(text('''SELECT * FROM research.financial_observations WHERE group_id=:group
        ORDER BY COALESCE(filed_at,source_as_of) DESC NULLS LAST,revision DESC LIMIT 1'''),{'group':group_id}).mappings().first()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['definitions'])
    parser.parse_args()
    with writer_engine().begin() as connection:register_metrics(connection)
    print('Financial metric definitions verified')


if __name__=='__main__':main()
