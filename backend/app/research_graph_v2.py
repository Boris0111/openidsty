"""Bounded typed exploration and three structural inference walks."""
from collections import deque
from typing import Literal
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release, envelope, entity, summary

router = APIRouter(prefix='/api/v2', tags=['research-graph'])

EDGE_SQL = '''
WITH edges AS (
  SELECT 'relation:'||r.relation_id AS id,r.source_id AS source,r.target_id AS target,r.kind,r.direction,
    r.mechanism,r.conditions,r.confidence,r.reviewed,
    COALESCE((SELECT jsonb_agg(jsonb_build_object('entity_id',c.entity_id,'claim_id',c.claim_id))
      FROM research.relation_claims c WHERE c.release_id=r.release_id AND c.relation_id=r.relation_id),'[]') AS claims,
    COALESCE(r.data->'metadata'->'evidence','[]') AS evidence,
    r.data#>>'{original,source_url}' AS evidence_url
  FROM research.relations r WHERE r.release_id=:r AND COALESCE(r.data->>'review_status','confirmed')<>'candidate'
  UNION ALL
  SELECT 'classification:'||t.link_id,t.parent_id,t.child_id,'classification','directed',
    '研究分類與供應角色索引','[]'::jsonb,NULL::text,NULL::date,'[]'::jsonb,'[]'::jsonb,NULL::text
  FROM research.taxonomy_links t WHERE t.release_id=:r
  UNION ALL
  SELECT 'offering:'||o.offering_id,o.company_id,o.product_id,'capability','directed',
    '產品供應能力；此連線不指認交易客戶。',o.conditions,
    COALESCE((SELECT CASE WHEN bool_and(c.confidence='well-supported') THEN 'well-supported'
      WHEN bool_or(c.confidence='needs-verification') THEN 'needs-verification' ELSE 'inference' END
      FROM research.offering_claims q JOIN research.research_claims c USING(release_id,entity_id,claim_id)
      WHERE q.release_id=o.release_id AND q.offering_id=o.offering_id),'inference'),NULL::date,
    COALESCE((SELECT jsonb_agg(jsonb_build_object('entity_id',q.entity_id,'claim_id',q.claim_id))
      FROM research.offering_claims q WHERE q.release_id=o.release_id AND q.offering_id=o.offering_id),'[]'),
    '[]'::jsonb,NULL::text
  FROM research.company_offerings o WHERE o.release_id=:r
)
SELECT * FROM edges WHERE NOT(id=ANY(CAST(:skip AS text[]))) AND
'''


def edge_rows(session, release, frontier, skip, limit, induced=False):
    condition = ('source=ANY(CAST(:frontier AS text[])) AND target=ANY(CAST(:frontier AS text[]))' if induced else
                 '(source=ANY(CAST(:frontier AS text[])) OR target=ANY(CAST(:frontier AS text[])))')
    return session.execute(text(EDGE_SQL + condition + ' ORDER BY id LIMIT :limit'),
        {'r': release['release_id'], 'frontier': sorted(frontier), 'skip': sorted(skip), 'limit': limit}).mappings().all()


@router.get('/graphs')
def graph(root: str = Query(..., max_length=200),
          scope: Literal['application', 'segment', 'product', 'company', 'theme'] | None = None,
          depth: int = Query(1, ge=1, le=3), max_nodes: int = Query(200, ge=1, le=500),
          max_edges: int = Query(400, ge=1, le=1000), release_id: uuid.UUID | None = None,
          session=Depends(get_research_session)):
    release = require_release(session, release_id)
    return envelope(release, graph_payload(session, release, root, scope, depth, max_nodes, max_edges))


