import copy
from app.models import Segment
from app.graph import industry_graph,impact_paths,segment_relation


def test_demand_feedback_is_distinct_and_graph_cycle_keeps_identity(db,client):
    graph=industry_graph(db,'ai-server')
    edge=next(e for e in graph['edges'] if e['id']=='datacenter:compute')
    assert edge['kind']=='demand-feedback' and edge['direction']=='one_way'
    assert edge['source_name']=='資料中心與雲端業者' and edge['target_name']=='運算晶片'
    assert edge['relation']['conditions'] and edge['relation']['gaps']
    detail=client.get('/api/segments/datacenter').json()
    assert edge in detail['relations']
    assert 'compute' in detail['downstream']
    paths=impact_paths(db,['memory'],5)
    assert any(p['segment']=='compute' and p['mechanism']=='downstream' for p in paths)
    assert all(len(p['path'])==len(set(p['path'])) for p in paths)


def test_legacy_edge_is_unreviewed_without_assumed_supply(db):
    source=db.get(Segment,'thermal');target=db.get(Segment,'odm')
    data=copy.deepcopy(source.data);data.pop('downstream-relations',None);source.data=data
    edge=segment_relation(source,target)
    assert edge['id']=='thermal:odm' and edge['kind']=='unreviewed'
    assert edge['relation']['confidence']=='needs-verification' and edge['relation']['gaps']
    assert edge['relation']['evidence']==[]
    paths=impact_paths(db,['thermal'],5)
    assert any(p['segment']=='pcb' and p['mechanism']=='sibling' for p in paths)
    assert any(p['segment']=='power' and p['mechanism']=='theme' for p in paths)


def test_explanations_do_not_change_any_of_the_three_walks(db):
    with_metadata={sid:impact_paths(db,[sid],5) for sid in ('memory','thermal','advanced-packaging')}
    originals={s.id:copy.deepcopy(s.data) for s in db.query(Segment).all()}
    for sid,data in originals.items():
        without=copy.deepcopy(data);without.pop('downstream-relations',None);db.get(Segment,sid).data=without
    db.flush()
    assert {sid:impact_paths(db,[sid],5) for sid in with_metadata}==with_metadata
