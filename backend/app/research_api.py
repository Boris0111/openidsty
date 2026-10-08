"""Shared read-only queries, classification payloads and auditable coverage."""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, or_, func
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
    segments=defaultdict(list); themes=defaultdict(list)
    for model,field,target in [(EventSegment,'segment_id',segments),(EventTheme,'theme_id',themes)]:
        for link in session.scalars(select(model).where(model.event_id.in_(ids))):
            target[link.event_id].append({'id':getattr(link,field),'relevance':link.relevance,'evidence':link.evidence})
    return [dict(columns(e,() if raw else ('raw',)),segments=segments[e.id],themes=themes[e.id]) for e in events]

def theme_payload(theme):
    return dict(theme.data,prose=theme.prose,checked=theme.checked)

def coverage(session, reference=None):
    reference=reference or datetime.now(timezone.utc)
    if reference.tzinfo is None: reference=reference.replace(tzinfo=timezone.utc)
    cutoff90=reference-timedelta(days=90); cutoff30=reference-timedelta(days=30)
    events={e.id:e for e in session.scalars(select(Event))}
    sources=list(session.scalars(select(Source).order_by(Source.id)))
    roles=defaultdict(set)
    for role in session.scalars(select(Role)): roles[role.segment_id].add(role.ticker)
    links={'segment':defaultdict(list),'theme':defaultdict(list)}
    for model,field,group in [(EventSegment,'segment_id','segment'),(EventTheme,'theme_id','theme')]:
        for link in session.scalars(select(model)): links[group][getattr(link,field)].append(link)
    rows=[]
    for group, model in [('segment',Segment),('theme',Theme)]:
        for item in session.scalars(select(model).order_by(model.id)):
            scope='segments' if group=='segment' else 'themes'
            configured=[s for s in sources if item.id in s.data.get(scope,[]) and s.data.get('adapter')!='manual']
            related=links[group][item.id]
            def utc(dt): return dt.replace(tzinfo=dt.tzinfo or timezone.utc) if dt else None
            def recent(e, cutoff): return e.lifecycle=='published' and e.published_at and cutoff<=utc(e.published_at)<=reference
            direct=[events[l.event_id] for l in related if l.relevance=='direct' and not events[l.event_id].routine and recent(events[l.event_id],cutoff90)]
            background=[events[l.event_id] for l in related if l.relevance=='background' and recent(events[l.event_id],cutoff90)]
            unknown=[events[l.event_id] for l in related if events[l.event_id].published_at is None]
            companies=roles[item.id] if group=='segment' else set(item.data.get('beneficiaries',[]))
            mention_count=sum(bool(companies.intersection(e.mentioned)) and bool(recent(e,cutoff90)) for e in events.values())
            routines=sum(e.routine and e.ticker in companies and (utc(e.published_at or e.reported_at or e.activity_at) or reference-timedelta(days=1000))>=cutoff90 for e in events.values())
            sample=sorted(direct,key=lambda e:utc(e.published_at),reverse=True)[:3]
            successes=[s for s in configured if s.last_success and s.status in ('success','partial')]
            source_payload=[dict(columns(s),registry_reachability=s.data.get('reachability'),registry_checked=s.data.get('checked')) for s in configured]
            newest=max((s.last_success for s in configured if s.last_success),default=None)
            gaps=[]
            if not item.prose: gaps.append('尚無研究散文')
            if not configured: gaps.append('尚無自動來源設定')
            if not successes: gaps.append('本輪來源尚未成功')
            if not direct: gaps.append('近 90 日尚無可確認發布日的直接事件')
            rows.append({'id':item.id,'kind':group,'name':item.name if group=='segment' else item.data['name_zh'],
                'layer':item.layer if group=='segment' else None,'research_available':bool(item.prose),
                'checked':item.checked if group=='theme' else None,'sources':source_payload,
                'configured_sources':len(configured),'successful_sources':len(successes),'last_updated':newest,
                'direct_30d':sum(bool(recent(e,cutoff30)) for e in direct),'direct_90d':len(direct),
                'background_90d':len(background),'unknown_date':len(unknown),'routine_90d':routines,
                'company_mentions_90d':mention_count,'samples':event_payloads(session,sample),'gaps':gaps})
    return {'as_of':reference,'window_start':cutoff90,'rules_version':rules()['version'],'rows':rows,
        'counting':'直接事件僅計發布日可確認、非預告、非例行的內容分類；背景統計、公司提及、未知日期與 inference 分開。來源設定範圍不代表有事件。'}

def coverage_markdown(data):
    text=['# 近 90 日資料覆蓋矩陣','',f'取得基準：{data["as_of"].isoformat()}；規則：{data["rules_version"]}', '', data['counting'], '',
        '| 種類 | 環節／題材 | 研究 | 來源設定／成功 | 直接 30／90 日 | 背景 90 日 | 未知發布日 | 缺口 |',
        '|---|---|---|---|---|---|---|---|']
    for r in data['rows']:
        text.append(f'| {r["kind"]} | {r["name"]} ({r["id"]}) | {"有" if r["research_available"] else "無"} | {r["configured_sources"]}／{r["successful_sources"]} | {r["direct_30d"]}／{r["direct_90d"]} | {r["background_90d"]} | {r["unknown_date"]} | {"；".join(r["gaps"]) or "—"} |')
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