def graph_payload(session, release, root, scope=None, depth=1, max_nodes=200, max_edges=400):
    center = entity(session, release, root)
    nodes, frontier, edges = {root}, {root}, {}
    reasons, continuation = set(), set()
    for _ in range(depth):
        if not frontier:
            break
        remaining = max_edges - len(edges)
        rows = edge_rows(session, release, frontier, edges, remaining + 1)
        if len(rows) > remaining:
            reasons.add('edge-limit')
        new_frontier = set()
        for row in rows[:remaining]:
            additions = {row['source'], row['target']} - nodes
            if len(nodes) + len(additions) > max_nodes:
                reasons.add('node-limit')
                continuation.update(additions)
                continue
            nodes.update(additions)
            new_frontier.update(additions)
            edges[row['id']] = dict(row)
        frontier = new_frontier
        if len(edges) >= max_edges:
            break
    # Include links among visible neighbours, preserving real cycles and directions.
    remaining = max_edges - len(edges)
    internal = edge_rows(session, release, nodes, edges, remaining + 1, induced=True)
    if len(internal) > remaining:
        reasons.add('edge-limit')
    edges.update({row['id']: dict(row) for row in internal[:remaining]})
    if frontier:
        outside = edge_rows(session, release, frontier, edges, 1)
        if outside:
            reasons.add('depth-limit')
            continuation.update({outside[0]['source'], outside[0]['target']} - nodes)
    rows = session.execute(text('SELECT entity_id,kind,name,summary,reviewed FROM research.entity_snapshots WHERE release_id=:r AND entity_id=ANY(CAST(:ids AS text[])) ORDER BY entity_id LIMIT :limit'),
                           {'r': release['release_id'], 'ids': sorted(nodes), 'limit': max_nodes}).mappings().all()
    return {'root': root, 'scope': scope or (center['kind'] if center['kind'] in ('application', 'segment', 'product', 'company', 'theme') else 'product'),
        'depth': depth, 'nodes': [summary(row) for row in rows], 'edges': list(edges.values()),
        'truncated': bool(reasons), 'truncation_reasons': sorted(reasons),
        'continue_from': sorted(continuation)[:20], 'list_url': '/api/v2/catalog?release_id=' + str(release['release_id'])}


def impact_moves(segment_id, segments, themes, mode):
    data = segments[segment_id]
    moves = []
    if mode in ('linear', 'all'):
        moves += [(target, 'upstream', None) for target in data['upstream']]
        moves += [(target, 'downstream', None) for target in data['downstream']]
    if mode in ('theme', 'all'):
        for theme in data['themes']:
            moves += [(target, 'theme', theme) for target in themes.get(theme, [])]
    if mode in ('sibling', 'all'):
        for downstream in data['downstream']:
            if downstream in segments:
                moves += [(target, 'sibling', downstream) for target in segments[downstream]['upstream']]
    return moves


def bounded_impact(segments, themes, seed, mode='all', depth=1, max_nodes=200, max_edges=400):
    paths, results, reasons = {seed: ([seed], [])}, [], set()
    queue = deque([(seed, 0)])
    seen_moves = set()
    descriptions = {'upstream': '沿既有上游結構推導', 'downstream': '沿既有下游結構推導',
                    'theme': '透過共同題材擴散，仍需驗證相同技術條件', 'sibling': '供應同一下游的並列環節，仍需驗證產品是否同受影響'}
    while queue:
        current, level = queue.popleft()
        path, steps = paths[current]
        moves = impact_moves(current, segments, themes, mode)
        if level >= depth:
            if any(target not in paths for target, _, _ in moves if target in segments):
                reasons.add('depth-limit')
            continue
        for target, kind, via in moves:
            if target not in segments:
                reasons.add('input-limit')
                continue
            identity = (current, target, kind, via)
            if target in path or identity in seen_moves:
                continue
            seen_moves.add(identity)
            if len(results) >= max_edges:
                reasons.add('edge-limit')
                continue
            if target not in paths and len(paths) >= max_nodes:
                reasons.add('node-limit')
                continue
            step = {'from': current, 'to': target, 'type': kind, 'via': via,
                    'confidence': 'inference', 'reason': descriptions[kind]}
            results.append({'segment_id': target, 'path': path + [target], 'steps': steps + [step],
                            'mechanism': kind, 'via': via, 'reason': descriptions[kind], 'confidence': 'inference'})
            if target not in paths:
                paths[target] = (path + [target], steps + [step])
                queue.append((target, level + 1))
    return {'paths': results, 'truncated': bool(reasons), 'truncation_reasons': sorted(reasons)}


