"""Validate the declarative catalog before changing any DB association."""
import re
from pathlib import Path
import yaml
from sqlalchemy import select, delete
from .config import DATA_DIR, MAP_DIR
from .models import Theme, Company, Indicator, ThemeIndicator
from .registry import canonical_sources

CATALOG = DATA_DIR / 'theme-indicators.yaml'


def read_definitions(path: Path = CATALOG, theme_ids=None, source_ids=None, company_ids=None):
    root=yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(root,dict) or not isinstance(root.get('version'),str) or not isinstance(root.get('indicators'),list):
        raise ValueError('指標定義須有 version 與 indicators 陣列')
    if theme_ids is None:
        theme_ids={p.stem for p in (MAP_DIR/'themes').glob('*.md')}
    if source_ids is None:source_ids={s['id'] for s in canonical_sources()}
    seen=set()
    for d in root['indicators']:
        if not isinstance(d,dict):raise ValueError('指標定義須為對應表')
        for key in ('id','name','entity','scope','limitations','source_id','dataset','measure'):
            if not isinstance(d.get(key),str) or not d[key].strip():raise ValueError(f'指標 {d.get("id")} 缺少 {key}')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',d['id']) or d['id'] in seen:raise ValueError('指標 ID 不合法或重複')
        seen.add(d['id'])
        for key,values in [('kind',('direct','proxy','background')),('unit',('amount','percent')),('frequency',('monthly','quarterly')),('basis',('monthly','quarterly')),('measure',('revenue','liquid-cooling-sales','wafer-share'))]:
            if d.get(key) not in values:raise ValueError(f'指標 {d["id"]} {key} 不合法')
        if d['frequency']!=d['basis']:raise ValueError('首輪指標 frequency／basis 必須一致')
        if d['unit']=='amount' and d.get('currency') not in ('USD','TWD'):raise ValueError('金額指標須宣告 USD／TWD')
        if d['unit']=='percent' and d.get('currency') is not None:raise ValueError('百分比不能宣告幣別')
        if d['source_id'] not in source_ids:raise ValueError(f'指標 {d["id"]} 引用不存在來源')
        if not isinstance(d.get('themes'),list) or not d['themes'] or any(not isinstance(t,str) or t not in theme_ids for t in d['themes']):raise ValueError('指標引用不存在題材或缺少關聯')
        if d['kind']=='proxy' and company_ids is not None and d['entity'] not in company_ids:raise ValueError('代理指標引用不存在公司')
        if any(k in d for k in ('value','observations','period_start','period_end')):raise ValueError('定義檔不得包含觀測數字／期別')
    return root['indicators']


def import_definitions(session,path: Path = CATALOG):
    definitions=read_definitions(path,set(session.scalars(select(Theme.id))),company_ids=set(session.scalars(select(Company.ticker))))
    for d in definitions:
        session.merge(Indicator(id=d['id'],name=d['name'],kind=d['kind'],unit=d['unit'],frequency=d['frequency'],basis=d['basis'],data=d))
    session.flush()
    session.execute(delete(ThemeIndicator))
    for d in definitions:
        for theme_id in dict.fromkeys(d['themes']):session.add(ThemeIndicator(theme_id=theme_id,indicator_id=d['id']))
    session.flush()
    return {'indicators':len(definitions),'associations':sum(len(set(d['themes'])) for d in definitions)}


if __name__=='__main__':
    from .db import Session,engine
    from .ingest import ingestion_lock
    with ingestion_lock(engine) as acquired:
        if not acquired:print({'status':'skipped_overlap'})
        else:
            with Session() as session:
                print(import_definitions(session));session.commit()
