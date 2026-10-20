"""Shared read-only queries, classification payloads and auditable coverage."""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, or_, func,case,and_,literal,union_all,true
from .models import Event, EventSegment, EventTheme, Segment, Theme, Role, Source
from .classify import rules

def columns(row, exclude=()):
    return {c.name:getattr(row,c.name) for c in row.__table__.columns if c.name not in exclude}

def event_order():
    return Event.routine.asc(), Event.published_at.desc().nullslast(), Event.id.desc()

def event_query(ticker=None, kind=None, industry=None, segment=None, theme=None, start=None, end=None, include_routine=False, relevance='direct'):
    query=select(Event)
    if ticker: query=query.where(Event.ticker==ticker)
    if kind: query=query.where(Event.kind==kind)
    if not include_routine: query=query.where(Event.routine.is_(False))
    if industry or segment:
        relation=select(EventSegment.event_id)
        if relevance!='all': relation=relation.where(EventSegment.relevance==relevance)
        if segment: relation=relation.where(EventSegment.segment_id==segment)
        if industry: relation=relation.join(Segment,EventSegment.segment_id==Segment.id).where(Segment.layer==industry)
        query=query.where(Event.id.in_(relation))
    if theme:
        relation=select(EventTheme.event_id).where(EventTheme.theme_id==theme)
        if relevance!='all': relation=relation.where(EventTheme.relevance==relevance)
        query=query.where(Event.id.in_(relation))
    if not (industry or segment or theme or ticker) and relevance!='all':
        content=or_(Event.id.in_(select(EventSegment.event_id).where(EventSegment.relevance==relevance)),
                    Event.id.in_(select(EventTheme.event_id).where(EventTheme.relevance==relevance)))
        if include_routine and relevance=='direct': content=or_(content,Event.routine.is_(True))
        query=query.where(content)
    if start: query=query.where(Event.published_at>=start)
    if end: query=query.where(Event.published_at<end)
    return query.order_by(*event_order())

def event_payloads(session, events, raw=False):
    ids=[e.id for e in events]
    names=session.info.setdefault('event_source_names',{})
    missing={e.source_id for e in events}-names.keys()
    if missing:names.update(session.execute(select(Source.id,Source.name).where(Source.id.in_(missing))).all())
    segments=defaultdict(list); themes=defaultdict(list)
    for model,field,target in [(EventSegment,'segment_id',segments),(EventTheme,'theme_id',themes)]:
        for link in session.scalars(select(model).where(model.event_id.in_(ids))):
            target[link.event_id].append({'id':getattr(link,field),'relevance':link.relevance,'evidence':link.evidence})
    return [dict(columns(e,() if raw else ('raw',)),source_name=names.get(e.source_id),segments=segments[e.id],themes=themes[e.id]) for e in events]

def theme_payload(theme):
    from .assessments import assessment_summary
    return dict(theme.data,prose=theme.prose,checked=theme.checked,assessment_summary=assessment_summary(theme))

