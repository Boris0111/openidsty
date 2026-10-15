import json
from pathlib import Path
import pytest
from app.classify import classify

SAMPLES = json.loads((Path(__file__).parent / 'fixtures/industry/odm-audit.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('sample', [s for s in SAMPLES if s['expected_odm'] is not None], ids=lambda s: str(s['event_id']))
def test_odm_audited_public_excerpts(sample):
    result = classify(sample['title'], sample['body'], sample['kind'])
    assert ('odm' in result['segments']) == sample['expected_odm']


@pytest.mark.parametrize('title,body,kind', [
    ('鴻海與廣達更新公告', '只有公司名稱與代號，未揭露供應角色', 'announcement'),
    ('鴻海月營收', 'AI 伺服器出貨與伺服器訂單', 'financials'),
    ('軟體更新改善效能', 'AI server assembly and server orders', 'industry_news'),
    ('MLCC 新產能', 'AI server demand at Murata Manufacturing', 'industry_news'),
])
def test_odm_company_routine_software_and_component_exclusion(title, body, kind):
    assert 'odm' not in classify(title, body, kind)['segments']
