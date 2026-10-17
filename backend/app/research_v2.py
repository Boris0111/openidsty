"""Published research reader contracts. All queries are release-scoped and bounded."""
import base64
import json
import re
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_compile import digest

router = APIRouter(prefix='/api/v2', tags=['research-v2'])
COLLECTIONS = {'companies': 'company', 'products': 'product', 'themes': 'theme', 'concepts': 'concept',
               'research': 'research', 'applications': 'application', 'roles': 'role', 'segments': 'segment'}
CATALOG_KINDS = ['application', 'segment', 'role', 'theme', 'product', 'concept', 'research']


def require_release(session, release_id):
    if release_id is None:
        row = session.execute(text("SELECT r.*,h.generation FROM research.release_head h JOIN research.research_releases r USING(release_id) WHERE r.status='published'")).mappings().first()
        if not row:
            raise ResearchError(503, 'research-unavailable', '新版研究尚未完成初始化。', True)
    else:
        row = session.execute(text("SELECT * FROM research.research_releases WHERE release_id=:id AND status='published'"), {'id': release_id}).mappings().first()
        if not row:
            raise ResearchError(404, 'release-not-found', '找不到這個已發布研究版本。')
    return row


def envelope(release, data):
    return {'release_id': str(release['release_id']), 'schema_version': release['schema_version'], 'data': data}


def entity(session, release, entity_id):
    row = session.execute(text('SELECT * FROM research.entity_snapshots WHERE release_id=:r AND entity_id=:id'),
                          {'r': release['release_id'], 'id': entity_id}).mappings().first()
    if not row:
        raise ResearchError(404, 'entity-not-found', '找不到這筆研究。')
    return row


def summary(row):
    return {'id': row['entity_id'], 'kind': row['kind'], 'name': row['name'],
            'summary': row['summary'], 'reviewed': row['reviewed']}


def cursor_value(cursor, release, collection, filters):
    if not cursor:
        return ''
    try:
        decoded = json.loads(base64.urlsafe_b64decode(cursor + '=' * (-len(cursor) % 4)))
        if (set(decoded) != {'release', 'collection', 'filter', 'last'} or
                not isinstance(decoded['last'], str) or not re.fullmatch('[a-z0-9-]{1,200}', decoded['last'])):
            raise ValueError()
        if (decoded['release'], decoded['collection'], decoded['filter']) != (str(release['release_id']), collection, digest(filters)):
            raise ResearchError(409, 'cursor-conflict', '分頁條件或研究版本已改變，請從第一頁重新讀取。')
        return decoded['last']
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise ResearchError(422, 'invalid-cursor', '分頁識別格式不正確。') from None


def page(session, release, collection, kinds, limit, cursor, market=None, role=None, category=None):
    if market and market not in ('TW', 'US', 'KR', 'JP', 'HK', 'DE', 'NL'):
        raise ResearchError(422, 'invalid-market', '市場條件不正確。')
    for selected in (role, category):
        if selected:
            entity(session, release, selected)
    filters = {'market': market, 'role': role, 'category': category}
    last = cursor_value(cursor, release, collection, filters)
    parameters = {'r': release['release_id'], 'kinds': kinds, 'limit': limit + 1,
                  'last': last, **filters}
    rows = session.execute(text('''
        WITH RECURSIVE descendants(entity_id) AS (
          SELECT CAST(:category AS text)
          UNION SELECT t.child_id FROM research.taxonomy_links t
          JOIN descendants d ON t.parent_id=d.entity_id WHERE t.release_id=:r
        )
        SELECT s.entity_id,s.kind,s.name,s.summary,s.reviewed FROM research.entity_snapshots s
        WHERE s.release_id=:r AND s.kind=ANY(CAST(:kinds AS text[])) AND s.entity_id>:last
          AND (CAST(:market AS text) IS NULL OR EXISTS (
            SELECT 1 FROM research.listings l WHERE l.release_id=:r AND l.company_id=s.entity_id AND l.market=:market))
          AND (CAST(:role AS text) IS NULL OR EXISTS (
            SELECT 1 FROM research.company_offerings o WHERE o.release_id=:r AND o.company_id=s.entity_id AND o.role_id=:role)
            OR EXISTS (SELECT 1 FROM research.taxonomy_links t WHERE t.release_id=:r AND t.parent_id=:role AND t.child_id=s.entity_id))
          AND (CAST(:category AS text) IS NULL OR s.entity_id IN (SELECT entity_id FROM descendants)
            OR EXISTS (SELECT 1 FROM research.company_offerings o WHERE o.release_id=:r AND o.company_id=s.entity_id
              AND (o.product_id IN (SELECT entity_id FROM descendants) OR o.role_id IN (SELECT entity_id FROM descendants))))
        ORDER BY s.entity_id LIMIT :limit
    '''), parameters).mappings().all()
    more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = None
    if more:
        value = {'release': str(release['release_id']), 'collection': collection, 'filter': digest(filters), 'last': rows[-1]['entity_id']}
        next_cursor = base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip('=')
    return {'items': [summary(row) for row in rows], 'next_cursor': next_cursor, 'has_more': more}


