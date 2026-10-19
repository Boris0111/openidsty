"""Bounded financial reads. Values remain exact; incompatible series stay separate."""
import base64,json,re,uuid
from datetime import date
from typing import Literal
from fastapi import APIRouter,Depends,Query
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release,entity,envelope,summary,claims_payload,reader_gaps
from .research_compile import digest
from .financial_core import METRICS,decimal_text

router=APIRouter(prefix='/api/v2',tags=['research-financials'])
Basis=Literal['monthly','quarterly','ytd','annual','instant']
OBS_COLUMNS='o.observation_id,o.revision,o.value,o.filed_at,o.source_as_of,o.recorded_at,o.supersedes,o.provenance_kind,o.limitations'
LATEST="""JOIN LATERAL (SELECT * FROM research.financial_observations f WHERE f.group_id=g.group_id
    ORDER BY COALESCE(f.filed_at,f.source_as_of) DESC NULLS LAST,f.revision DESC LIMIT 1) o ON true"""
FORMULAS={'financial-v1:gross-margin':'input[0] / input[1] * 100',
    'financial-v1:revenue-yoy':'(input[0] / input[1] - 1) * 100','financial-v1:ytd-difference':'input[0] - input[1]'}


def company(session,release,identifier):
    row=entity(session,release,identifier)
    if row['kind']!='company':raise ResearchError(404,'company-not-found','找不到這家公司。')
    return row


def preferred(row):
    profile=row['data'].get('financial-reporting',{})
    return profile.get('primary-source-family') if profile.get('confidence')=='well-supported' else None


def as_of(session):return session.execute(text('SELECT transaction_timestamp()')).scalar_one()


def numeric(row):
    return {**{key:str(value) if isinstance(value,uuid.UUID) else value for key,value in row.items() if key not in ('n','period_rank')},
        'value':decimal_text(row['value']),'label':METRICS[row['metric_id']][0],
        'derived':row['provenance_kind']=='derived'}


def enrich(session,rows,release):
    """Two batch queries, with limits per observation, independent of history size."""
    if not rows:return []
    ids=[row['observation_id'] for row in rows]
    # OFFSET 0 keeps the security_barrier view a keyed lookup per cited fact instead of hashing every published fact.
    sources=session.execute(text('''SELECT ranked.* FROM (
        SELECT p.observation_id,f.fact_id,f.accession,f.tag,f.value,f.filed_at,f.source_url,
            f.raw_unit,f.multiplier,f.source_as_of,f.locator,
            row_number() OVER(PARTITION BY p.observation_id ORDER BY f.filed_at DESC NULLS LAST,f.fact_id) AS n
        FROM research.observation_provenance p CROSS JOIN LATERAL (
            SELECT * FROM research.financial_fact_citations c WHERE c.fact_id=p.fact_id OFFSET 0) f
        WHERE p.observation_id=ANY(CAST(:ids AS uuid[]))) ranked WHERE n<=21'''),{'ids':ids}).mappings().all()
    inputs=session.execute(text('''SELECT ranked.* FROM (SELECT d.observation_id AS target_id,d.input_id,d.ordinal,d.formula_version,
        g.company_id,g.metric_id,g.source_family,g.unit,g.group_id,g.period_start,g.period_end,g.basis,g.scope,g.currency,g.share_class,
        o.value,o.revision,o.provenance_kind,row_number() OVER(PARTITION BY d.observation_id ORDER BY d.ordinal) AS n FROM research.financial_derivations d
        JOIN research.financial_observations o ON o.observation_id=d.input_id JOIN research.financial_groups g USING(group_id)
        WHERE d.observation_id=ANY(CAST(:ids AS uuid[]))) ranked WHERE n<=3 ORDER BY target_id,ordinal'''),{'ids':ids}).mappings().all()
    result=[]
    for row in rows:
        item=numeric(row);facts=[fact for fact in sources if fact['observation_id']==row['observation_id']]
        item['sources']=[{'fact_id':str(fact['fact_id']),'accession':fact['accession'],'tag':fact['tag'],
            'raw_value':decimal_text(fact['value']) if fact['value'] is not None else None,
            **{key:fact[key] for key in ('filed_at','source_as_of','source_url','raw_unit','multiplier','locator')}} for fact in facts[:20]]
        item['sources_truncated']=len(facts)>20
        lineage=[part for part in inputs if part['target_id']==row['observation_id']]
        item['lineage']=[{**numeric({key:value for key,value in part.items() if key not in ('target_id','input_id','ordinal','formula_version')}),
            'observation_id':str(part['input_id']),'ordinal':part['ordinal'],
            'url':f"/api/v2/companies/{part['company_id']}/financials/observations/{part['input_id']}?release_id={release['release_id']}"} for part in lineage[:2]]
        item['lineage_truncated']=len(lineage)>2
        item['formula_version']=lineage[0]['formula_version'] if lineage else None
        item['formula']=FORMULAS.get(item['formula_version'])
        item['detail_url']=f"/api/v2/companies/{row['company_id']}/financials/observations/{row['observation_id']}?release_id={release['release_id']}"
        result.append(item)
    return result


