"""Authoring validation must protect all previously published read models."""
import copy
import json
import shutil
from pathlib import Path
import pytest
import yaml
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from app.config import MAP_DIR
from app.import_map import import_map,read_doc
from app.ingest import register_sources,save_records
from app.indicator_definitions import import_definitions
from app.models import Company,Event,Financial,IndicatorObservation,Segment,Theme,ThemeAssessmentVersion
from app.theme_updates import updates_payload
from app.industry_connectors import record
from app.connectors import parse_tw
from app.observations import save_observation


def snapshot(db):
    tables={}
    for model in (Event,Financial,IndicatorObservation,Segment,Theme,ThemeAssessmentVersion):
        table=model.__table__
        tables[table.name]=[dict(r) for r in db.execute(select(table).order_by(*table.primary_key.columns)).mappings()]
    tables['updates']=updates_payload(db,list(db.scalars(select(Theme.id).where(Theme.active.is_(True)).order_by(Theme.id))))
    return json.dumps(tables,sort_keys=True,default=str)


def write_doc(path,data,body):
    path.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True,sort_keys=False)+'---\n'+body,encoding='utf-8')


@pytest.mark.parametrize('invalid',['edge','document','date'])
def test_invalid_optional_research_rolls_back_every_projection(db,tmp_path,invalid):
    register_sources(db);import_definitions(db);db.commit()
    save_records(db,'technews-components',[record('液冷設備測試','測試事件，不是 runtime 資料','https://example.invalid/technical-import',None,'unknown')],[],list(db.scalars(select(Company))))
    companies=list(db.scalars(select(Company)))
    events,financials=parse_tw((Path(__file__).parent/'fixtures/tw-revenue.json').read_text(encoding='utf-8'),'revenue','https://example.invalid/revenue',{'2330':'2330.TW'})
    save_records(db,'twse-revenue',events,financials,companies)
    save_observation(db,dict(indicator_id='aaon-liquid-cooling-revenue',source_id='aaon-earnings-metrics',document_identity='test-quarter',dataset='sales',entity='AAON',original_period='2026 Q2',period_start=date(2026,4,1),period_end=date(2026,6,30),basis='quarterly',scope='測試產品',unit='amount',currency='USD',value=Decimal('123.45678901'),published_precision='unknown',date_semantics='unknown',url='https://example.invalid/quarter',raw_excerpt='Synthetic test value.',raw={}))
    db.commit()
    original=snapshot(db)
    copied=tmp_path/'map';shutil.copytree(MAP_DIR,copied)
    path=copied/'ai-server/thermal.md';data,body=read_doc(path)
    if invalid=='edge':
        data['downstream-relations']={'missing':{'kind':'supply'}}
        expected='非實存下游邊'
    else:
        data['technical-profile']={'product-boundary':'測試產品邊界','adoption-conditions':['需驗證'],'bottlenecks':['介面限制'],'substitution-limits':['無跨平台替代證據'],'claims':[{'id':'sample-claim','statement':'僅測試引用','confidence':'inference','evidence':[{'document-id':'missing','version-id':'first','locator':'scope'}]}],'evidence-gaps':['無客戶採用證據'],'reviewed':'2026-10-16' if invalid=='document' else '2026-02-30'}
        expected='引用不存在文件版本' if invalid=='document' else 'reviewed 須為有效'
    write_doc(path,data,body)
    with pytest.raises(ValueError,match=expected):import_map(db,copied)
    assert snapshot(db)==original


def test_technical_only_import_does_not_fabricate_assessment_version_or_tokens(db,tmp_path):
    register_sources(db);import_definitions(db);db.commit()
    before=updates_payload(db,['liquid-cooling']);versions=list(db.scalars(select(ThemeAssessmentVersion.id)))
    copied=tmp_path/'map';shutil.copytree(MAP_DIR,copied)
    path=copied/'themes/liquid-cooling.md';data,body=read_doc(path)
    data['technical-profile']={'product-boundary':'測試研究範圍','adoption-conditions':['需核對介面'],'bottlenecks':['材料與設備整合'],'substitution-limits':['無跨平台替代驗證'],'claims':[],'assessment-claim-ids':[data['assessment']['claims'][0]['id']],'evidence-gaps':['尚無指定材料與冷卻液長期相容性測試'],'reviewed':'2026-10-16'}
    write_doc(path,data,body);import_map(db,copied)
    assert db.get(Theme,'liquid-cooling').data['technical-profile']==data['technical-profile']
    assert list(db.scalars(select(ThemeAssessmentVersion.id)))==versions
    assert updates_payload(db,['liquid-cooling'])==before