@router.get('/manifest')
def manifest(session=Depends(get_research_session)):
    release = require_release(session, None)
    return envelope(release, {'published_at': release['published_at'], 'generation': release['generation']})


@router.get('/catalog')
def catalog(release_id: uuid.UUID | None = None, limit: int = Query(50, ge=1, le=100),
            cursor: str | None = Query(None, max_length=1024), session=Depends(get_research_session)):
    release = require_release(session, release_id)
    result = page(session, release, 'catalog', CATALOG_KINDS, limit, cursor)
    keys = [row['id'] for row in result['items']]
    links = session.execute(text('SELECT link_id,parent_id,child_id FROM research.taxonomy_links WHERE release_id=:r AND parent_id=ANY(CAST(:ids AS text[])) ORDER BY link_id LIMIT 401'), {'r': release['release_id'], 'ids': keys}).mappings().all()
    result['links'] = [dict(row) for row in links[:400]]
    result['links_truncated'] = len(links) > 400
    return envelope(release, result)


@router.get('/resolve')
def resolve(kind: str = Query(..., max_length=20), key: str = Query(..., min_length=1, max_length=200),
            release_id: uuid.UUID | None = None, session=Depends(get_research_session)):
    if kind not in COLLECTIONS.values():
        raise ResearchError(422, 'invalid-kind', '研究類別不正確。')
    release = require_release(session, release_id)
    rows = session.execute(text('''
        SELECT DISTINCT s.entity_id,s.kind,s.name,s.summary,s.reviewed FROM research.entity_snapshots s
        WHERE s.release_id=:r AND s.kind=:kind AND (s.entity_id=:key OR
          EXISTS(SELECT 1 FROM research.legacy_mappings m WHERE m.release_id=:r AND m.entity_id=s.entity_id AND m.kind=:kind AND m.legacy_key=:key) OR
          EXISTS(SELECT 1 FROM research.listings l WHERE l.release_id=:r AND l.company_id=s.entity_id AND l.ticker=:key))
        ORDER BY s.entity_id LIMIT 101
    '''), {'r': release['release_id'], 'kind': kind, 'key': key}).mappings().all()
    if not rows:
        raise ResearchError(404, 'entity-not-found', '找不到這個代號或研究入口。')
    if len(rows) > 1:
        raise ResearchError(409, 'ambiguous-identity', '這個入口對應多個主體，請選擇公司。', candidates=[summary(row) for row in rows[:100]], truncated=len(rows) > 100)
    return envelope(release, summary(rows[0]))


def citation_payload(row):
    data = row['data']
    version = data.get('version', data)
    return {'document_id': row['document_id'], 'revision_id': row['revision_id'], 'title': row['title'],
        'url': row['url'], 'document_kind': row['doc_kind'], 'published': version.get('published'),
        'reviewed': version.get('reviewed'), 'scope': version.get('scope'),
        'read_scope': version.get('read-scope'), 'access_limitations': version.get('access-limitations'),
        'locators': version.get('locators', [{'id': version.get('locator'), 'section': version.get('locator'),
                                            'excerpt': version.get('excerpt')}])}


@router.get('/documents/{document_id}/revisions/{revision_id}')
def document_revision(document_id: str, revision_id: str, release_id: uuid.UUID | None = None,
                      session=Depends(get_research_session)):
    release = require_release(session, release_id)
    rows = session.execute(text('''SELECT d.* FROM research.document_revisions d
        JOIN research.release_documents rd USING(revision_id)
        WHERE rd.release_id=:r AND d.document_id=:doc
          AND (d.revision_id=:revision OR d.version_key=:revision) LIMIT 2'''),
        {'r': release['release_id'], 'doc': document_id, 'revision': revision_id}).mappings().all()
    if not rows or revision_id == 'latest':
        raise ResearchError(404, 'citation-not-found', '找不到這份研究所引用的文件版本。')
    if len(rows) > 1:
        raise ResearchError(409, 'ambiguous-citation', '這個舊引用對應多個版本，請使用研究內的固定版本連結。')
    return envelope(release, citation_payload(rows[0]))


def claims_payload(session, release, entity_id):
    claims = session.execute(text('SELECT * FROM research.research_claims WHERE release_id=:r AND entity_id=:id ORDER BY claim_id LIMIT 101'), {'r': release['release_id'], 'id': entity_id}).mappings().all()
    evidence = session.execute(text('''SELECT e.claim_id,e.ordinal,e.locator,e.stance,e.applicable_period,
        d.revision_id,d.document_id,d.title,d.url,d.doc_kind,d.data FROM research.claim_evidence e
        JOIN research.document_revisions d USING(revision_id)
        WHERE e.release_id=:r AND e.entity_id=:id ORDER BY e.claim_id,e.ordinal LIMIT 401'''),
        {'r': release['release_id'], 'id': entity_id}).mappings().all()
    result = []
    for claim in claims[:100]:
        citations = [{**citation_payload(row), 'locator': row['locator'], 'stance': row['stance'],
                      'applicable_period': row['applicable_period']} for row in evidence[:400] if row['claim_id'] == claim['claim_id']]
        result.append({'id': claim['claim_id'], 'statement': claim['statement'], 'confidence': claim['confidence'],
                      'conditions': claim['conditions'], 'reviewed': claim['reviewed'], 'evidence': citations})
    return result, len(claims) > 100 or len(evidence) > 400


