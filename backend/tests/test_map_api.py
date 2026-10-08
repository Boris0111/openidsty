import shutil
import pytest
from sqlalchemy import select, func
from app.config import MAP_DIR
from app.import_map import import_map
from app.models import Company, Segment, Role
from app.graph import impact_paths, company_graph

def test_import_is_idempotent_and_unique(db):
    before = db.scalar(select(func.count()).select_from(Company))
    import_map(db)
    assert db.scalar(select(func.count()).select_from(Company)) == before
    assert len(list(db.scalars(select(Role).where(Role.ticker=='AVGO')))) >= 2

def test_invalid_map_leaves_projection_intact(db,tmp_path):
    target=tmp_path/'map'
    shutil.copytree(MAP_DIR,target)
    p=target/'ai-server/thermal.md'
    p.write_text(p.read_text(encoding='utf-8').replace('segment: thermal','segment: compute'),encoding='utf-8')
    with pytest.raises(ValueError):
        import_map(db,target)
    assert db.get(Segment,'thermal').name=='散熱'

def test_three_walks_and_cycles_terminate(db):
    paths=impact_paths(db,['thermal'],5)
    assert any(p['segment']=='pcb' and p['mechanism']=='sibling' for p in paths)
    assert any(p['segment']=='power' and p['mechanism']=='theme' for p in paths)
    assert len(paths)<100
    assert all(len(p['path'])==len(set(p['path'])) for p in paths)

def test_readonly_endpoints_and_complete_graph(client):
    layers=client.get('/api/industries').json()
    for layer in layers:
        graph=client.get(f'/api/industries/{layer["id"]}/graph').json()
        assert sum(not n['external'] for n in graph['nodes'])==layer['segment_count']
        assert len({e['id'] for e in graph['edges']})==len(graph['edges'])
    assert client.post('/api/companies',json={}).status_code==405
    assert client.get('/api/companies/UNKNOWN').status_code==404
    assert client.get('/api/compare?tickers=NVDA').status_code==422
    result=client.get('/api/compare?tickers=NVDA,AMD').json()
    assert result['companies'][0]['financials']==[]
    assert client.get('/api/sources').headers['cache-control']=='no-store'

def test_company_graph_filters_and_keeps_neighbor_edges(db,client):
    graph=company_graph(db,'NVDA')
    assert all(e['review_status']=='confirmed' for e in graph['edges'])
    expanded=company_graph(db,'NVDA',True)
    assert any(e['source']=='2330.TW' and e['target']=='2317.TW' for e in expanded['edges'])
    assert len([e for e in graph['edges'] if e['source']=='2330.TW' and e['target']=='NVDA'])==2
    assert next(n for n in graph['nodes'] if n['id']=='2330.TW')['relevance']=='high'

def test_migration_schema_matches_models(tmp_path):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, inspect
    from app.db import Base
    from app.config import ROOT
    cfg=Config(str(ROOT/'backend/alembic.ini'))
    url=f'sqlite:///{tmp_path.as_posix()}/migration.db'
    cfg.attributes['database_url']=url
    command.upgrade(cfg,'head')
    inspector=inspect(create_engine(url))
    assert set(Base.metadata.tables)<=set(inspector.get_table_names())
    for name,table in Base.metadata.tables.items():
        assert {c.name for c in table.columns}=={c['name'] for c in inspector.get_columns(name)}
    command.upgrade(cfg,'head')
