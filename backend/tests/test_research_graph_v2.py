from app.config import MAP_DIR
from app.import_map import read_doc
from app.research_graph_v2 import bounded_impact
from test_research_v2 import v2


def real_map():
    segments, themes = {}, {}
    for layer in ('ai-server', 'semiconductor'):
        for path in (MAP_DIR / layer).glob('*.md'):
            data, _ = read_doc(path)
            segments['segment-' + data['segment']] = {
                key: ['theme-' + item if key == 'themes' else 'segment-' + item for item in data[key]]
                for key in ('upstream', 'downstream', 'themes')}
    for path in (MAP_DIR / 'themes').glob('*.md'):
        data, _ = read_doc(path)
        themes['theme-' + data['theme']] = ['segment-' + item for item in data['segments']]
    return segments, themes


def test_real_supply_cycle_terminates_with_bounded_distinct_paths():
    segments, themes = real_map()
    result = bounded_impact(segments, themes, 'segment-compute', depth=3)
    assert 0 < len(result['paths']) <= 400
    for path in result['paths']:
        assert len(path['path']) <= 4 and len(path['path']) == len(set(path['path']))
        assert len(path['steps']) == len(path['path']) - 1
        assert all(step['confidence'] == 'inference' for step in path['steps'])


def test_thermal_reaches_pcb_by_common_downstream_and_retains_theme_reason():
    segments, themes = real_map()
    result = bounded_impact(segments, themes, 'segment-thermal', depth=1)
    pcb = next(path for path in result['paths'] if path['segment_id'] == 'segment-pcb' and path['mechanism'] == 'sibling')
    assert pcb['via'] == 'segment-odm' and pcb['steps'][0]['via'] == 'segment-odm'
    assert any(path['segment_id'] == 'segment-power' and path['mechanism'] == 'theme' for path in result['paths'])
    linear = bounded_impact(segments, themes, 'segment-thermal', mode='linear', depth=1)
    assert not any(path['segment_id'] == 'segment-pcb' for path in linear['paths'])
    for mode in ('linear', 'theme', 'sibling'):
        selected = bounded_impact(segments, themes, 'segment-thermal', mode=mode)
        assert all(path['mechanism'] in ({'upstream', 'downstream'} if mode == 'linear' else {mode}) for path in selected['paths'])


def test_impact_caps_are_explicit():
    segments, themes = real_map()
    result = bounded_impact(segments, themes, 'segment-thermal', max_nodes=2, max_edges=1)
    assert result['truncated'] and len(result['paths']) <= 1
    assert {'node-limit', 'edge-limit'} & set(result['truncation_reasons'])


def test_typed_graph_does_not_turn_capability_into_named_supply(v2):
    client, data = v2
    response = client.get('/api/v2/graphs', params={'root': data['keys'][0], 'scope': 'company'})
    assert response.status_code == 200
    graph = response.json()['data']
    assert {edge['kind'] for edge in graph['edges']} == {'classification', 'capability'}
    capability = next(edge for edge in graph['edges'] if edge['kind'] == 'capability')
    assert capability['source'] == data['keys'][0] and capability['target'] == data['product']
    assert '不指認交易客戶' in capability['mechanism']
    assert len(graph['nodes']) == 3 and not graph['truncated']


def test_graph_limits_and_unpublished_root(v2):
    client, data = v2
    graph = client.get('/api/v2/graphs', params={'root': data['keys'][0], 'max_nodes': 1, 'max_edges': 1}).json()['data']
    assert len(graph['nodes']) == 1 and graph['edges'] == [] and graph['truncated']
    assert graph['continue_from'] and graph['list_url']
    assert client.get('/api/v2/graphs', params={'root': data['keys'][2]}).status_code == 404
    assert client.get('/api/v2/graphs', params={'root': data['keys'][0], 'depth': 4}).status_code == 422
    assert client.get('/api/v2/graphs', params={'root': data['keys'][0], 'max_nodes': 501}).status_code == 422


def test_impact_api_preserves_via_and_real_graph_cycle(v2):
    client, _ = v2
    response = client.get('/api/v2/impact', params={'segment_id': 'segment-thermal', 'mode': 'all'})
    assert response.status_code == 200
    pcb = next(path for path in response.json()['data']['paths'] if path['segment_id'] == 'segment-pcb')
    assert pcb['via'] == 'segment-odm' and pcb['mechanism'] == 'sibling'
    graph = client.get('/api/v2/graphs', params={'root': 'segment-thermal', 'depth': 3}).json()['data']
    assert {(edge['source'], edge['target']) for edge in graph['edges']} == {
        ('segment-thermal', 'segment-odm'), ('segment-odm', 'segment-thermal')}
    assert {edge['kind'] for edge in graph['edges']} == {'segment-supply', 'segment-feedback'}