def read_cursor(value,release,filters):
    if not value:return date.max,'f'*64
    try:
        token=json.loads(base64.urlsafe_b64decode(value+'='*(-len(value)%4)))
        if set(token)!={'release','filter','last'} or not isinstance(token['last'],list) or len(token['last'])!=2:raise ValueError()
        if token['release']!=str(release['release_id']) or token['filter']!=digest(filters):
            raise ResearchError(409,'cursor-conflict','研究版本或財務篩選已改變，請從第一頁讀取。')
        day,group=token['last']
        if not isinstance(group,str) or not re.fullmatch('[0-9a-f]{64}',group):raise ValueError()
        return date.fromisoformat(day),group
    except (ValueError,KeyError,TypeError,UnicodeError):raise ResearchError(422,'invalid-cursor','財務分頁格式不正確。') from None


@router.get('/companies/{company_id}/financials')
def financials(company_id:str,release_id:uuid.UUID|None=None,metric:str|None=Query(None,max_length=60),basis:Basis|None=None,
    currency:str|None=Query(None,pattern='^[A-Z]{3}$'),source_family:str|None=Query(None,max_length=80,pattern='^[a-z0-9]+(?:-[a-z0-9]+)*$'),
    scope:str|None=Query(None,max_length=100),all_scopes:bool=False,period_from:date|None=None,period_to:date|None=None,
    limit:int=Query(50,ge=1,le=100),cursor:str|None=Query(None,max_length=2048),session=Depends(get_research_session)):
    release=require_release(session,release_id);owner=company(session,release,company_id)
    if metric and metric not in METRICS:raise ResearchError(422,'invalid-metric','找不到這個財務指標。')
    if period_from and period_to and period_from>period_to:raise ResearchError(422,'invalid-period','期間起日不得晚於迄日。')
    filters={key:value for key,value in locals().copy().items() if key in ('company_id','metric','basis','currency','source_family','scope','all_scopes','period_from','period_to')}
    last_day,last_group=read_cursor(cursor,release,filters)
    parameters={**filters,'last_day':last_day,'last_group':last_group,'limit':limit+1}
    rows=session.execute(text('''WITH windowed AS (
        SELECT g.*,'''+OBS_COLUMNS+''',row_number() OVER(PARTITION BY source_family,metric_id,basis,scope,currency,share_class
            ORDER BY period_end DESC,period_start DESC,g.group_id DESC) AS period_rank
        FROM research.financial_groups g '''+LATEST+'''
        WHERE g.company_id=:company_id AND (CAST(:metric AS text) IS NULL OR metric_id=:metric)
        AND (CAST(:basis AS text) IS NULL OR basis=:basis) AND (CAST(:currency AS text) IS NULL OR currency=:currency)
        AND (CAST(:source_family AS text) IS NULL OR source_family=:source_family) AND (CAST(:scope AS text) IS NULL OR scope=:scope)
        AND (CAST(:scope AS text) IS NOT NULL OR :all_scopes OR g.scope='consolidated' OR NOT EXISTS(
            SELECT 1 FROM research.financial_groups other WHERE other.company_id=g.company_id AND other.metric_id=g.metric_id
            AND other.source_family=g.source_family AND other.period_start=g.period_start AND other.period_end=g.period_end
            AND other.basis=g.basis AND other.currency=g.currency AND other.share_class=g.share_class AND other.scope='consolidated'
            AND EXISTS(SELECT 1 FROM research.financial_observations valid WHERE valid.group_id=other.group_id))))
        SELECT * FROM windowed WHERE period_rank<=CASE basis WHEN 'monthly' THEN 36 WHEN 'annual' THEN 3 ELSE 8 END
        AND (CAST(:period_from AS date) IS NULL OR period_end>=:period_from)
        AND (CAST(:period_to AS date) IS NULL OR period_end<=:period_to)
        AND (period_end,group_id)<(CAST(:last_day AS date),:last_group)
        ORDER BY period_end DESC,group_id DESC LIMIT :limit'''),parameters).mappings().all()
    visible=rows[:limit];more=len(rows)>limit
    next_cursor=base64.urlsafe_b64encode(json.dumps({'release':str(release['release_id']),'filter':digest(filters),
        'last':[visible[-1]['period_end'].isoformat(),visible[-1]['group_id']]}).encode()).decode().rstrip('=') if more else None
    return envelope(release,{'as_of':as_of(session),'preferred_source_family':preferred(owner),
        'source_selection_gap':None if preferred(owner) else '尚未核對主要申報來源；各來源分開呈現。',
        'items':enrich(session,visible,release),'has_more':more,'next_cursor':next_cursor,
        'window':{'quarterly':8,'ytd':8,'instant':8,'annual':3,'monthly':36},
        'scope_selection':'explicit' if scope else 'all' if all_scopes else 'prefer-consolidated',
        'gaps':[] if visible else ['此條件內尚未取得財務；缺值不代表零或公司未申報。']})


