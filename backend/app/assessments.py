"""Authored research and newly classified information are separate read models."""
import copy
from datetime import date, timezone, timedelta
from sqlalchemy import select
from .models import Source, now
from .registry import canonical_sources
from .research_api import event_query, event_payloads

TAIPEI = timezone(timedelta(hours=8))


def assessment_summary(theme):
    assessment = theme.data.get('assessment')
    return {
        'available': isinstance(assessment, dict),
        'summary': assessment.get('summary') if assessment else None,
        'confidence': assessment.get('confidence') if assessment else None,
        'reviewed': assessment.get('reviewed') if assessment else None,
    }


def candidate_events(session, theme, reference=None):
    reference = reference or now()
    reference = reference.replace(tzinfo=reference.tzinfo or timezone.utc)
    assessment = theme.data.get('assessment') or {}
    baseline = assessment.get('reviewed') or theme.checked
    baseline = date.fromisoformat(baseline) if baseline else None
    candidates, unknown = [], []
    for event in session.scalars(event_query(theme=theme.id)):
        if event.lifecycle != 'published':
            continue
        if event.published_at is None:
            unknown.append(event)
            continue
        published = event.published_at.replace(tzinfo=event.published_at.tzinfo or timezone.utc)
        if baseline and published <= reference and published.astimezone(TAIPEI).date() > baseline:
            candidates.append(event)
    return candidates, unknown


def assessment_payload(session, theme):
    from .assessment_versions import latest_version
    version=latest_version(session,theme.id)
    assessment = copy.deepcopy(theme.data.get('assessment'))
    available = isinstance(assessment, dict)
    definitions = {entry['id']: entry for entry in canonical_sources()}
    sources = list(session.scalars(select(Source)))
    evidence_sources, warnings = {}, []
    for sid in dict.fromkeys(e['source_id'] for e in (assessment or {}).get('evidence', [])):
        definition = definitions.get(sid, {})
        runtime = [row for row in sources if row.id == sid or row.id.startswith(sid + '-')]
        evidence_sources[sid] = {
            'id': sid, 'name': definition.get('name', sid), 'url': definition.get('url'),
            'reachability': definition.get('reachability'), 'checked': definition.get('checked'),
            'runtime': [{'id': row.id, 'status': row.status, 'last_success': row.last_success, 'error': row.error} for row in runtime],
        }
        if definition.get('reachability') == 'unverified':
            warnings.append({'source_id': sid, 'kind': 'unverified', 'message': definition.get('notes') or '原文件可讀性尚未確認；研究查核基準另列。'})
        for row in runtime:
            if row.status in ('failed', 'partial', 'configuration_required'):
                warnings.append({'source_id': sid, 'runtime_source_id': row.id, 'kind': row.status, 'message': row.error})
    if assessment:
        for path in assessment.get('paths', []):
            path['confidence'] = 'inference'
    candidates, unknown = candidate_events(session, theme)
    return {
        'available': available, 'status': theme.data['status'], 'checked': theme.checked,
        'assessment': assessment, 'evidence_sources': evidence_sources, 'source_warnings': warnings,
        'candidates': event_payloads(session, candidates[:8]), 'candidate_count': len(candidates),
        'unknown_date_count': len(unknown), 'undated_candidates': event_payloads(session, unknown[:8]),
        'current_version_id': version.id if version else None,
    }
