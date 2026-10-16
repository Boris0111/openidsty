"""Authored research and newly classified information are separate read models."""
import copy
from datetime import date, datetime,time, timezone, timedelta
from sqlalchemy import select,func
from .models import Source,Event, now
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


def candidate_query(theme, reference=None):
    reference = reference or now()
    reference = reference.replace(tzinfo=reference.tzinfo or timezone.utc)
    assessment = theme.data.get('assessment') or {}
    baseline = assessment.get('reviewed') or theme.checked
    baseline = date.fromisoformat(baseline) if baseline else None
    q=event_query(theme=theme.id).where(Event.lifecycle=='published')
    start=datetime.combine(baseline+timedelta(days=1),time.min,TAIPEI).astimezone(timezone.utc) if baseline else None
    known=q.where(Event.published_at>=start,Event.published_at<=reference) if start else q.where(False)
    return known,q.where(Event.published_at.is_(None))

def candidate_events(session,theme,reference=None):
    known,unknown=candidate_query(theme,reference)
    return list(session.scalars(known)),list(session.scalars(unknown))


def assessment_payload(session, theme):
    from .assessment_versions import latest_version
    version=latest_version(session,theme.id)
    assessment = copy.deepcopy(theme.data.get('assessment'))
    available = isinstance(assessment, dict)
    evidence_sources,warnings=source_evidence(session,assessment)
    if assessment:
        for path in assessment.get('paths', []):
            path['confidence'] = 'inference'
    known,undated=candidate_query(theme)
    candidate_count=session.scalar(select(func.count()).select_from(known.order_by(None).subquery()))
    unknown_count=session.scalar(select(func.count()).select_from(undated.order_by(None).subquery()))
    candidates=list(session.scalars(known.limit(8)));unknown=list(session.scalars(undated.limit(8)))
    return {
        'available': available, 'status': theme.data['status'], 'checked': theme.checked,
        'assessment': assessment, 'evidence_sources': evidence_sources, 'source_warnings': warnings,
        'candidates': event_payloads(session, candidates), 'candidate_count': candidate_count,
        'unknown_date_count': unknown_count, 'undated_candidates': event_payloads(session, unknown),
        'current_version_id': version.id if version else None,
    }


def source_evidence(session,assessment):
    if 'research_sources' not in session.info:
        sources=list(session.scalars(select(Source)))
        session.info['event_source_names']={source.id:source.name for source in sources}
        session.info['research_sources']=({row.id:dict(row.data,name=row.name,url=row.url) for row in sources},sources)
    definitions,sources=session.info['research_sources']
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
    return evidence_sources,warnings
