"""Published-entity events, with rumor observations in a separate reader contract."""
import base64,json,uuid
from datetime import date,datetime,timezone
from typing import Literal
from fastapi import APIRouter,Depends,Query
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release,entity,envelope
from .research_compile import digest
from .research_financials import as_of

router=APIRouter(prefix='/api/v2',tags=['research-events'])
ORDER_DATE="COALESCE(e.published_at,e.reported_at,'0001-01-01 00:00:00+00'::timestamptz)"


def event_page(session,release,entity_id,source_id,source_nature,relevance,period_from,period_to,include_unknown,limit,cursor,rumors):
    if entity_id:entity(session,release,entity_id)
    if period_from and period_to and period_from>period_to:raise ResearchError(422,'invalid-period','期間起日不得晚於迄日。')
    if source_nature and ((rumors and source_nature!='rumor') or (not rumors and source_nature=='rumor')):
        raise ResearchError(422,'invalid-source-nature','傳聞請從觀察入口讀取；正式事件入口僅提供官方發布與報導。')
    filters={'entity_id':entity_id,'source_id':source_id,'source_nature':source_nature,'relevance':relevance,
        'period_from':period_from,'period_to':period_to,'include_unknown':include_unknown,'rumors':rumors}
    last_time,last_id=datetime.max.replace(tzinfo=timezone.utc),2147483647
    if cursor:
        try:
            value=json.loads(base64.urlsafe_b64decode(cursor+'='*(-len(cursor)%4)))
            if set(value)!={'release','filter','last'} or not isinstance(value['last'],list) or len(value['last'])!=2:raise ValueError()
            if value['release']!=str(release['release_id']) or value['filter']!=digest(filters):
                raise ResearchError(409,'cursor-conflict','事件篩選或研究版本已改變，請從第一頁讀取。')
            last_time=datetime.fromisoformat(value['last'][0]);last_id=value['last'][1]
            if last_time.tzinfo is None or type(last_id) is not int or not 1<=last_id<=2147483647:raise ValueError()
        except (ValueError,KeyError,TypeError,UnicodeError):raise ResearchError(422,'invalid-cursor','事件分頁格式不正確。') from None
    params={**filters,'release':release['release_id'],'last_time':last_time,'last_id':last_id,'limit':limit+1}
    rows=session.execute(text('''SELECT e.id,e.source_id,left(e.title,500) AS title,left(e.body,800) AS excerpt,
        e.url,e.kind,e.published_at,e.published_precision,e.reported_at,e.date_semantics,e.period,e.routine,
        COALESCE(rs.name,s.name) AS source_name,'''+ORDER_DATE+''' AS order_date
        FROM public.events e JOIN public.sources s ON s.id=e.source_id
        LEFT JOIN research.release_sources rs ON rs.release_id=:release AND rs.source_id=e.source_id
        WHERE e.lifecycle='published' AND (CAST(:source_id AS text) IS NULL OR e.source_id=:source_id)
        AND EXISTS(SELECT 1 FROM research.event_entity_links l JOIN research.entity_snapshots snap
            ON snap.release_id=:release AND snap.entity_id=l.entity_id WHERE l.event_id=e.id
            AND (CAST(:entity_id AS text) IS NULL OR l.entity_id=:entity_id)
            AND (CAST(:relevance AS text) IS NULL OR l.relevance=:relevance)
            AND (CAST(:source_nature AS text) IS NULL OR l.source_nature=:source_nature)
            AND CASE WHEN :rumors THEN l.source_nature='rumor' ELSE l.source_nature IN ('official','report') END)
        AND ((:include_unknown AND e.published_at IS NULL AND e.reported_at IS NULL) OR (
            COALESCE(e.published_at,e.reported_at) IS NOT NULL
            AND (CAST(:period_from AS date) IS NULL OR COALESCE(e.published_at,e.reported_at)>=CAST(:period_from AS date))
            AND (CAST(:period_to AS date) IS NULL OR COALESCE(e.published_at,e.reported_at)<CAST(:period_to AS date)+interval '1 day')))
        AND ('''+ORDER_DATE+''',e.id)<(CAST(:last_time AS timestamptz),:last_id)
        ORDER BY '''+ORDER_DATE+''' DESC,e.id DESC LIMIT :limit'''),params).mappings().all()
    visible=rows[:limit];ids=[row['id'] for row in visible]
    links=session.execute(text('''SELECT ranked.* FROM (SELECT l.event_id,l.entity_id,s.name,s.kind,l.relevance,l.source_nature,
        row_number() OVER(PARTITION BY l.event_id ORDER BY l.relevance,l.entity_id) AS n
        FROM research.event_entity_links l JOIN research.entity_snapshots s ON s.release_id=:release AND s.entity_id=l.entity_id
        WHERE l.event_id=ANY(CAST(:ids AS integer[]))) ranked WHERE n<=101'''),{'release':release['release_id'],'ids':ids}).mappings().all() if ids else []
    items=[]
    for row in visible:
        related=[part for part in links if part['event_id']==row['id']]
        items.append({**{key:value for key,value in row.items() if key!='order_date'},
            'source_nature':'rumor' if rumors else next((part['source_nature'] for part in related if part['source_nature']!='rumor'),source_nature),
            'date_unknown':row['published_at'] is None and row['reported_at'] is None,
            'entities':[{key:part[key] for key in ('entity_id','name','kind','relevance','source_nature')} for part in related[:100]],
            'entities_truncated':len(related)>100})
    more=len(rows)>limit
    next_cursor=base64.urlsafe_b64encode(json.dumps({'release':str(release['release_id']),'filter':digest(filters),
        'last':[visible[-1]['order_date'].isoformat(),visible[-1]['id']]}).encode()).decode().rstrip('=') if more else None
    return envelope(release,{'as_of':as_of(session),'items':items,'has_more':more,'next_cursor':next_cursor,
        'classification_limit':'事件與內容提及不是正式供應關係；傳聞需另經研究核對與發布。'})


@router.get('/events')
def events(release_id:uuid.UUID|None=None,entity_id:str|None=Query(None,max_length=200),
    source_id:str|None=Query(None,max_length=100),source_nature:Literal['official','report','rumor']|None=None,
    relevance:Literal['direct','background','mention']|None=None,period_from:date|None=None,period_to:date|None=None,
    include_unknown:bool=True,limit:int=Query(50,ge=1,le=100),cursor:str|None=Query(None,max_length=2048),session=Depends(get_research_session)):
    return event_page(session,require_release(session,release_id),entity_id,source_id,source_nature,relevance,
        period_from,period_to,include_unknown,limit,cursor,False)


@router.get('/observations')
def observations(release_id:uuid.UUID|None=None,entity_id:str|None=Query(None,max_length=200),
    source_id:str|None=Query(None,max_length=100),source_nature:Literal['official','report','rumor']|None=None,
    relevance:Literal['direct','background','mention']|None=None,period_from:date|None=None,period_to:date|None=None,
    include_unknown:bool=True,limit:int=Query(50,ge=1,le=100),cursor:str|None=Query(None,max_length=2048),session=Depends(get_research_session)):
    return event_page(session,require_release(session,release_id),entity_id,source_id,source_nature,relevance,
        period_from,period_to,include_unknown,limit,cursor,True)
