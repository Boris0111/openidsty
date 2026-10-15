"""Metric source failures are isolated from events and financial ingestion."""
from .models import Source,now
from .metric_connectors import fetch_metrics
from .observations import save_observation
from .source_diagnostics import failure_details


def ingest_metric_source(session,definition,http,fetcher=fetch_metrics):
    source=session.get(Source,definition['id'])
    source.last_attempt=now();source.new_count=0;session.commit()
    try:
        records=fetcher(definition,http)
        if not records:raise ValueError('HTTP 可讀但未取得有效指標數值')
        count=sum(save_observation(session,row) for row in records)
        meta=definition.get('_fetch_meta',{})
        warnings=meta.get('warnings',[])
        source.status='partial' if warnings else 'success'
        source.error='；'.join(warnings)[:1200] if warnings else None
        source.last_success=now();source.new_count=count
        source.data=dict(source.data,last_error_kind='partial' if warnings else None,last_http_status=None,fetch_meta=meta)
        if definition.get('_backfill'):
            source.data=dict(source.data,backfill_meta=meta)
            # A bounded, partially readable archive still has a completed first attempt.
            # Keep its limitations; hourly checks should not refetch all eight reports.
            source.data=dict(source.data,backfill_completed_at=now().isoformat())
        session.commit()
    except Exception as exc:
        session.rollback();source=session.get(Source,definition['id'])
        source.status='failed';source.error=f'{type(exc).__name__}: {exc}'[:1200]
        source.new_count=0;source.data=dict(source.data,**failure_details(exc))
        if definition.get('_fetch_meta'):source.data=dict(source.data,fetch_meta=definition['_fetch_meta'])
        session.commit()
    return {'status':source.status,'new_count':source.new_count,'error':source.error}
