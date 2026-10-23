"""One source run feeds events, research links and theme proxy revenue."""
import re
from collections import defaultdict
from datetime import datetime,timezone
from sqlalchemy import text,select
from .models import Company,Event,Source,EventSegment,EventTheme
from .ingest import ingest_one
from .connectors import fetch_source


def company_mappings(session,release):
    rows=session.execute(text('''SELECT m.legacy_key,m.entity_id FROM research.legacy_mappings m
        WHERE m.release_id=:release AND m.kind='company' '''),{'release':release}).all()
    grouped=defaultdict(set)
    for key,identifier in rows:grouped[key].add(identifier)
    return {key:next(iter(ids)) for key,ids in grouped.items() if len(ids)==1}


def nature(definition,event):
    if definition.get('source_nature') in ('official','report','rumor'):return definition['source_nature']
    if definition.get('type') in ('filings','earnings_call','official_stats','technical-documents'):return 'official'
    if re.search(r'傳聞|傳出|據悉|消息人士|知情人士|rumou?r|reportedly|anonymous',event.title+' '+event.body,re.I):return 'rumor'
    return 'report'


def link_events(session,definition,started,mapping,release,events=None):
    available=set(session.execute(text('SELECT entity_id FROM research.entity_snapshots WHERE release_id=:release'),{'release':release}).scalars())
    if events is None:events=session.scalars(select(Event).where(Event.source_id==definition['id'],Event.fetched_at>=started).order_by(Event.id).limit(2001)).all()
    for event in events[:2000]:
        links=set();kind=nature(definition,event)
        if mapping.get(event.ticker):links.add((mapping[event.ticker],'direct'))
        for ticker in event.mentioned or []:
            if mapping.get(ticker) and ticker!=event.ticker:links.add((mapping[ticker],'mention'))
        for model,prefix,key in ((EventSegment,'segment-','segment_id'),(EventTheme,'theme-','theme_id')):
            for association in session.scalars(select(model).where(model.event_id==event.id)):
                identifier=prefix+getattr(association,key)
                if identifier in available:links.add((identifier,association.relevance))
        session.execute(text('DELETE FROM research.event_entity_links WHERE event_id=:id'),{'id':event.id})
        for identifier,relevance in links:
            if identifier not in available:continue
            session.execute(text('''INSERT INTO research.event_entity_links(event_id,entity_id,relevance,source_nature)
                VALUES(:event,:entity,:relevance,:nature)'''),{'event':event.id,'entity':identifier,'relevance':relevance,'nature':kind})
    return {'events_classified':min(len(events),2000),'truncated':len(events)>2000}


def ingest_definition(session,definition,http):
    release=session.execute(text('SELECT release_id FROM research.release_head')).scalar_one_or_none()
    companies=list(session.scalars(select(Company)));mapping=company_mappings(session,release)
    if not mapping:raise ValueError('尚未建立已發布公司的識別映射。')
    started=datetime.now(timezone.utc)
    # Monthly and SEC revenue only feed theme proxy indicators through the legacy financials table.
    revenue_source=definition['adapter']=='sec-facts' or (definition['adapter']=='tw' and definition.get('kind')=='revenue')
    if definition['adapter']=='technical-documents':
        from .technical_monitor import ingest_documents
        result=ingest_documents(session,definition,client=http,force=True) # Outer durable queue already checks due time.
    elif definition['adapter'] in ('aaon-metrics','tsmc-metrics'):
        from .metric_ingest import ingest_metric_source
        result=ingest_metric_source(session,definition,http)
    else:result=ingest_one(session,definition,http,companies,fetch_source)
    if result['status'] in ('success','partial'):
        result.update(link_events(session,definition,started,mapping,release));result['mapping_release_id']=str(release)
        if revenue_source:
            from .financial_indicators import project_financials
            result['indicator_changes']=project_financials(session)
        session.commit()
    return result