def coverage(session, reference=None):
    reference=reference or datetime.now(timezone.utc)
    if reference.tzinfo is None: reference=reference.replace(tzinfo=timezone.utc)
    cutoff90=reference-timedelta(days=90); cutoff30=reference-timedelta(days=30)
    sources=list(session.scalars(select(Source).order_by(Source.id)))
    session.info['event_source_names']={source.id:source.name for source in sources}
    roles=defaultdict(set)
    for sid,ticker in session.execute(select(Role.segment_id,Role.ticker)):roles[sid].add(ticker)
    groups={'segment':list(session.scalars(select(Segment).order_by(Segment.id))),'theme':list(session.scalars(select(Theme).where(Theme.active.is_(True)).order_by(Theme.id)))}
    stats={};samples={}
    recent=and_(Event.lifecycle=='published',Event.published_at>=cutoff90,Event.published_at<=reference)
    for group,model,field in [('segment',EventSegment,EventSegment.segment_id),('theme',EventTheme,EventTheme.theme_id)]:
        direct=and_(model.relevance=='direct',Event.routine.is_(False),recent)
        q=select(field,
            func.count(func.distinct(case((and_(direct,Event.published_at>=cutoff30),Event.id)))).label('direct30'),
            func.count(func.distinct(case((direct,Event.id)))).label('direct90'),
            func.count(func.distinct(case((and_(model.relevance=='background',recent),Event.id)))).label('background'),
            func.count(func.distinct(case((Event.published_at.is_(None),Event.id)))).label('unknown')
        ).join(Event,Event.id==model.event_id).group_by(field)
        stats[group]={r[0]:tuple(r[1:]) for r in session.execute(q)}
        ranked=select(field.label('scope_id'),Event.id.label('event_id'),func.row_number().over(partition_by=field,order_by=(Event.published_at.desc(),Event.id.asc())).label('rank')).join(Event,Event.id==model.event_id).where(direct).subquery()
        pairs=list(session.execute(select(ranked.c.scope_id,ranked.c.event_id).where(ranked.c.rank<=3).order_by(ranked.c.scope_id,ranked.c.rank)))
        ids={eid for _,eid in pairs};events={e.id:e for e in session.scalars(select(Event).where(Event.id.in_(ids)))}
        payloads={e['id']:e for e in event_payloads(session,list(events.values()))}
        samples[group]=defaultdict(list)
        for sid,eid in pairs:samples[group][sid].append(payloads[eid])
    companies={}
    for group,items in groups.items():
        for item in items:companies[group,item.id]=roles[item.id] if group=='segment' else set(item.data.get('beneficiaries',[]))
    scope_rows=[select(literal(group).label('kind'),literal(sid).label('scope_id'),literal(ticker).label('ticker')) for (group,sid),tickers in companies.items() for ticker in tickers]
    mentions={};routines={}
    if scope_rows:
        scope=union_all(*scope_rows).cte('company_scopes')
        each=(func.json_array_elements_text(Event.mentioned).table_valued('value') if session.bind.dialect.name=='postgresql' else func.json_each(Event.mentioned).table_valued('value')).alias('mentioned_company')
        mq=select(scope.c.kind,scope.c.scope_id,func.count(func.distinct(Event.id))).select_from(Event).join(each,true()).join(scope,scope.c.ticker==each.c.value).where(recent).group_by(scope.c.kind,scope.c.scope_id)
        mentions={(g,sid):count for g,sid,count in session.execute(mq)}
        rq=select(scope.c.kind,scope.c.scope_id,func.count(func.distinct(Event.id))).select_from(Event).join(scope,scope.c.ticker==Event.ticker).where(Event.routine.is_(True),func.coalesce(Event.published_at,Event.reported_at,Event.activity_at)>=cutoff90).group_by(scope.c.kind,scope.c.scope_id)
        routines={(g,sid):count for g,sid,count in session.execute(rq)}
    from .technical_documents import summary_map
    documents=summary_map(session)
    from .indicator_api import indicator_context
    indicator_state=indicator_context(session,[t.id for t in groups['theme']],sources)
    rows=[]
    for group,items in groups.items():
        for item in items:
            if group=='theme' and not item.active:continue
            scope='segments' if group=='segment' else 'themes'
            configured=[s for s in sources if item.id in s.data.get(scope,[]) and s.data.get('adapter') not in ('manual','technical-documents')]
            direct30,direct,background,unknown=stats[group].get(item.id,(0,0,0,0))
            mention_count=mentions.get((group,item.id),0);routine_count=routines.get((group,item.id),0)
            sample=samples[group][item.id]
            successes=[s for s in configured if s.last_success and s.status in ('success','partial')]
            source_payload=[dict(columns(s),registry_reachability=s.data.get('reachability'),registry_checked=s.data.get('checked')) for s in configured]
            newest=max((s.last_success for s in configured if s.last_success),default=None)
            gaps=[]
            if not item.prose: gaps.append('尚無研究散文')
            if not configured: gaps.append('尚無自動來源設定')
            if not successes: gaps.append('本輪來源尚未成功')
            pending=sum(s.status=='configuration_required' for s in configured)
            failed=sum(s.status=='failed' for s in configured)
            if pending: gaps.append(f'{pending} 個來源待設定')
            if failed: gaps.append(f'{failed} 個來源取得失敗')
            if not direct30: gaps.append('近 30 日尚無可確認發布日的直接事件')
            if not direct: gaps.append('近 90 日尚無可確認發布日的直接事件')
            indicator_data=None
            if group=='theme':
                from .indicator_api import indicators_payload
                indicator_data=indicators_payload(session,item,reference=reference.date(),context=indicator_state,history=False)
            rows.append({'id':item.id,'kind':group,'name':item.name if group=='segment' else item.data['name_zh'],
                'layer':item.layer if group=='segment' else None,'research_available':bool(item.prose),
                'checked':item.checked if group=='theme' else None,'sources':source_payload,
                'configured_sources':len(configured),'successful_sources':len(successes),'last_updated':newest,
                'assessment_available':bool(item.data.get('assessment')) if group=='theme' else None,
                'assessment_checked':(item.data.get('assessment') or {}).get('reviewed') if group=='theme' else None,
                'indicator_count':len(indicator_data['indicators']) if indicator_data else None,
                'available_indicator_count':sum(i['latest'] is not None for i in indicator_data['indicators']) if indicator_data else None,
                'indicator_gaps':(indicator_data['gaps']+[f'{i["name"]} ({i["kind"]})：{g}' for i in indicator_data['indicators'] for g in i['gaps']]) if indicator_data else [],
                'direct_30d':direct30,'direct_90d':direct,
                'background_90d':background,'unknown_date':unknown,'routine_90d':routine_count,
                'company_mentions_90d':mention_count,'samples':sample,'gaps':gaps,
                'technical_profile_available':bool(item.data.get('technical-profile')),'technical_reviewed':(item.data.get('technical-profile') or {}).get('reviewed'),'technical_gaps':(item.data.get('technical-profile') or {}).get('evidence-gaps',[]),'technical_documents':[d for d in documents if item.id in d[scope]]})
    return {'as_of':reference,'window_start':cutoff90,'rules_version':rules()['version'],'rows':rows,
        'counting':'直接事件僅計發布日可確認、非預告、非例行的內容分類；背景統計、公司提及、未知日期與 inference 分開。來源設定範圍不代表有事件。'}

