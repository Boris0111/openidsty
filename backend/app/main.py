from fastapi import FastAPI, Depends, HTTPException, Query, Response
from sqlalchemy import select, or_, text
from sqlalchemy.orm import Session as DbSession
from datetime import date, datetime, time, timedelta, timezone
from .db import get_session
from .models import Company, Segment, Theme, Role, Event, Financial, Source, IngestionRun, EventSegment
from .research_api import event_query, event_payloads, event_order, theme_payload, coverage, coverage_markdown
from .graph import LAYERS, industry_graph, company_graph, impact_paths,segment_relations

app = FastAPI(title='IndustryFlow 產業情報', version='0.1.0', docs_url='/api/docs', openapi_url='/api/openapi.json', redoc_url=None)
from .research_v2 import router as research_router
from .research_graph_v2 import router as research_graph_router
from .research_search import router as research_search_router
from .research_assets import router as research_assets_router
from .research_http import install as install_research_http
from .research_auth import router as research_auth_router
from .research_drafts import router as research_drafts_router
from .research_publication import router as research_publication_router
from .financial_imports import router as financial_imports_router
from .source_updates import router as source_updates_router
app.include_router(source_updates_router)
app.include_router(financial_imports_router)
app.include_router(research_publication_router)
app.include_router(research_drafts_router)
app.include_router(research_auth_router)
app.include_router(research_graph_router)
app.include_router(research_search_router)
app.include_router(research_assets_router)
app.include_router(research_router)
install_research_http(app)

def columns(row, exclude=()):
    return {c.name:getattr(row,c.name) for c in row.__table__.columns if c.name not in exclude}

def require(session, model, key):
    row = session.get(model, key)
    if row is None or (model is Theme and not row.active):
        raise HTTPException(404, '找不到這筆資料')
    return row

def company_detail(session, ticker):
    company = require(session, Company, ticker)
    roles = [{'segment':r.segment_id, 'segment_name':s.name, 'layer':s.layer, 'role':r.role} for r,s in session.execute(select(Role,Segment).join(Segment,Role.segment_id==Segment.id).where(Role.ticker==ticker))]
    financials = list(session.scalars(select(Financial).where(Financial.ticker==ticker).order_by(Financial.period_end.desc(),Financial.published_at.desc()).limit(24)))
    events = list(session.scalars(event_query(ticker=ticker,include_routine=True).limit(20)))
    # Mention-only events are a distinct collection; issuer always remains the primary company.
    mentioned = [e for e in session.scalars(select(Event).order_by(*event_order())) if ticker in e.mentioned][:20]
    return dict(columns(company, ('cik',)), roles=roles, financials=[columns(f,('raw',)) for f in financials], events=event_payloads(session,events), mentioned_events=event_payloads(session,mentioned))

@app.middleware('http')
async def cache_headers(request, call_next):
    response = await call_next(request)
    if request.method=='GET' and 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if response.headers.get('Content-Type') == 'application/json':
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.get('/api/health')
def health(session:DbSession=Depends(get_session)):
    session.execute(text('SELECT 1'))
    return {'status':'ok','map_ready':session.scalar(select(Segment.id).limit(1)) is not None}

@app.get('/api/industries')
def industries(session:DbSession=Depends(get_session)):
    return [{'id':key,'name':name,'segment_count':len(list(session.scalars(select(Segment.id).where(Segment.layer==key))))} for key,name in LAYERS.items()]

@app.get('/api/industries/{layer}/graph')
def industry(layer:str, session:DbSession=Depends(get_session)):
    if layer not in LAYERS:
        raise HTTPException(404, '找不到產業')
    return industry_graph(session,layer)

@app.get('/api/segments')
def segment_list(industry:str|None=None,session:DbSession=Depends(get_session)):
    if industry and industry not in LAYERS: raise HTTPException(422,'產業不存在')
    query=select(Segment).order_by(Segment.layer,Segment.position)
    if industry: query=query.where(Segment.layer==industry)
    return [{'id':s.id,'name':s.name,'layer':s.layer} for s in session.scalars(query)]

@app.get('/api/segments/{sid}')
def segment(sid:str, session:DbSession=Depends(get_session)):
    s = require(session,Segment,sid)
    keys=s.data['upstream']+s.data['downstream']
    neighbors={n.id:n for n in session.scalars(select(Segment).where(Segment.id.in_(keys)))} if keys else {}
    if any(key not in neighbors for key in keys):raise HTTPException(404,'找不到這筆資料')
    linked={t.id:t for t in session.scalars(select(Theme).where(Theme.id.in_(s.data['themes']),Theme.active.is_(True)))} if s.data['themes'] else {}
    return dict(s.data, prose=s.prose, themes_detail=[theme_payload(linked[key]) for key in s.data['themes'] if key in linked],
        relations=segment_relations(s,neighbors),
        neighbors=[{'id':n,'name':neighbors[n].name,'layer':neighbors[n].layer} for n in dict.fromkeys(keys)],
        events=event_payloads(session,list(session.scalars(event_query(segment=sid).limit(8)))))