@router.get('/companies/{company_id}/financials/observations/{observation_id}')
def observation(company_id:str,observation_id:uuid.UUID,release_id:uuid.UUID|None=None,
    before_revision:int|None=Query(None,ge=1),limit:int=Query(20,ge=1,le=100),session=Depends(get_research_session)):
    release=require_release(session,release_id);company(session,release,company_id)
    row=session.execute(text('SELECT g.*,'+OBS_COLUMNS+''' FROM research.financial_groups g
        JOIN research.financial_observations o USING(group_id) WHERE o.observation_id=:id AND g.company_id=:company'''),
        {'id':observation_id,'company':company_id}).mappings().first()
    if not row:raise ResearchError(404,'observation-not-found','找不到這家公司的財務觀測。')
    active=session.execute(text('SELECT o.observation_id FROM research.financial_groups g '+LATEST+' WHERE g.group_id=:id'),{'id':row['group_id']}).scalar_one()
    history=session.execute(text('SELECT g.*,'+OBS_COLUMNS+''' FROM research.financial_groups g
        JOIN research.financial_observations o USING(group_id) WHERE g.group_id=:group
        AND (CAST(:before AS integer) IS NULL OR o.revision<:before) ORDER BY o.revision DESC LIMIT :limit'''),
        {'group':row['group_id'],'before':before_revision,'limit':limit+1}).mappings().all()
    return envelope(release,{'as_of':as_of(session),'observation':enrich(session,[row],release)[0],
        'active_observation_id':str(active),'revisions':enrich(session,history[:limit],release),
        'has_more':len(history)>limit,'next_before_revision':history[limit-1]['revision'] if len(history)>limit else None})


def comparison_reasons(values,missing,unverified,ambiguous):
    reasons=[]
    if missing:reasons.append('部分公司未取得此指標。')
    if unverified:reasons.append('部分公司尚未核對主要申報來源。')
    if ambiguous:reasons.append('同一期間有多個來源或會計範圍，不能任選數值。')
    if not values:return reasons
    for fields,message in [(('period_start','period_end','basis'),'實際期間或單季／累計／全年／期末口徑不同。'),
        (('unit',),'指標單位不同。'),(('scope',),'申報範圍不同。')]:
        if len({tuple(row[key] for key in fields) for row in values})>1:reasons.append(message)
    if any(row['scope']!='consolidated' for row in values):reasons.append('尚未全部核對為合併報表範圍。')
    if values[0]['unit']!='percent' and len({row['currency'] for row in values})>1:reasons.append('原幣不同；不自動換匯或排名。')
    if values[0]['unit']=='per-share' and (len({row['share_class'] for row in values})>1 or
        any(row['share_class'] in ('','unspecified','unknown') for row in values)):
        reasons.append('EPS 股別或 ADR／普通股口徑不同或尚未核對。')
    if any(row['provenance_kind']=='legacy-import' for row in values):reasons.append('含尚未核對原始申報的舊版數值。')
    return reasons


