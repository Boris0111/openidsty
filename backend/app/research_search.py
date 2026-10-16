"""Alias search preserves legal identities and English token boundaries."""
import base64
import json
import re
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from .research_compile import normalize, digest
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release, envelope, summary, cursor_value, COLLECTIONS

router = APIRouter(prefix='/api/v2', tags=['research-search'])


def search_query(q, release_id, limit=50, last_rank=-1, last_id='', kinds=None):
    normalized = normalize(q)
    if not normalized:
        raise ResearchError(422, 'invalid-search', '請輸入公司、產品、代號或術語。')
    chinese = bool(re.search(r'[\u3400-\u9fff]', normalized))
    escaped = normalized.replace('!', '!!').replace('%', '!%').replace('_', '!_')
    if chinese:
        predicate = "a.normalized LIKE :pattern ESCAPE '!'"
        pattern = escaped + '%' if len(normalized) <= 2 else '%' + escaped + '%'
        rank = 1 if len(normalized) <= 2 else 2
    else:
        predicate = 'a.normalized ~ :boundary'
        pattern, rank = '', 2
    sql = '''
      WITH hits AS (
        SELECT a.entity_id,min(CASE WHEN a.normalized=:q THEN 0 ELSE :rank END) AS rank,
          array_agg(DISTINCT a.alias ORDER BY a.alias) AS matched_aliases
        FROM research.entity_aliases a WHERE a.release_id=:r AND (a.normalized=:q OR ''' + predicate + ''')
        GROUP BY a.entity_id
      )
      SELECT s.entity_id,s.kind,s.name,s.summary,s.reviewed,h.rank,h.matched_aliases,
        s.data->'roles' AS roles FROM hits h JOIN research.entity_snapshots s ON s.entity_id=h.entity_id AND s.release_id=:r
      WHERE s.kind=ANY(CAST(:kinds AS text[])) AND (h.rank,s.entity_id)>(:last_rank,:last_id)
      ORDER BY h.rank,s.entity_id LIMIT :limit
    '''
    return sql, {'r': release_id, 'q': normalized, 'rank': rank, 'pattern': pattern,
        'boundary': r'(^|[^[:alnum:]_])' + re.escape(normalized) + r'([^[:alnum:]_]|$)',
        'kinds': kinds or list(COLLECTIONS.values()), 'last_rank': last_rank, 'last_id': last_id, 'limit': limit}


@router.get('/search')
def search(q: str = Query(..., min_length=1, max_length=100), release_id: uuid.UUID | None = None,
           kind: str | None = Query(None, max_length=20), limit: int = Query(50, ge=1, le=100),
           cursor: str | None = Query(None, max_length=1024), session=Depends(get_research_session)):
    if kind and kind not in COLLECTIONS.values():
        raise ResearchError(422, 'invalid-kind', '研究類別不正確。')
    release = require_release(session, release_id)
    filters = {'q': normalize(q), 'kind': kind}
    last = cursor_value(cursor, release, 'search', filters)
    last_rank, last_id = -1, ''
    if last:
        rank, _, last_id = last.partition('-')
        if rank not in ('0', '1', '2') or not last_id:
            raise ResearchError(422, 'invalid-cursor', '搜尋分頁識別不正確。')
        last_rank = int(rank)
    sql, parameters = search_query(q, release['release_id'], limit + 1, last_rank, last_id, [kind] if kind else None)
    rows = session.execute(text(sql), parameters).mappings().all()
    more, next_cursor = len(rows) > limit, None
    rows = rows[:limit]
    if more:
        value = {'release': str(release['release_id']), 'collection': 'search', 'filter': digest(filters),
                 'last': str(rows[-1]['rank']) + '-' + rows[-1]['entity_id']}
        next_cursor = base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip('=')
    items = []
    for row in rows:
        items.append({**summary(row), 'matched_aliases': row['matched_aliases'],
                      'roles': [role['description'] for role in (row['roles'] or [])]})
    return envelope(release, {'items': items, 'has_more': more, 'next_cursor': next_cursor})
