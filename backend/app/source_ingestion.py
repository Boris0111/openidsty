"""One response feeds canonical finance and compatible legacy projections."""
import hashlib,json,re
from collections import defaultdict
from datetime import date,datetime,timezone
from sqlalchemy import text,select
from .models import Company,Event,Source,EventSegment,EventTheme
from .ingest import ingest_one
from .connectors import fetch_source,parse_tw,parse_sec_facts
from .financial_tw import parse_taiwan,TwIssuer,persist_taiwan,capabilities as tw_capabilities
from .financial_sec import parse_companyfacts,SecIssuer,persist_sec,capabilities as sec_capabilities
from .payloads import raw_payload


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
    canonical={};started=datetime.now(timezone.utc);capabilities=None
    def fetcher(d,client,tracked):
        nonlocal canonical,capabilities
        if d['adapter']=='tw' and d.get('kind') in ('revenue','financials','balance'):
            issuers={};codes=defaultdict(set)
            profiles={row.entity_id:row.data.get('financial-reporting',{}) for row in session.execute(text('''SELECT s.entity_id,s.data
                FROM research.entity_snapshots s WHERE s.release_id=:release AND s.kind='company' '''),{'release':release})}
            for ticker,identifier in mapping.items():
                if re.fullmatch(r'\d{4}\.TW(?:O)?',ticker):codes[ticker.split('.')[0]].add(identifier)
            for code,ids in codes.items():
                if len(ids)==1:
                    identifier=next(iter(ids));profile=profiles.get(identifier,{})
                    calendar=tuple(map(int,profile['fiscal-year-end'].split('-'))) if profile.get('fiscal-year-end') and profile.get('confidence')=='well-supported' else None
                    issuers[code]=TwIssuer(identifier,calendar,calendar_valid_from=date.fromisoformat(profile['calendar-valid-from']) if calendar else None,
                        calendar_valid_to=date.fromisoformat(profile['calendar-valid-to']) if profile.get('calendar-valid-to') else None)
            def parse(response):return parse_taiwan(response.content,d['id'],d['kind'],str(response.url),issuers)
            response=client.get(d['url'])
            try:parsed=parse(response)
            except ValueError:
                if not d.get('fallback'):raise
                response=client.get(d['fallback']);parsed=parse(response)
            result=persist_taiwan(session.connection(),parsed)
            canonical={key:value for key,value in result.items() if key!='items'}
            canonical.update(records=len(parsed.records),unresolved=raw_payload(parsed.unresolved[:1000]),
                unresolved_truncated=len(parsed.unresolved)>1000,payload_sha256=hashlib.sha256(response.content).hexdigest())
            capabilities=tw_capabilities(d['kind'])
            # Quarterly calendars are not guessed to keep a legacy projection full.
            if d['kind']=='balance':return [],[]
            usable={row.value.context.company_id for row in parsed.records}
            if not usable:return [],[]
            try:return parse_tw(response.text,d['kind'],str(response.url),{code:ticker for code,ticker in tracked.items() if code in issuers and issuers[code].company_id in usable})
            except ValueError:
                canonical['legacy_projection_gap']='舊版欄位無法表示此期間格式；已保存 canonical 值，舊值保留。'
                return [],[]
        if d['adapter']=='sec-facts':
            identifier=mapping.get(d.get('ticker'))
            if not identifier:raise ValueError('官方 CIK 無法對應目前已發布的公司。')
            cik=session.execute(text('''SELECT i.value FROM research.source_identifiers i
                WHERE i.release_id=:release AND i.company_id=:company AND i.provider='sec-cik' '''),{'release':release,'company':identifier}).scalar_one_or_none()
            if not cik:raise ValueError('公司未設定已核對 CIK。')
            response=client.get(d['url'],sec=True)
            parsed=parse_companyfacts(response.content,SecIssuer(identifier,cik));result=persist_sec(session.connection(),parsed)
            canonical={key:value for key,value in result.items() if key!='items'}
            canonical.update(records=len(parsed.records),unresolved=raw_payload(parsed.unresolved[:1000]),
                unresolved_truncated=len(parsed.unresolved)>1000,payload_sha256=hashlib.sha256(response.content).hexdigest())
            capabilities=sec_capabilities()
            return parse_sec_facts(response.json(),d['ticker'],d['url'])
        return fetch_source(d,client,tracked)
    if definition['adapter']=='technical-documents':
        from .technical_monitor import ingest_documents
        result=ingest_documents(session,definition,client=http,force=True) # Outer durable queue already checks due time.
    elif definition['adapter'] in ('aaon-metrics','tsmc-metrics'):
        from .metric_ingest import ingest_metric_source
        result=ingest_metric_source(session,definition,http)
    else:result=ingest_one(session,definition,http,companies,fetcher)
    if result['status'] in ('success','partial'):
        result.update(link_events(session,definition,started,mapping,release));result['mapping_release_id']=str(release)
        if canonical:
            result['financial']=canonical;result['capabilities']=capabilities
            result['new_count']+=canonical['new_revisions']
            if canonical['needs_review'] or not canonical['records']:
                result['status']='partial';result['error']='官方內容已取得，部分日期／範圍或欄位仍需核對。'
            from .financial_indicators import project_financials
            result['indicator_changes']=project_financials(session)
        session.commit()
    return result