@router.get('/compare')
def compare(company_ids:str=Query(...,max_length=850),basis:Literal['monthly','quarterly','ytd','annual']='annual',
    release_id:uuid.UUID|None=None,session=Depends(get_research_session)):
    identifiers=company_ids.split(',')
    if not 2<=len(identifiers)<=4 or len(set(identifiers))!=len(identifiers):raise ResearchError(422,'invalid-comparison','比較須選擇 2 至 4 家不同公司。')
    release=require_release(session,release_id);profiles=[company(session,release,key) for key in identifiers]
    offerings=session.execute(text('''SELECT ranked.* FROM (SELECT o.company_id,o.product_id,p.name,o.role_id,r.name AS role_name,
        o.conditions,row_number() OVER(PARTITION BY o.company_id ORDER BY o.product_id,o.role_id) AS n
        FROM research.company_offerings o JOIN research.entity_snapshots p ON p.release_id=o.release_id AND p.entity_id=o.product_id
        JOIN research.entity_snapshots r ON r.release_id=o.release_id AND r.entity_id=o.role_id
        WHERE o.release_id=:release AND o.company_id=ANY(CAST(:ids AS text[]))) ranked WHERE n<=101'''),
        {'release':release['release_id'],'ids':identifiers}).mappings().all()
    financial=session.execute(text('''SELECT ranked.* FROM (SELECT g.*,'''+OBS_COLUMNS+''',dense_rank() OVER(
        PARTITION BY company_id,metric_id,source_family ORDER BY period_end DESC) AS period_rank,
        row_number() OVER(PARTITION BY company_id,metric_id,source_family ORDER BY period_end DESC,period_start DESC,g.group_id) AS n
        FROM research.financial_groups g '''+LATEST+''' WHERE g.company_id=ANY(CAST(:ids AS text[]))
        AND basis=CASE WHEN g.metric_id IN ('cash-and-equivalents','total-liabilities') THEN 'instant' ELSE :basis END
        AND (g.scope='consolidated' OR NOT EXISTS(SELECT 1 FROM research.financial_groups other
            WHERE other.company_id=g.company_id AND other.metric_id=g.metric_id AND other.source_family=g.source_family
            AND other.period_start=g.period_start AND other.period_end=g.period_end AND other.basis=g.basis
            AND other.scope='consolidated' AND EXISTS(SELECT 1 FROM research.financial_observations valid WHERE valid.group_id=other.group_id)))) ranked
        WHERE period_rank=1 AND n<=11 ORDER BY company_id,metric_id,source_family,group_id LIMIT 2001'''),{'ids':identifiers,'basis':basis}).mappings().all()
    if len(financial)>2000:raise ResearchError(422,'comparison-too-broad','來源組合過多，請先核對各公司的主要申報來源。')
    columns=[];selected={};unverified=[]
    for row in profiles:
        key=row['entity_id'];family=preferred(row)
        if not family:unverified.append(key)
        candidates=[value for value in financial if value['company_id']==key and (not family or value['source_family']==family)]
        # Prefer consolidated when present; retain other original scopes as explicit gaps.
        for metric in METRICS:
            values=[value for value in candidates if value['metric_id']==metric]
            consolidated=[value for value in values if value['scope']=='consolidated']
            selected[key,metric]=consolidated or values
        sections=re.split(r'^##\s+(.+?)\s*$',row['markdown'],flags=re.M)
        prose={sections[i]:sections[i+1].strip() for i in range(1,len(sections)-1,2)}
        claims,truncated=claims_payload(session,release,key)
        products=[dict(item) for item in offerings if item['company_id']==key]
        columns.append({**summary(row),'roles':[{'segment_id':role['segment-id'],'description':role['description']} for role in row['data'].get('roles',[])[:100]],
            'products':products[:100],'risks':prose.get('風險','')[:12000] or None,'business_model':prose.get('商業模式','')[:12000] or None,
            'claims':claims,'gaps':reader_gaps(row['data'].get('gaps')),'research_depth':row['data'].get('research-depth','basic'),
            'truncated':truncated or len(products)>100 or any(len(prose.get(heading,''))>12000 for heading in ('風險','商業模式')),'preferred_source_family':family})
    all_values={row['observation_id']:row for rows in selected.values() for row in rows[:2]}
    enriched={row['observation_id']:row for row in enrich(session,list(all_values.values()),release)}
    metrics=[]
    for metric,(label,*_) in METRICS.items():
        missing=[key for key in identifiers if not selected[key,metric]]
        ambiguous=[key for key in identifiers if len(selected[key,metric])>1]
        values=[item for key in identifiers for item in selected[key,metric]]
        reasons=comparison_reasons(values,missing,unverified,ambiguous)
        metrics.append({'metric_id':metric,'label':label,'comparable':not reasons,'reasons':reasons,
            'values':[enriched[str(item['observation_id'])] for key in identifiers for item in selected[key,metric][:2]],
            'missing_company_ids':missing,'ambiguous_company_ids':ambiguous,
            'candidates_truncated_company_ids':[key for key in identifiers if len(selected[key,metric])>2]})
    return envelope(release,{'as_of':as_of(session),'basis':basis,'companies':columns,'metrics':metrics,
        'policy':'保留原幣與實際期間；不自動換匯、EPS 換算或跨來源拼報表。'})
