"""Read-only update summary for device-local favourites. Nothing about the reader is stored."""
import uuid
from typing import Literal
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release, as_of
from .research_compile import digest
from .research_financials import LATEST
from .theme_updates import indicator_tokens

router = APIRouter(prefix='/api/v2', tags=['research-updates'])
Kind = Literal['company', 'product', 'theme', 'research']
MAX_TARGETS = 100


class Seen(BaseModel):
    research: str | None = Field(None, max_length=128)
    values: str | None = Field(None, max_length=128)
    events: int | None = Field(None, ge=0, le=2147483647)


class Target(BaseModel):
    kind: Kind
    id: str = Field(min_length=3, max_length=200, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    seen: Seen | None = None


class Query(BaseModel):
    release_id: uuid.UUID | None = None
    items: list[Target] = Field(max_length=MAX_TARGETS)

    @field_validator('items')
    @classmethod
    def unique(cls, items):
        if len({(item.kind, item.id) for item in items}) != len(items):
            raise ValueError('duplicate targets')
        return items


RESEARCH_SQL = '''SELECT s.entity_id,s.kind,s.name,s.semantic_hash,
  (SELECT md5(COALESCE(string_agg(r.relation_id||'|'||md5(row(r.kind,r.source_id,r.target_id,r.direction,r.mechanism,
      r.conditions,r.confidence,r.reviewed,r.product_id,r.application_id,r.data)::text),',' ORDER BY r.relation_id),''))
   FROM research.relations r WHERE r.release_id=s.release_id AND (r.source_id=s.entity_id OR r.target_id=s.entity_id)) AS relations,
  (SELECT md5(COALESCE(string_agg(o.offering_id||'|'||md5(row(o.company_id,o.product_id,o.role_id,o.conditions)::text),',' ORDER BY o.offering_id),''))
   FROM research.company_offerings o WHERE o.release_id=s.release_id AND s.entity_id IN (o.company_id,o.product_id,o.role_id)) AS offerings
FROM research.entity_snapshots s WHERE s.release_id=:release AND s.entity_id=ANY(CAST(:ids AS text[]))'''

# The effective value of each series; a re-filed identical value adds no revision, so no new token.
VALUES_SQL = '''SELECT g.company_id,md5(COALESCE(string_agg(g.group_id||':'||o.observation_id::text,',' ORDER BY g.group_id),'')) AS token
FROM research.financial_groups g ''' + LATEST + ''' WHERE g.company_id=ANY(CAST(:ids AS text[])) GROUP BY g.company_id'''

# Event ids only grow when a new event is recorded; retries deduplicate into the same row.
EVENTS_SQL = '''SELECT w.entity_id,max(e.id) AS marker,
  count(DISTINCT e.id) FILTER (WHERE e.id>COALESCE(w.seen,2147483647) AND COALESCE(e.published_at,e.reported_at) IS NOT NULL) AS new_dated,
  count(DISTINCT e.id) FILTER (WHERE e.id>COALESCE(w.seen,2147483647) AND COALESCE(e.published_at,e.reported_at) IS NULL) AS new_undated
FROM (SELECT unnest(CAST(:ids AS text[])) AS entity_id,unnest(CAST(:seen AS integer[])) AS seen) w
JOIN research.event_entity_links l ON l.entity_id=w.entity_id AND l.source_nature IN ('official','report')
JOIN public.events e ON e.id=l.event_id AND e.lifecycle='published'
GROUP BY w.entity_id,w.seen'''


def compared(current, seen):
    return None if seen is None else current != seen


@router.post('/updates/query')
def updates(query: Query, session=Depends(get_research_session)):
    release = require_release(session, query.release_id)
    ids = [item.id for item in query.items]
    research = {row['entity_id']: row for row in session.execute(text(RESEARCH_SQL),
                {'release': release['release_id'], 'ids': ids}).mappings()} if ids else {}
    found = [item for item in query.items if item.id in research and research[item.id]['kind'] == item.kind]
    companies = [item.id for item in found if item.kind == 'company']
    values = {row['company_id']: row['token'] for row in session.execute(text(VALUES_SQL), {'ids': companies}).mappings()} if companies else {}
    themes = {item.id: item.id.removeprefix('theme-') for item in found if item.kind == 'theme'}
    indicators = indicator_tokens(session, list(themes.values())) if themes else {}
    events = {row['entity_id']: row for row in session.execute(text(EVENTS_SQL), {'ids': [item.id for item in found],
              'seen': [item.seen.events if item.seen else None for item in found]}).mappings()} if found else {}
    items = []
    for item in query.items:
        seen = item.seen or Seen()
        row = research.get(item.id)
        if not row or row['kind'] != item.kind:
            items.append({'kind': item.kind, 'id': item.id, 'available': False,
                          'reason': '這份研究不在目前已發布版本中，可能已改名、合併或封存。'})
            continue
        research_token = digest([row['semantic_hash'], row['relations'], row['offerings']])
        if item.kind == 'company':
            values_token = values.get(item.id) or digest([])
        elif item.kind == 'theme':
            values_token = indicators.get(themes[item.id])
        else:
            values_token = None  # Products and research pages carry no observed values.
        event = events.get(item.id) or {'marker': 0, 'new_dated': 0, 'new_undated': 0}
        pending_events = seen.events is None
        items.append({'kind': item.kind, 'id': item.id, 'available': True, 'name': row['name'],
            'research': {'token': research_token, 'changed': compared(research_token, seen.research)},
            'values': {'applicable': values_token is not None, 'token': values_token,
                       'changed': compared(values_token, seen.values) if values_token is not None else False},
            'events': {'marker': event['marker'], 'changed': None if pending_events else event['new_dated'] + event['new_undated'] > 0,
                       'new_dated': 0 if pending_events else event['new_dated'],
                       'new_undated': 0 if pending_events else event['new_undated']}})
    data = {'as_of': as_of(session), 'release_id': str(release['release_id']), 'items': items,
            'note': '更新只依各收藏物件自己的研究、有效數值與事件判定；收藏不含研究全文。'}
    return JSONResponse(jsonable_encoder({'release_id': str(release['release_id']), 'schema_version': release['schema_version'], 'data': data}),
                        headers={'Cache-Control': 'no-store'})
