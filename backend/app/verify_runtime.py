"""Read-only runtime audit plus an overlap guard check. Never publishes fixtures."""
import json
from urllib.request import urlopen, Request
from sqlalchemy import select, func, text
from app.db import Session,engine
from app.models import Company,Segment,Theme,Event,Financial,Source
from app.ingest import ingestion_lock,run_ingestion

def get(url,body=None):
    request=Request(url,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=10) as response:
        return json.load(response)

if __name__=='__main__':
    assert engine.dialect.name=='postgresql','Runtime must use PostgreSQL'
    with ingestion_lock(engine) as acquired:
        assert acquired,'Another update is running; rerun this audit after it completes'
        assert run_ingestion()=={'status':'skipped_overlap'}
    with Session() as session:
        counts={model.__tablename__:session.scalar(select(func.count()).select_from(model)) for model in (Segment,Theme,Company,Event,Financial,Source)}
        assert counts['events']>0 and counts['financials']>0
        assert session.scalar(text('SELECT version_num FROM alembic_version'))=='0002'
        assert session.scalar(select(func.count()).select_from(Event).where(Event.source_id=='fixture'))==0
    health=get('http://api:8000/api/health')
    assert health['map_ready']
    deployments=get('http://prefect:4200/api/deployments/filter',{})
    deployment=next(d for d in deployments if d['name']=='hourly')
    assert deployment['work_pool_name']=='industryflow'
    assert deployment['global_concurrency_limit']['active']
    assert deployment['global_concurrency_limit']['limit']==1
    active_schedules=[s for s in deployment['schedules'] if s['active']]
    assert len(active_schedules)==1 and active_schedules[0]['schedule'].get('cron')=='7 * * * *'
    runs=get('http://prefect:4200/api/flow_runs/filter',{'sort':'START_TIME_DESC','limit':10})
    completed=[r for r in runs if r['deployment_id']==deployment['id'] and r['state_type']=='COMPLETED']
    assert completed,'No completed Prefect deployment run'
    print(json.dumps({'counts':counts,'overlap_guard':'passed','hourly_schedule':'7 * * * *','concurrency_limit':1,'completed_run_id':completed[0]['id'],'entrypoint':deployment['entrypoint']},ensure_ascii=False))
