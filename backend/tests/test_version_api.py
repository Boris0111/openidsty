import copy
from app.models import Theme
from app.assessment_versions import latest_version,prepare_version


def test_version_paging_cross_theme_readonly_diff_and_times(db,client):
    theme=db.get(Theme,'liquid-cooling');first=latest_version(db,theme.id)
    changed=copy.deepcopy(theme.data);changed['assessment']['summary']='需要具名新訂單';changed['assessment']['conditions'].append('新採購條件');changed['assessment']['change_reason']='重新核對訂單範圍'
    second=prepare_version(db,theme.id,changed,theme.checked);db.add(second);db.commit()
    data=client.get('/api/themes/liquid-cooling/assessment/versions?limit=1').json()
    assert data['total']==2 and data['current_version_id']==second.id and len(data['versions'])==1
    assert data['versions'][0]['reviewed']=='2026-10-07' and data['versions'][0]['recorded_at'][:10]!='2026-10-07'
    assert client.get(f'/api/themes/liquid-cooling/assessment/versions/{first.id}').json()['payload']['assessment']['summary']==first.payload['assessment']['summary']
    for query in ('limit=0','limit=101','offset=-1'):assert client.get('/api/themes/liquid-cooling/assessment/versions?'+query).status_code==422
    wrong=latest_version(db,'hbm4').id
    assert client.get(f'/api/themes/liquid-cooling/assessment/versions/{wrong}').status_code==404
    assert client.get(f'/api/themes/liquid-cooling/assessment/compare?from_version={wrong}&to_version={second.id}').status_code==404
    result=client.get(f'/api/themes/liquid-cooling/assessment/compare?from_version={first.id}&to_version={second.id}').json()
    assert result['to']['reason']=='重新核對訂單範圍'
    assert any(c['path']=='assessment.summary' for c in result['changes'])
    assert any(c['path']=='assessment.conditions' and c['kind']=='added' for c in result['changes'])
    assert client.get('/api/themes/liquid-cooling/assessment/compare?from_version=0&to_version=1').status_code==422
    assert client.post('/api/themes/liquid-cooling/assessment/versions').status_code==405