@app.get('/api/themes')
def themes(session:DbSession=Depends(get_session)):
    return [theme_payload(t) for t in session.scalars(select(Theme).where(Theme.active.is_(True)).order_by(Theme.id))]

@app.get('/api/themes/{tid}')
def theme(tid:str,session:DbSession=Depends(get_session)):
    t=require(session,Theme,tid)
    segments={s.id:{'id':s.id,'name':s.name,'layer':s.layer} for s in session.execute(select(Segment.id,Segment.name,Segment.layer).where(Segment.id.in_(t.data['segments'])))}
    if any(key not in segments for key in t.data['segments']):raise HTTPException(404,'找不到這筆資料')
    return dict(theme_payload(t),segments_detail=[segments[key] for key in t.data['segments']],
        events=event_payloads(session,list(session.scalars(event_query(theme=tid).limit(20)))))

@app.get('/api/themes/{tid}/assessment')
def theme_assessment(tid:str,session:DbSession=Depends(get_session)):
    from .assessments import assessment_payload
    return assessment_payload(session,require(session,Theme,tid))

@app.get('/api/themes/{tid}/indicators')
def theme_indicators(tid:str,limit:int=Query(12,ge=1,le=36),session:DbSession=Depends(get_session)):
    from .indicator_api import indicators_payload
    return indicators_payload(session,require(session,Theme,tid),limit)

@app.get('/api/themes/{tid}/assessment/versions')
def assessment_versions(tid:str,limit:int=Query(20,ge=1,le=100),offset:int=Query(0,ge=0),session:DbSession=Depends(get_session)):
    from .assessment_versions import latest_version,version_payload
    from .models import ThemeAssessmentVersion
    from sqlalchemy import func
    require(session,Theme,tid);current=latest_version(session,tid)
    query=select(ThemeAssessmentVersion).where(ThemeAssessmentVersion.theme_id==tid).order_by(ThemeAssessmentVersion.version_number.desc())
    rows=list(session.scalars(query.limit(limit).offset(offset)))
    return {'theme_id':tid,'current_version_id':current.id if current else None,'total':session.scalar(select(func.count()).select_from(ThemeAssessmentVersion).where(ThemeAssessmentVersion.theme_id==tid)),'versions':[version_payload(row) for row in rows]}

@app.get('/api/themes/{tid}/indicators/{iid}/revisions')
def indicator_revisions(tid:str,iid:str,limit:int=Query(20,ge=1,le=100),offset:int=Query(0,ge=0),session:DbSession=Depends(get_session)):
    from .models import IndicatorObservation,ThemeIndicator
    from .indicator_api import observation_payload
    from sqlalchemy import func
    require(session,Theme,tid)
    if session.get(ThemeIndicator,(tid,iid)) is None:raise HTTPException(404,'指標不屬於此題材')
    q=select(IndicatorObservation).where(IndicatorObservation.indicator_id==iid)
    total=session.scalar(select(func.count()).select_from(q.subquery()))
    rows=session.scalars(q.order_by(IndicatorObservation.period_end.desc(),IndicatorObservation.revision.desc(),IndicatorObservation.id.desc()).limit(limit).offset(offset))
    return {'total':total,'limit':limit,'offset':offset,'items':[observation_payload(row) for row in rows]}

def require_version(session,tid,version_id):
    from .models import ThemeAssessmentVersion
    row=require(session,ThemeAssessmentVersion,version_id)
    if row.theme_id!=tid:raise HTTPException(404,'版本不屬於此題材')
    return row

@app.get('/api/themes/{tid}/assessment/versions/{version_id}')
def assessment_version(tid:str,version_id:int,session:DbSession=Depends(get_session)):
    from .assessment_versions import version_payload
    require(session,Theme,tid)
    return version_payload(require_version(session,tid,version_id),True)

@app.get('/api/themes/{tid}/assessment/compare')
def assessment_compare(tid:str,from_version:int=Query(...,ge=1),to_version:int=Query(...,ge=1),session:DbSession=Depends(get_session)):
    from .assessment_versions import version_payload,diff_values
    require(session,Theme,tid)
    before=require_version(session,tid,from_version);after=require_version(session,tid,to_version)
    return {'from':version_payload(before,True),'to':version_payload(after,True),'changes':diff_values(before.payload,after.payload)}

@app.get('/api/search')
def search(q:str=Query('',max_length=100),session:DbSession=Depends(get_session)):
    needle=q.strip().casefold(); results=[]
    if not needle: return []
    for s in session.scalars(select(Segment).order_by(Segment.position)):
        if needle in s.name.casefold() or needle in s.id.casefold():
            results.append({'kind':'segment','id':s.id,'name':s.name,'url':f'/?layer={s.layer}&segment={s.id}'})
    for t in session.scalars(select(Theme).where(Theme.active.is_(True)).order_by(Theme.id)):
        if needle in t.id.casefold() or needle in t.data['name_zh'].casefold():
            results.append({'kind':'theme','id':t.id,'name':t.data['name_zh'],'url':f'/themes/{t.id}'})
    from urllib.parse import quote
    for c in session.scalars(select(Company).order_by(Company.ticker)):
        if any(needle in a.casefold() for a in c.aliases):
            results.append({'kind':'company','id':c.ticker,'name':c.name,'url':f'/companies/{quote(c.ticker,safe="")}'})
    return results[:30]

