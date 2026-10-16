"""Runs outside API workers; database advisory lock also covers manual execution."""
from prefect import flow, task
from app.ingest import run_ingestion

@task(name='fetch-official-sources', retries=1, retry_delay_seconds=30)
def fetch_official_sources(only=None,force_documents=False):
    return run_ingestion(only=only,force_documents=force_documents)

@flow(name='official-information', log_prints=True)
def official_information_flow(only=None,force_documents=False):
    return fetch_official_sources(only,force_documents)
