import asyncio
from prefect.client.orchestration import get_client
from app.flows import official_information_flow
from prefect.types.entrypoint import EntrypointType
from app.publication_flows import research_publication_flow, publication_reconciliation_flow

async def configure():
    from prefect.client.schemas.actions import WorkPoolCreate
    async with get_client() as client:
        try:
            await client.read_work_pool('industryflow')
        except Exception as exc:
            from prefect.exceptions import ObjectNotFound
            if not isinstance(exc,ObjectNotFound):
                raise
            await client.create_work_pool(WorkPoolCreate(name='industryflow',type='process'))
    deployment=await official_information_flow.to_deployment(name='hourly',cron='7 * * * *',concurrency_limit=1,tags=['official','hourly'],entrypoint_type=EntrypointType.MODULE_PATH,job_variables={'working_dir':'/workspace/backend','env':{'PYTHONPATH':'/workspace/backend'}})
    await deployment.apply(work_pool_name='industryflow')
    for function, name, interval in [(research_publication_flow, 'publish', None),
                                     (publication_reconciliation_flow, 'minute', 60)]:
        deployment = await function.to_deployment(name=name, interval=interval, concurrency_limit=1,
            tags=['research-publication'], entrypoint_type=EntrypointType.MODULE_PATH,
            job_variables={'working_dir':'/workspace/backend','env':{'PYTHONPATH':'/workspace/backend'}})
        await deployment.apply(work_pool_name='industryflow')

if __name__=='__main__':
    asyncio.run(configure())