@app.get('/api/theme-updates')
def theme_updates(ids:str=Query('',max_length=2000),session:DbSession=Depends(get_session)):
    from .theme_updates import updates_payload
    selected=list(dict.fromkeys(t.strip() for t in ids.split(',') if t.strip()))
    if len(selected)>20:raise HTTPException(422,'最多查詢 20 個不同題材')
    return updates_payload(session,selected)

@app.get('/api/coverage')
def data_coverage(session:DbSession=Depends(get_session)):
    return coverage(session)

@app.get('/api/technical-documents')
def technical_documents(limit:int=Query(20,ge=1,le=50),offset:int=Query(0,ge=0),segment:str|None=None,theme:str|None=None,session:DbSession=Depends(get_session)):
    from .technical_documents import list_documents
    return list_documents(session,limit,offset,segment,theme)

@app.get('/api/technical-documents/{did}')
def technical_document(did:str,limit:int=Query(10,ge=1,le=50),offset:int=Query(0,ge=0),session:DbSession=Depends(get_session)):
    from .technical_documents import document_detail
    return document_detail(session,did,limit,offset)

@app.get('/api/coverage/report')
def coverage_report(session:DbSession=Depends(get_session)):
    return Response(coverage_markdown(coverage(session)),media_type='text/markdown; charset=utf-8',headers={'Content-Disposition':'attachment; filename="coverage-90d.md"'})

@app.get('/api/segments/{sid}/impact')
def segment_impact(sid:str, depth:int=Query(3, ge=1, le=5), session:DbSession=Depends(get_session)):
    require(session,Segment,sid)
    return {'seed':sid,'confidence':'inference','paths':impact_paths(session,[sid],depth)}

@app.get('/api/companies')
def companies(q:str=Query('',max_length=100), session:DbSession=Depends(get_session)):
    all_companies = list(session.scalars(select(Company).order_by(Company.ticker)))
    needle = q.casefold()
    return [columns(c,('cik',)) for c in all_companies if not q or any(needle in a.casefold() for a in c.aliases)]

@app.get('/api/compare')
def compare(tickers:str=Query(...,max_length=200), session:DbSession=Depends(get_session)):
    choices = list(dict.fromkeys(t.strip() for t in tickers.split(',') if t.strip()))
    if not 2 <= len(choices) <= 4:
        raise HTTPException(422, '請選擇 2–4 家不同公司')
    return {'companies':[company_detail(session,t) for t in choices]}

@app.get('/api/companies/{ticker}')
def company(ticker:str, session:DbSession=Depends(get_session)):
    return company_detail(session,ticker)

@app.get('/api/companies/{ticker}/graph')
def relations(ticker:str, include_candidates:bool=False, session:DbSession=Depends(get_session)):
    require(session,Company,ticker)
    return company_graph(session,ticker,include_candidates)

@app.get('/api/events')
def events(ticker:str|None=None, kind:str|None=None, industry:str|None=None,segment:str|None=None,theme:str|None=None,
           date_from:date|None=None,date_to:date|None=None,include_routine:bool=False,
           relevance:str=Query('direct',pattern='^(direct|background|all)$'),limit:int=Query(30,ge=1,le=100), offset:int=Query(0,ge=0,le=10000), session:DbSession=Depends(get_session)):
    if industry and industry not in LAYERS: raise HTTPException(422,'產業不存在')
    if date_from and date_to and date_from>date_to: raise HTTPException(422,'起日不得晚於迄日')
    tz=timezone(timedelta(hours=8))
    start=datetime.combine(date_from,time.min,tz) if date_from else None
    end=datetime.combine(date_to+timedelta(days=1),time.min,tz) if date_to else None
    query=event_query(ticker,kind,industry,segment,theme,start,end,include_routine,relevance)
    return event_payloads(session,list(session.scalars(query.offset(offset).limit(limit))))

@app.get('/api/events/{event_id}')
def event(event_id:int, session:DbSession=Depends(get_session)):
    e = require(session,Event,event_id)
    seeds = list(session.scalars(select(EventSegment.segment_id).where(EventSegment.event_id==e.id,EventSegment.relevance=='direct')))
    return dict(event_payloads(session,[e],raw=True)[0], source=columns(require(session,Source,e.source_id)), impact={'confidence':'inference','seeds':seeds,'paths':impact_paths(session,seeds)})

@app.get('/api/sources')
def sources(session:DbSession=Depends(get_session)):
    run = session.scalar(select(IngestionRun).order_by(IngestionRun.id.desc()).limit(1))
    return {'sources':[columns(s) for s in session.scalars(select(Source).order_by(Source.id))], 'last_run':columns(run) if run else None}
