"""Validate the canonical map before touching any database projection."""
import json
import subprocess
import sys
import re
from pathlib import Path
import yaml
from sqlalchemy import delete, select
from .config import ROOT, MAP_DIR, DATA_DIR
from .models import Company, Segment, Theme, Role, Relation

def read_doc(path):
    _, header, prose = path.read_text(encoding='utf-8').split('---', 2)
    # Make YAML date objects safe for JSON storage.
    return json.loads(json.dumps(yaml.safe_load(header), default=str)), prose.strip()

def validate_research(data, tickers):
    seen = set()
    for ticker, meta in data.get('companies', {}).items():
        if ticker not in tickers or not isinstance(meta.get('aliases', []), list):
            raise ValueError(f'未知公司或 aliases 格式錯誤：{ticker}')
    for r in data.get('relations', []):
        if r['id'] in seen or r['source'] not in tickers or r['target'] not in tickers or r['source'] == r['target']:
            raise ValueError(f'關係識別錯誤：{r["id"]}')
        seen.add(r['id'])
        for key, allowed in {'kind': {'supply','partner'}, 'direction': {'one_way','two_way'}, 'review_status': {'confirmed','candidate'}, 'relevance': {'high','medium','low','unknown'}, 'evidence': {'official_statement','inference'}}.items():
            if r.get(key) not in allowed:
                raise ValueError(f'關係 {r["id"]}：{key} 不合法')
        if r['kind'] == 'supply' and r['direction'] != 'one_way':
            raise ValueError('供應關係須由 supplier 指向 customer')
        if not r.get('reason') or not r.get('checked') or not r.get('source_url', '').startswith('https://'):
            raise ValueError('每筆關係須有理由、查核日與 HTTPS 來源')
        if r['review_status'] == 'confirmed' and r['evidence'] == 'inference':
            raise ValueError('推論證據不得直接升格為已確認關係')

def import_map(session, map_dir: Path = MAP_DIR, research_path: Path = DATA_DIR / 'company-research.yaml'):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'scripts/validate_map.py'), '--map-dir', str(map_dir)], capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    docs = [read_doc(p) for layer in ('ai-server','semiconductor') for p in sorted((map_dir/layer).glob('*.md'))]
    research = yaml.safe_load(research_path.read_text(encoding='utf-8')) if research_path.exists() else {}
    tickers = {c['ticker'] for d, _ in docs for c in d['companies']}
    validate_research(research, tickers)
    for d, prose in docs:
        session.merge(Segment(id=d['segment'], layer=d['layer'], name=d['name_zh'], position=d['position'], data=d, prose=prose))
    for p in sorted((map_dir/'themes').glob('*.md')):
        d, prose = read_doc(p)
        checked = re.search(r'查核日期[：:]\s*(\d{4}-\d{2}-\d{2})', prose)
        session.merge(Theme(id=d['theme'], data=d, prose=prose, checked=checked[1] if checked else None))
    session.flush()
    for d, _ in docs:
        for c in d['companies']:
            meta = research.get('companies', {}).get(c['ticker'], {})
            company = session.get(Company, c['ticker'])
            if not company:
                company = Company(ticker=c['ticker'], name=c['name_zh'])
                session.add(company)
            company.name = c['name_zh']
            company.aliases = list(dict.fromkeys([c['name_zh'], c['ticker']] + meta.get('aliases', [])))
            company.cik = str(meta['cik']).zfill(10) if meta.get('cik') else None
    session.flush()
    session.execute(delete(Role))
    for d, _ in docs:
        for c in d['companies']:
            session.add(Role(ticker=c['ticker'], segment_id=d['segment'], role=c['role'], tier=c['tier']))
    session.execute(delete(Relation))
    for r in research.get('relations', []):
        session.add(Relation(**{k:r[k] for k in ('id','source','target','kind','direction','review_status','relevance')}, data=r))
    # Remove stale structure, while keeping companies referenced by historical events.
    session.execute(delete(Segment).where(Segment.id.not_in([d['segment'] for d, _ in docs])))
    theme_ids = [read_doc(p)[0]['theme'] for p in (map_dir/'themes').glob('*.md')]
    session.execute(delete(Theme).where(Theme.id.not_in(theme_ids)))
    session.commit()
    return {'segments': len(docs), 'companies': len(tickers), 'relations': len(research.get('relations', []))}

if __name__ == '__main__':
    from .db import Session
    with Session() as session:
        print(json.dumps(import_map(session), ensure_ascii=False))