@router.get('/{collection}')
def objects(collection: str, release_id: uuid.UUID | None = None,
            limit: int = Query(50, ge=1, le=100), cursor: str | None = Query(None, max_length=1024),
            market: str | None = Query(None, max_length=8), role: str | None = Query(None, max_length=200),
            category: str | None = Query(None, max_length=200), session=Depends(get_research_session)):
    if collection not in COLLECTIONS:
        raise ResearchError(404, 'collection-not-found', '找不到這個研究目錄。')
    release = require_release(session, release_id)
    return envelope(release, page(session, release, collection, [COLLECTIONS[collection]], limit, cursor, market, role, category))


@router.get('/{collection}/{entity_id}')
def detail(collection: str, entity_id: str, release_id: uuid.UUID | None = None,
           session=Depends(get_research_session)):
    if collection not in COLLECTIONS:
        raise ResearchError(404, 'collection-not-found', '找不到這個研究目錄。')
    release = require_release(session, release_id)
    row = entity(session, release, entity_id)
    if row['kind'] != COLLECTIONS[collection]:
        raise ResearchError(404, 'entity-not-found', '找不到這筆研究。')
    return envelope(release, detail_payload(session, release, row))


def detail_payload(session, release, row):
    """Same curated reader contract for published content and owner-only previews."""
    entity_id = row['entity_id']
    data = row['data']
    fields = ('definition', 'purpose', 'boundary', 'adoption-conditions', 'bottlenecks', 'substitution-limits',
              'scope', 'comparisons', 'related-ids', 'diagram-assets', 'gaps', 'aliases', 'listings',
              'roles', 'research-depth', 'status', 'milestones', 'kpis', 'signals', 'upstream', 'downstream', 'themes', 'segments')
    content = {key.replace('-', '_'): data[key] for key in fields if key in data}
    if 'roles' in content:
        content['roles'] = [{'segment_id': role['segment-id'], 'description': role['description']} for role in content['roles']]
    if data.get('assessment'):
        content['assessment'] = {key: data['assessment'][key] for key in ('summary', 'confidence', 'reviewed', 'conditions', 'gaps', 'paths') if key in data['assessment']}
    if data.get('technical-profile'):
        content['technical_profile'] = {key.replace('-', '_'): value for key, value in data['technical-profile'].items()}
    claims, truncated = claims_payload(session, release, entity_id)
    related = session.execute(text('''SELECT DISTINCT s.entity_id,s.kind,s.name,s.summary,s.reviewed
        FROM research.taxonomy_links t JOIN research.entity_snapshots s ON s.release_id=t.release_id
          AND s.entity_id=CASE WHEN t.parent_id=:id THEN t.child_id ELSE t.parent_id END
        WHERE t.release_id=:r AND (t.parent_id=:id OR t.child_id=:id)
        ORDER BY s.entity_id LIMIT 101'''), {'r': release['release_id'], 'id': entity_id}).mappings().all()
    assets = []
    if data.get('diagram-assets'):
        rows = session.execute(text('SELECT asset_id,sha256,metadata FROM research.release_assets WHERE release_id=:r AND asset_id=ANY(CAST(:ids AS text[])) ORDER BY asset_id'),
            {'r': release['release_id'], 'ids': data['diagram-assets']}).mappings().all()
        assets = [{'id': asset['asset_id'], 'url': '/api/v2/assets/' + asset['sha256'] + '?release_id=' + str(release['release_id']),
                   'alt': asset['metadata']['alt'], 'attribution': asset['metadata']['attribution']} for asset in rows]
    return {**summary(row), 'markdown': row['markdown'], 'content': content, 'claims': claims,
        'assets': assets,
        'legacy_return': legacy_return(session,release,entity_id),
        'related': [summary(item) for item in related[:100]], 'truncated': truncated or len(related) > 100,
        'content_version': row['semantic_hash']}


def legacy_return(session,release,entity_id):
    from urllib.parse import urlencode
    parents=session.execute(text('''WITH RECURSIVE parents(id) AS (
        SELECT CAST(:id AS text) UNION SELECT t.parent_id FROM research.taxonomy_links t
        JOIN parents p ON p.id=t.child_id WHERE t.release_id=:release)
        SELECT s.name,s.data->>'layer' AS layer,s.data->>'segment' AS segment
        FROM parents p JOIN research.entity_snapshots s ON s.entity_id=p.id AND s.release_id=:release
        WHERE s.kind='segment' ORDER BY s.entity_id LIMIT 1'''),{'id':entity_id,'release':release['release_id']}).mappings().first()
    if not parents or parents['layer'] not in ('ai-server','semiconductor') or not parents['segment']:return None
    return {'url':'/?'+urlencode({'layer':parents['layer'],'segment':parents['segment']}),'label':'回到「'+parents['name']+'」產業地圖'}
