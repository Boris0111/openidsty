"""Validate the canonical map before touching any database projection."""
import json
import subprocess
import sys
import re
import shutil
import tempfile
from pathlib import Path
import yaml
from sqlalchemy import delete, select,update
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

def load_authoring(map_dir: Path):
    """Validate and read one immutable copy, including optional document references."""
    with tempfile.TemporaryDirectory(prefix='industry-authoring-') as temporary:
        snapshot=Path(temporary)/'industry-map'
        shutil.copytree(map_dir,snapshot)
        result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'scripts/validate_map.py'), '--map-dir', str(snapshot)], capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        docs=[read_doc(p) for layer in ('ai-server','semiconductor') for p in sorted((snapshot/layer).glob('*.md'))]
        themes=[read_doc(p) for p in sorted((snapshot/'themes').glob('*.md'))]
        document_path=snapshot/'technical-documents.yaml'
        documents=yaml.safe_load(document_path.read_text(encoding='utf-8')) if document_path.exists() else {'schema-version':'technical-documents-v1','documents':[]}
        from .registry import canonical_sources
        sources=canonical_sources(snapshot/'sources.yaml')
    return docs,themes,documents,sources

def _import_map(session, map_dir: Path, research_path: Path):
    docs,authored_themes,documents,sources=load_authoring(map_dir)
    research = yaml.safe_load(research_path.read_text(encoding='utf-8')) if research_path.exists() else {}
    tickers = {c['ticker'] for d, _ in docs for c in d['companies']}
    validate_research(research, tickers)
    from .assessment_versions import prepare_version
    theme_docs=[]
    for d,prose in authored_themes:
        checked=re.search(r'查核日期[：:]\s*(\d{4}-\d{2}-\d{2})',prose)
        checked=checked[1] if checked else None
        session.scalar(select(Theme).where(Theme.id==d['theme']).with_for_update())
        theme_docs.append((d,prose,checked,prepare_version(session,d['theme'],d,checked)))
    for d, prose in docs:
        session.merge(Segment(id=d['segment'], layer=d['layer'], name=d['name_zh'], position=d['position'], data=d, prose=prose))
    for d,prose,checked,version in theme_docs:
        session.merge(Theme(id=d['theme'],data=d,prose=prose,checked=checked,active=True))
    session.flush()
    for _,_,_,version in theme_docs:
        if version:session.add(version)
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
    theme_ids = [d['theme'] for d,_ in authored_themes]
    session.execute(update(Theme).where(Theme.id.not_in(theme_ids)).values(active=False))
    from .technical_documents import import_documents
    import_documents(session,documents,sources)
    return {'segments': len(docs), 'companies': len(tickers), 'relations': len(research.get('relations', []))}

def import_map(session,map_dir:Path=MAP_DIR,research_path:Path=DATA_DIR/'company-research.yaml'):
    try:
        result=_import_map(session,map_dir,research_path);session.commit();return result
    except Exception:
        session.rollback();raise

if __name__ == '__main__':
    from .db import Session,engine
    from .ingest import ingestion_lock
    with ingestion_lock(engine) as acquired:
        if not acquired:print(json.dumps({'status':'skipped_overlap'}))
        else:
            with Session() as session:
                print(json.dumps(import_map(session),ensure_ascii=False))