def coverage_markdown(data):
    text=['# 近 90 日資料覆蓋矩陣','',f'取得基準：{data["as_of"].isoformat()}；規則：{data["rules_version"]}', '', data['counting'], '',
        '| 種類 | 環節／題材 | 研究 | 來源設定／成功 | 直接 30／90 日 | 背景 90 日 | 未知發布日 | 缺口 |',
        '|---|---|---|---|---|---|---|---|']
    for r in data['rows']:
        text.append(f'| {r["kind"]} | {r["name"]} ({r["id"]}) | {"有" if r["research_available"] else "無"} | {r["configured_sources"]}／{r["successful_sources"]} | {r["direct_30d"]}／{r["direct_90d"]} | {r["background_90d"]} | {r["unknown_date"]} | {"；".join(r["gaps"]) or "—"} |')
    text+=['','## 題材判讀與指標覆蓋','','| 題材 | 判讀 | 原查核基準 | 指標設定／取得 | 指標缺口 |','|---|---|---|---|---|']
    for r in data['rows']:
        if r['kind']=='theme':
            text.append(f'| {r["name"]} ({r["id"]}) | {"可讀" if r["assessment_available"] else "尚未整理"} | {r["assessment_checked"] or "未提供"} | {r["indicator_count"]}／{r["available_indicator_count"]} | {"；".join(r["indicator_gaps"]) or "—"} |')
    text+=['','## 技術研究與文件核對','','技術文件與新聞／指標分開計數。文件性質、研究查核與 runtime 健康互不替代。','']
    for r in data['rows']:
        text.append(f"- {r['name']}：技術查核 {r['technical_reviewed'] or '未整理'}；"+'；'.join(r['technical_gaps']))
        for d in r['technical_documents']:text.append(f"  - {d['title']}；性質 {d['doc_kind']}；基準 {d['versions']}；待核對 {d['pending_count']}；文件 {d['id']}")
    text+=['','## 真實分類樣本','']
    for r in data['rows']:
        text.append(f'### {r["name"]} ({r["id"]})')
        for e in r['samples']:
            text.append(f'- [{e["title"]}]({e["url"]})；發布 {e["published_at"].isoformat()}；事件 {e["id"]}')
        if not r['samples']: text.append('- 尚無直接樣本，保留缺口。')
        for s in r['sources']:
            meta=s['data'].get('backfill_meta') or s['data'].get('fetch_meta',{})
            text.append(f'- 來源 {s["id"]}：{s["status"]}；歷史觀察 {meta.get("oldest_observed","未取得")}；{s["error"] or "；".join(meta.get("warnings",[])) or meta.get("limit", "尚未取得回補紀錄")}')
        text.append('')
    return '\n'.join(text)