@router.get('/impact')
def impact(segment_id: str = Query(..., max_length=200), mode: Literal['linear', 'theme', 'sibling', 'all'] = 'all',
           depth: int = Query(1, ge=1, le=3), max_nodes: int = Query(200, ge=1, le=500),
           max_edges: int = Query(400, ge=1, le=1000), release_id: uuid.UUID | None = None,
           session=Depends(get_research_session)):
    release = require_release(session, release_id)
    seed = segment_id if segment_id.startswith('segment-') else 'segment-' + segment_id
    if entity(session, release, seed)['kind'] != 'segment':
        raise ResearchError(422, 'invalid-impact-root', '請選擇環節作為影響推導起點。')
    rows = session.execute(text('''SELECT entity_id,name,data->'upstream' AS upstream,data->'downstream' AS downstream,
        data->'themes' AS themes,data->'companies' AS companies FROM research.entity_snapshots
        WHERE release_id=:r AND kind='segment' ORDER BY (entity_id=:seed) DESC,entity_id LIMIT 501'''),
        {'r': release['release_id'], 'seed': seed}).mappings().all()
    segments = {row['entity_id']: {'name': row['name'],
        'upstream': ['segment-' + key for key in row['upstream']],
        'downstream': ['segment-' + key for key in row['downstream']],
        'themes': ['theme-' + key for key in row['themes']], 'companies': row['companies']} for row in rows[:500]}
    theme_rows = []
    if mode in ('theme', 'all'):
        theme_rows = session.execute(text("SELECT entity_id,data->'segments' AS segments FROM research.entity_snapshots WHERE release_id=:r AND kind='theme' ORDER BY entity_id LIMIT 501"), {'r': release['release_id']}).mappings().all()
    themes = {row['entity_id']: ['segment-' + key for key in row['segments']] for row in theme_rows[:500]}
    result = bounded_impact(segments, themes, seed, mode, depth, max_nodes, max_edges)
    if len(rows) > 500 or len(theme_rows) > 500:
        result['truncated'] = True
        result['truncation_reasons'] = sorted(set(result['truncation_reasons']) | {'input-limit'})
    targets = {path['segment_id'] for path in result['paths']}
    tickers = sorted({c['ticker'] for target in targets for c in segments[target]['companies'][:100]})
    companies = session.execute(text('''SELECT m.legacy_key,s.entity_id,s.name FROM research.legacy_mappings m
        JOIN research.entity_snapshots s USING(release_id,entity_id)
        WHERE m.release_id=:r AND m.kind='company' AND m.legacy_key=ANY(CAST(:tickers AS text[]))'''),
        {'r': release['release_id'], 'tickers': tickers}).mappings().all()
    by_ticker = {row['legacy_key']: {'id': row['entity_id'], 'name': row['name']} for row in companies}
    for path in result['paths']:
        data = segments[path['segment_id']]
        path['name'] = data['name']
        path['companies'] = [by_ticker[c['ticker']] for c in data['companies'][:100] if c['ticker'] in by_ticker]
        path['companies_truncated'] = len(data['companies']) > 100
        path['companies_url'] = '/api/v2/companies?role=' + path['segment_id'] + '&release_id=' + str(release['release_id'])
        if path['companies_truncated']:
            result['truncated'] = True
            result['truncation_reasons'] = sorted(set(result['truncation_reasons']) | {'company-limit'})
    return envelope(release, {'root': seed, 'mode': mode, 'depth': depth, **result})
