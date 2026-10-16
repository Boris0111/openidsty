"""Public content tokens; no personal state or operational timestamps."""
import hashlib,json
from sqlalchemy import select,func,or_,and_
from sqlalchemy.orm import load_only
from .models import Theme,Indicator,ThemeIndicator,ThemeAssessmentVersion,IndicatorObservation,Source,Event,EventTheme,now
from .assessments import source_evidence,TAIPEI
from .observations import latest_query
from .financial_indicators import runtime_source_id
from datetime import date,datetime,time,timedelta,timezone
from collections import defaultdict


def token(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,default=str,separators=(',',':')).encode()).hexdigest()


def updates_payload(session,ids):
    themes={t.id:t for t in session.scalars(select(Theme).where(Theme.id.in_(ids),Theme.active.is_(True)))}
    latest=select(ThemeAssessmentVersion.theme_id,func.max(ThemeAssessmentVersion.version_number).label('number')).where(ThemeAssessmentVersion.theme_id.in_(ids)).group_by(ThemeAssessmentVersion.theme_id).subquery()
    versions={v.theme_id:v for v in session.scalars(select(ThemeAssessmentVersion).join(latest,and_(latest.c.theme_id==ThemeAssessmentVersion.theme_id,latest.c.number==ThemeAssessmentVersion.version_number)).options(load_only(ThemeAssessmentVersion.id,ThemeAssessmentVersion.theme_id,ThemeAssessmentVersion.version_number)))}
    definitions=defaultdict(list)
    for tid,i in session.execute(select(ThemeIndicator.theme_id,Indicator).join(Indicator).where(ThemeIndicator.theme_id.in_(ids)).order_by(Indicator.id)):definitions[tid].append(i)
    iids={i.id for values in definitions.values() for i in values};observations=defaultdict(list)
    fields=('id','indicator_id','identity','revision','content_hash','valid','original_period','period_end')
    for row in session.scalars(latest_query(iids).options(load_only(*(getattr(IndicatorObservation,f) for f in fields)))):observations[row.indicator_id].append(row)
    from . import assessments
    reference=assessments.now();conditions=[]
    for tid,t in themes.items():
        baseline=(t.data.get('assessment') or {}).get('reviewed') or t.checked
        after=Event.published_at>=datetime.combine(date.fromisoformat(baseline)+timedelta(days=1),time.min,TAIPEI).astimezone(timezone.utc) if baseline else False
        conditions.append(and_(EventTheme.theme_id==tid,or_(Event.published_at.is_(None),and_(after,Event.published_at<=reference))))
    events=defaultdict(list)
    eq=select(EventTheme.theme_id,Event.id,Event.identity,Event.title,Event.body,Event.published_at,Event.published_precision,Event.lifecycle).join(Event,Event.id==EventTheme.event_id).where(EventTheme.relevance=='direct',Event.routine.is_(False),Event.lifecycle=='published',or_(*conditions) if conditions else False)
    for row in session.execute(eq):events[row[0]].append(row)
    sources={s.id:s for s in session.scalars(select(Source))};items=[]
    for tid in ids:
        theme=themes.get(tid)
        if not theme:
            items.append({'theme_id':tid,'available':False,'reason':'題材已不存在或不在目前研究範圍'});continue
        version=versions.get(tid);rows=[];summary=[];available=0
        _,warnings=source_evidence(session,theme.data.get('assessment'))
        for i in definitions[tid]:
            values=observations[i.id]
            rows.extend((i.id,r.identity,r.revision,r.content_hash,r.valid) for r in values)
            current=next((r for r in values[:12] if r.valid),None);available+=int(current is not None)
            summary.append({'id':i.id,'name':i.name,'kind':i.kind,'period':current.original_period if current else None,'revision':current.revision if current else None})
            sid=i.data['source_id'] if i.kind=='direct' else runtime_source_id(i.data);source=sources.get(sid)
            if source and source.error and source.status in ('failed','partial','configuration_required'):warnings.append({'source_id':sid,'kind':source.status,'message':source.error})
        content=[(identity or str(eid),title,body,published.isoformat() if published else None,precision,lifecycle) for _,eid,identity,title,body,published,precision,lifecycle in events[tid]]
        known=sum(e.published_at is not None for e in events[tid]);unknown=len(events[tid])-known
        items.append({'theme_id':tid,'available':True,'name':theme.data['name_zh'],'current_version_id':version.id if version else None,'version_number':version.version_number if version else None,'reviewed':theme.checked,'assessment_summary':(theme.data.get('assessment') or {}).get('summary'),'indicator_token':token(sorted(rows)),'candidate_token':token(sorted(content,key=lambda r:r[0])),'candidate_count':known,'unknown_date_count':unknown,'indicator_count':len(summary),'available_indicator_count':available,'indicator_summary':summary,'source_warnings':warnings,'pending_summary':f'{known} 則待纳入判讀；{unknown} 則新收錄資訊發布日待確認（不代表新發生）'})
    return {'items':items}
