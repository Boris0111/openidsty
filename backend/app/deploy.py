import asyncio
from prefect.client.orchestration import get_client
from app.flows import official_information_flow
from prefect.types.entrypoint import EntrypointType

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

if __name__=='__main__':
    asyncio.run(configure())
