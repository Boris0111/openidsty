from prefect import flow
from .source_updates import process,reconcile


@flow(name='source-updates',retries=0,log_prints=False)
def source_refresh_flow(job_id:str):return process(job_id)


@flow(name='source-reconciliation',retries=0,log_prints=False)
async def source_reconciliation_flow():return await reconcile()
