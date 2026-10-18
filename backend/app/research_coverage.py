"""Owner-only maintenance coverage. Reader pages keep only claim-level limits."""
import re
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text, select, func
from sqlalchemy.orm import Session
from .research_auth import require_owner
from .research_db import get_admin_connection
from .research_drafts import respond
from .research_http import ResearchError
from .research_api import coverage, event_payloads
from .models import Theme, Event, TechnicalDocument, TechnicalObservation, TechnicalReview

router = APIRouter(prefix='/api/admin', tags=['coverage'])
GAP_STATUSES = ('not-researched', 'not-public', 'not-obtained', 'not-applicable')
RESEARCH_KINDS = ('company', 'application', 'role', 'product', 'concept', 'research')
SAMPLE = 5


def citations(data):
    """Which authored claim cites which fixed document version and locator."""
    found = {}
    for claim in (data.get('technical-profile') or {}).get('claims', []):
        for reference in claim.get('evidence', []):
            if 'document-id' in reference:
                found.setdefault(reference['document-id'], []).append(
                    {'claim_id': claim.get('id'), 'version_id': reference.get('version-id'), 'locator': reference.get('locator')})
    return found


def technical_reviews(session, ids):
    """Adopted baselines come from the authored manifest; candidates are bounded per document."""
    if not ids:
        return {}
    counts = {}
    for document, status, count in session.execute(select(TechnicalObservation.document_id, TechnicalReview.status, func.count())
            .join(TechnicalReview).where(TechnicalObservation.document_id.in_(ids))
            .group_by(TechnicalObservation.document_id, TechnicalReview.status)):
        counts.setdefault(document, {})[status] = count
    ranked = (select(TechnicalObservation.document_id, TechnicalObservation.id, TechnicalObservation.official_version,
                     TechnicalObservation.fetched_at, TechnicalObservation.url, TechnicalReview.status, TechnicalReview.reason,
                     func.row_number().over(partition_by=TechnicalObservation.document_id,
                                            order_by=TechnicalObservation.id.desc()).label('rank'))
              .join(TechnicalReview).where(TechnicalObservation.document_id.in_(ids), TechnicalReview.status != 'adopted').subquery())
    candidates = {}
    for row in session.execute(select(ranked).where(ranked.c.rank <= SAMPLE).order_by(ranked.c.document_id, ranked.c.rank)).mappings():
        candidates.setdefault(row['document_id'], []).append({'observation_id': row['id'], 'official_version': row['official_version'],
            'fetched_at': row['fetched_at'], 'url': row['url'], 'status': row['status'], 'reason': row['reason']})
    result = {}
    for document in session.scalars(select(TechnicalDocument).where(TechnicalDocument.id.in_(ids))):
        result[document.id] = {
            'id': document.id, 'title': document.title, 'doc_kind': document.doc_kind, 'active': document.active,
            'adopted': [{'version_id': v['id'], 'label': v.get('label'), 'reviewed': v.get('reviewed'),
                         'read_scope': v.get('read-scope'),
                         'locators': [{'id': l['id'], 'section': l.get('section')} for l in v.get('locators', [])]}
                        for v in document.data.get('versions', [])],
            'review_counts': counts.get(document.id, {}),
            'candidates': candidates.get(document.id, [])}
    return result


def theme_candidates(session, themes):
    from .assessments import candidate_query
    result = {}
    for theme in themes:
        known, undated = candidate_query(theme)
        result[theme.id] = {
            'baseline': (theme.data.get('assessment') or {}).get('reviewed') or theme.checked,
            'status': 'awaiting-assessment',
            'dated_count': session.scalar(select(func.count()).select_from(known.order_by(None).subquery())),
            'undated_count': session.scalar(select(func.count()).select_from(undated.order_by(None).subquery())),
            'samples': [{'id': e['id'], 'title': e['title'], 'published_at': e['published_at'], 'source_name': e['source_name']}
                        for e in event_payloads(session, list(session.scalars(known.limit(SAMPLE))))]}
    return result


