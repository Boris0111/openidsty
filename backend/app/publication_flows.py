"""Publication and minute outbox reconciliation share the existing process worker."""
from prefect import flow
from .research_publication import run_job, reconcile


@flow(name='research-publication', log_prints=False, retries=0)
def research_publication_flow(job_id: str):
    result = run_job(job_id)
    return {'job_id': str(result.get('job_id', job_id)), 'status': result.get('status'), 'busy': result.get('busy', False)}


@flow(name='research-publication-reconciliation', log_prints=False, retries=0)
async def publication_reconciliation_flow():
    return {'submitted': await reconcile()}
