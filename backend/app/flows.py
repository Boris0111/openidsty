"""Runs outside API workers; database advisory lock also covers manual execution."""
from prefect import flow, task
from app.ingest import run_ingestion

@task(name='fetch-official-sources', retries=1, retry_delay_seconds=30)
def fetch_official_sources():
    return run_ingestion()

@flow(name='official-information', log_prints=True)
def official_information_flow():
    return fetch_official_sources()