@router.get('/coverage')
def scope_coverage(owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    session = Session(bind=connection, expire_on_commit=False)
    data = coverage(session)
    rows = data['rows']
    documents = technical_reviews(session, sorted({d['id'] for row in rows for d in row['technical_documents']}))
    themes = {t.id: t for t in session.scalars(select(Theme).where(Theme.active.is_(True)))}
    pending = theme_candidates(session, themes.values())
    from .models import Segment
    authored = {('segment', s.id): s.data for s in session.scalars(select(Segment))}
    authored.update({('theme', key): theme.data for key, theme in themes.items()})
    for row in rows:
        cited = citations(authored.get((row['kind'], row['id'])) or {})
        row['technical_documents'] = [{**documents[d['id']], 'citations': cited.get(d['id'], [])}
                                      for d in row['technical_documents'] if d['id'] in documents]
        row['assessment_candidates'] = pending.get(row['id']) if row['kind'] == 'theme' else None
        row.pop('samples', None)  # Event samples stay on the maintenance report and events page.
    return respond({**data, 'rows': rows,
        'review_note': '待核對候選與待納入判讀事件只在管理端呈現；一般閱讀只保留影響主張的研究限制。'})


CURSOR = re.compile(r'^(?P<kind>[a-z]+):(?P<entity>[a-z0-9-]{1,200})$')
GAP_SQL = '''WITH head AS (SELECT release_id FROM research.release_head WHERE singleton),
base AS (
  SELECT s.release_id,s.entity_id,s.kind,s.name,s.reviewed,s.data->>'research-depth' AS research_depth,
    (SELECT count(*) FROM research.research_claims c WHERE c.release_id=s.release_id AND c.entity_id=s.entity_id) AS claims,
    g.not_researched,g.not_public,g.not_obtained,g.not_applicable,g.unclassified,
    (s.kind='company' AND s.data->>'research-depth' IS DISTINCT FROM 'deep') AS implied_not_researched
  FROM research.entity_snapshots s JOIN head USING(release_id)
  CROSS JOIN LATERAL (SELECT
      count(*) FILTER (WHERE jsonb_typeof(x)='object' AND x->>'status'='not-researched') AS not_researched,
      count(*) FILTER (WHERE jsonb_typeof(x)='object' AND x->>'status'='not-public') AS not_public,
      count(*) FILTER (WHERE jsonb_typeof(x)='object' AND x->>'status'='not-obtained') AS not_obtained,
      count(*) FILTER (WHERE jsonb_typeof(x)='object' AND x->>'status'='not-applicable') AS not_applicable,
      count(*) FILTER (WHERE jsonb_typeof(x)='string') AS unclassified
    FROM jsonb_array_elements(CASE WHEN jsonb_typeof(s.data->'gaps')='array' THEN s.data->'gaps' ELSE '[]'::jsonb END) x) g
  WHERE s.kind=ANY(CAST(:kinds AS text[]))),
counted AS (
  SELECT *, not_researched+CASE WHEN implied_not_researched AND not_researched=0 THEN 1 ELSE 0 END AS effective_not_researched
  FROM base)'''


@router.get('/coverage/entities')
def entity_coverage(owner=Depends(require_owner), connection=Depends(get_admin_connection),
                    kind: str | None = Query(None, max_length=20), status: str | None = Query(None, max_length=20),
                    cursor: str | None = Query(None, max_length=230), limit: int = Query(50, ge=1, le=100)):
    if kind is not None and kind not in RESEARCH_KINDS:
        raise ResearchError(422, 'invalid-kind', '不支援的研究類型。')
    if status is not None and status not in (*GAP_STATUSES, 'unclassified'):
        raise ResearchError(422, 'invalid-gap-status', '不支援的缺口狀態。')
    after = CURSOR.fullmatch(cursor) if cursor else None
    if cursor and not after:
        raise ResearchError(422, 'invalid-cursor', '分頁位置無效。')
    head = connection.execute(text('SELECT release_id FROM research.release_head WHERE singleton')).scalar()
    if head is None:
        raise ResearchError(409, 'publication-base-missing', '尚未建立完整正式研究。')
    kinds = [kind] if kind else list(RESEARCH_KINDS)
    totals = connection.execute(text(GAP_SQL + '''
        SELECT kind,count(*) AS entities,count(*) FILTER (WHERE implied_not_researched) AS basic_companies,
          sum(effective_not_researched) AS not_researched,sum(not_public) AS not_public,sum(not_obtained) AS not_obtained,
          sum(not_applicable) AS not_applicable,sum(unclassified) AS unclassified
        FROM counted GROUP BY kind ORDER BY kind'''), {'kinds': kinds}).mappings().all()
    column = {'not-researched': 'effective_not_researched', 'not-public': 'not_public', 'not-obtained': 'not_obtained',
              'not-applicable': 'not_applicable', 'unclassified': 'unclassified'}.get(status)
    rows = connection.execute(text(GAP_SQL + '''
        SELECT c.entity_id,c.kind,c.name,c.reviewed,c.research_depth,c.claims,c.implied_not_researched,
          c.effective_not_researched AS not_researched,c.not_public,c.not_obtained,c.not_applicable,c.unclassified,
          s.data->'gaps' AS gaps
        FROM counted c JOIN research.entity_snapshots s ON s.release_id=c.release_id AND s.entity_id=c.entity_id
        WHERE (CAST(:after_kind AS text) IS NULL OR (c.kind,c.entity_id)>(CAST(:after_kind AS text),CAST(:after_entity AS text)))
          AND (''' + (f'c.{column}>0' if column else 'true') + ''')
        ORDER BY c.kind,c.entity_id LIMIT :limit'''),
        {'kinds': kinds, 'after_kind': after['kind'] if after else None, 'after_entity': after['entity'] if after else None,
         'limit': limit + 1}).mappings().all()
    items = []
    for row in rows[:limit]:
        gaps = row['gaps'] if isinstance(row['gaps'], list) else []
        items.append({**{key: row[key] for key in row.keys() if key != 'gaps'},
                      'gaps': [{'status': g['status'], 'reason': g['reason']} if isinstance(g, dict)
                               else {'status': None, 'reason': g} for g in gaps]})
    return respond({'release_id': str(head), 'totals': [dict(row) for row in totals], 'items': items,
        'has_more': len(rows) > limit,
        'next_cursor': f"{rows[limit - 1]['kind']}:{rows[limit - 1]['entity_id']}" if len(rows) > limit else None,
        'definitions': {'not-researched': '未研究', 'not-public': '未公開', 'not-obtained': '未取得',
                        'not-applicable': '不適用', 'unclassified': '未分類（舊文字缺口）'},
        'counting': '缺口計數只取已發布研究；basic 公司即使沒有明列也計一筆未研究。研究限制文字列為未分類，不代表待辦。'})
