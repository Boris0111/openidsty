"""Compile a maintainer-created Git archive into a complete research snapshot.

This bootstrap CLI is not a reader upload endpoint. Managed-clone publication
and owner authorization are implemented separately before web editing is enabled.
"""
import argparse
from datetime import date, datetime
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
import uuid
from sqlalchemy import create_engine, text
from .config import ROOT, DATABASE_URL

SCHEMA = 'research-v1'


def clean(value):
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items() if not k.startswith('_')}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def canonical(value):
    return json.dumps(clean(value), ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC', value).replace('臺', '台').casefold().split())


def compile_archive(content):
    if len(content) > 100 * 1024 * 1024:
        raise ValueError('Bootstrap archive exceeds 100 MiB')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import validate_map as legacy
    from research_schema import validate_research
    with tempfile.TemporaryDirectory(prefix='research-compile-') as temporary:
        folder = Path(temporary)
        total = 0
        seen = set()
        with tarfile.open(fileobj=io.BytesIO(content), mode='r:') as archive:
            for member in archive:
                relative = PurePosixPath(member.name)
                if relative.is_absolute() or '..' in relative.parts or '\\' in member.name:
                    raise ValueError('Unsafe archive path')
                if member.isdir():
                    continue
                if not member.isfile() or member.name in seen:
                    raise ValueError('Archive links/duplicates forbidden')
                if not (member.name.startswith('industry-map/') or member.name in
                        ('data/company-research.yaml', 'data/theme-indicators.yaml')):
                    raise ValueError('Non-research path in archive')
                total += member.size
                if member.size > 10 * 1024 * 1024 or total > 100 * 1024 * 1024:
                    raise ValueError('Oversized archive content')
                seen.add(member.name)
                target = folder / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        map_dir = folder / 'industry-map'
        result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/validate_map.py'),
                                 '--map-dir', str(map_dir)], capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        errors = legacy.Errors()
        previous = legacy.MAP_DIR
        try:
            legacy.MAP_DIR = map_dir
            segments, themes = legacy.load_segments(errors), legacy.load_themes(errors)
            research = validate_research(map_dir, segments, themes, errors, legacy.parse_doc, legacy.load_yaml)
        finally:
            legacy.MAP_DIR = previous
        if errors:
            raise ValueError(str(errors.items))
        snapshots = []
        for kind, values, field in [('segment', segments, 'segment'), ('theme', themes, 'theme')]:
            for key, obj in values.items():
                reviewed = re.search(r'查核日期[：:]\s*(\d{4}-\d{2}-\d{2})', obj['_body'])
                profile = obj.get('technical-profile', {})
                snapshots.append({'entity_id': kind + '-' + key, 'kind': kind, 'name': obj['name_zh'],
                    'summary': profile.get('product-boundary') or obj['name_zh'] + '的供應角色、技術與傳導研究。',
                    'markdown': obj['_body'], 'reviewed': reviewed[1] if reviewed else profile.get('reviewed'),
                    'data': clean(obj)})
        for key, obj in research['entities'].items():
            snapshots.append({'entity_id': key, 'kind': obj['kind'], 'name': obj['name-zh'],
                'summary': obj['summary'], 'markdown': obj['_body'], 'reviewed': obj['reviewed'], 'data': clean(obj)})
        snapshots.sort(key=lambda s: s['entity_id'])
        for snapshot in snapshots:
            snapshot['semantic_hash'] = digest(snapshot)
        sources_yaml = legacy.load_yaml((map_dir / 'sources.yaml').read_text(encoding='utf-8'))
        sources = [dict(source, market=market) for market, groups in sources_yaml.items()
                   for entries in groups.values() for source in entries]
        document_path = map_dir / 'technical-documents.yaml'
        documents = legacy.load_yaml(document_path.read_text(encoding='utf-8'))['documents'] if document_path.exists() else []
        relations_path = folder / 'data/company-research.yaml'
        old_relations = legacy.load_yaml(relations_path.read_text(encoding='utf-8')).get('relations', []) if relations_path.exists() else []
        indicator_path = folder / 'data/theme-indicators.yaml'
        indicators = legacy.load_yaml(indicator_path.read_text(encoding='utf-8')) if indicator_path.exists() else {}
        asset_bytes = {key: (map_dir / asset['path']).read_bytes().hex() for key, asset in research['assets'].items()}
        return clean({'snapshots': snapshots, 'sources': sorted(sources, key=lambda s: s['id']),
                      'documents': documents, 'taxonomy': research['taxonomy'], 'offerings': research['offerings'],
                      'relations': research['relations'], 'legacy_relations': old_relations,
                      'assets': research['assets'], 'asset_bytes': asset_bytes, 'indicator_definitions': indicators})


def insert(connection, table, values, conflict=False):
    # All table/column names originate in this module, never request strings.
    columns = ','.join(values)
    expressions = []
    parameters = {}
    for key, value in values.items():
        if isinstance(value, (dict, list)):
            expressions.append('CAST(:' + key + ' AS jsonb)')
            parameters[key] = canonical(value)
        else:
            expressions.append(':' + key)
            parameters[key] = value
    suffix = ' ON CONFLICT DO NOTHING' if conflict else ''
    connection.execute(text('INSERT INTO research.' + table + ' (' + columns + ') VALUES (' +
                            ','.join(expressions) + ')' + suffix), parameters)


def document(connection, release, document_id, version, title, url, kind, data, cited=True):
    revision = digest([document_id, version, title, url, kind, data])
    insert(connection, 'documents', {'document_id': document_id}, True)
    insert(connection, 'document_revisions', {'revision_id': revision, 'document_id': document_id,
        'version_key': version, 'title': title, 'url': url, 'doc_kind': kind, 'data': data}, True)
    if cited:
        insert(connection, 'release_documents', {'release_id': release, 'revision_id': revision}, True)
    return revision


def legacy_history(connection, release, mappings):
    """Copy legacy lineage, retaining original precision, dates and review state."""
    for table, kind in [('theme_assessment_versions', 'assessment'), ('indicators', 'indicator-definition'),
                        ('indicator_observations', 'indicator-observation'), ('technical_documents', 'technical-document'),
                        ('technical_observations', 'technical-observation'), ('technical_reviews', 'technical-review')]:
        for row in connection.execute(text('SELECT * FROM public.' + table + ' ORDER BY id')).mappings():
            payload = clean(dict(row))
            if kind == 'assessment':
                entities = ['theme-' + row['theme_id']]
            elif kind.startswith('indicator-'):
                indicator_id = row['id'] if kind == 'indicator-definition' else row['indicator_id']
                entities = ['theme-' + t for t in connection.execute(text('SELECT theme_id FROM public.theme_indicators WHERE indicator_id=:id'), {'id': indicator_id}).scalars()]
            else:
                doc_id = row['id'] if kind == 'technical-document' else row.get('document_id')
                if kind == 'technical-review':
                    doc_id = connection.execute(text('SELECT document_id FROM public.technical_observations WHERE id=:id'), {'id': row['observation_id']}).scalar_one()
                scopes = connection.execute(text('SELECT data FROM public.technical_documents WHERE id=:id'), {'id': doc_id}).scalar_one()
                entities = ['segment-' + key for key in scopes.get('segments', [])] + ['theme-' + key for key in scopes.get('themes', [])]
            for entity in entities:
                if entity not in mappings:
                    raise ValueError('Legacy history references missing entity ' + entity)
                insert(connection, 'legacy_history', {'release_id': release, 'entity_id': entity, 'history_kind': kind,
                    'legacy_id': entity + ':' + str(row['id']), 'content_hash': digest(payload), 'data': payload})


def project(connection, bundle, commit, publish=False, reason='Initial legacy migration'):
    content_hash = digest(bundle)
    release = uuid.uuid5(uuid.NAMESPACE_URL, commit + ':' + SCHEMA + ':' + content_hash)
    existing = connection.execute(text('SELECT status,content_hash FROM research.research_releases WHERE release_id=:id'), {'id': release}).mappings().first()
    if existing:
        expected = {s['entity_id']: s['semantic_hash'] for s in bundle['snapshots']}
        stored = connection.execute(text('SELECT entity_id,kind,name,summary,markdown,data,reviewed,semantic_hash FROM research.entity_snapshots WHERE release_id=:id'), {'id': release}).mappings().all()
        actual = {s['entity_id']: digest({k: v for k, v in s.items() if k != 'semantic_hash'}) for s in stored}
        if expected != actual or existing['content_hash'] != content_hash:
            raise ValueError('Existing projection differs from rebuilt archive')
        if publish and existing['status'] == 'ready':
            activate_bootstrap(connection, release, commit, content_hash, reason)
            existing = {**existing, 'status': 'published'}
        return {'release_id': str(release), 'content_hash': content_hash, 'status': existing['status'], 'reused': True, 'entities': len(actual)}
    insert(connection, 'research_releases', {'release_id': release, 'git_commit': commit,
        'schema_version': SCHEMA, 'content_hash': content_hash, 'status': 'preparing', 'reason': reason})
    mappings = {s['entity_id']: s for s in bundle['snapshots']}
    legacy_company = {}
    for snapshot in bundle['snapshots']:
        entity = snapshot['entity_id']
        insert(connection, 'entities', {'entity_id': entity, 'kind': snapshot['kind']}, True)
        insert(connection, 'entity_snapshots', {'release_id': release, **snapshot})
        data = snapshot['data']
        aliases = [(snapshot['name'], 'name')] + [(a, 'alias') for a in data.get('aliases', [])]
        if snapshot['kind'] in ('segment', 'theme'):
            old = data[snapshot['kind']]
            insert(connection, 'legacy_mappings', {'release_id': release, 'kind': snapshot['kind'], 'legacy_key': old, 'entity_id': entity})
        for old in data.get('legacy-keys', []):
            legacy_company[old] = entity
            insert(connection, 'legacy_mappings', {'release_id': release, 'kind': 'company', 'legacy_key': old, 'entity_id': entity})
            aliases.append((old, 'legacy'))
        for listing in data.get('listings', []):
            insert(connection, 'listings', {'release_id': release, 'listing_id': digest([entity, listing]),
                'company_id': entity, **{k.replace('-', '_'): v for k, v in listing.items()}})
            aliases.append((listing['ticker'], 'ticker'))
        for ident in data.get('source-identifiers', []):
            insert(connection, 'source_identifiers', {'release_id': release, 'company_id': entity,
                'provider': ident['provider'], 'value': ident['value'].lstrip('0') if ident['provider'] == 'sec-cik' else ident['value']})
        for alias, kind in aliases:
            insert(connection, 'entity_aliases', {'release_id': release, 'entity_id': entity,
                'alias': alias, 'normalized': normalize(alias), 'alias_kind': kind}, True)
    revisions = {}
    cited_documents = set()

    def find_citations(value):
        if isinstance(value, dict):
            if 'document-id' in value and 'version-id' in value:
                cited_documents.add((value['document-id'], value['version-id']))
            for child in value.values():
                find_citations(child)
        elif isinstance(value, list):
            for child in value:
                find_citations(child)

    find_citations([s['data'] for s in bundle['snapshots']])
    for source in bundle['sources']:
        insert(connection, 'release_sources', {'release_id': release, 'source_id': source['id'],
            'name': source['name'], 'url': source['url'], 'data': source})
    for doc in bundle['documents']:
        for version in doc['versions']:
            revisions[(doc['id'], version['id'])] = document(connection, release, doc['id'], version['id'],
                doc['title'], version['url'], doc['doc-kind'],
                {'document': {k: v for k, v in doc.items() if k != 'versions'}, 'version': version},
                (doc['id'], version['id']) in cited_documents)
    for snapshot in bundle['snapshots']:
        entity = snapshot['entity_id']
        authored_claims = list(snapshot['data'].get('claims', []))
        assessment = snapshot['data'].get('assessment')
        if assessment:
            evidence_by_id = {e['id']: e for e in assessment['evidence']}
            for old in assessment['claims']:
                evidence = []
                for evidence_id in old['evidence_ids']:
                    item = evidence_by_id[evidence_id]
                    evidence.append({'source-id': item['source_id'], 'url': item['url'],
                        'locator': evidence_id, 'read-scope': '保留既有判讀的必要摘錄與原查核日',
                        'excerpt': item['excerpt'], 'published': item['published'],
                        'stance': old['stance'], 'applicable-period': item['period']})
                authored_claims.append({'id': old['id'], 'statement': old['statement'],
                    'confidence': old['confidence'], 'conditions': assessment['conditions'],
                    'reviewed': assessment['reviewed'], 'evidence': evidence})
        for claim in authored_claims:
            insert(connection, 'research_claims', {'release_id': release, 'entity_id': entity, 'claim_id': claim['id'],
                **{k: claim[k] for k in ('statement', 'confidence', 'conditions', 'reviewed')}})
            for ordinal, evidence in enumerate(claim['evidence']):
                revision = revisions[(evidence['document-id'], evidence['version-id'])] if 'document-id' in evidence else document(
                    connection, release, 'page-' + digest([evidence['source-id'], evidence['url']]), digest(evidence),
                    evidence['locator'], evidence['url'], 'informative', evidence)
                insert(connection, 'claim_evidence', {'release_id': release, 'entity_id': entity, 'claim_id': claim['id'],
                    'ordinal': ordinal, 'revision_id': revision, 'locator': evidence['locator'],
                    'stance': evidence['stance'], 'applicable_period': evidence['applicable-period'], 'data': evidence})
    for item in bundle['taxonomy']:
        insert(connection, 'taxonomy_links', {'release_id': release, 'link_id': item['id'], 'parent_id': item['parent'], 'child_id': item['child']})
    for snapshot in bundle['snapshots']:
        for role in snapshot['data'].get('roles', []):
            insert(connection, 'taxonomy_links', {'release_id': release, 'link_id': 'baseline-' + digest([snapshot['entity_id'], role['segment-id']]),
                'parent_id': role['segment-id'], 'child_id': snapshot['entity_id']}, True)
    for item in bundle['offerings']:
        insert(connection, 'company_offerings', {'release_id': release, 'offering_id': item['id'],
            'company_id': item['company'], 'product_id': item['product'], 'role_id': item['role'], 'conditions': item['conditions']})
        for claim in item['claim-refs']:
            insert(connection, 'offering_claims', {'release_id': release, 'offering_id': item['id'],
                'entity_id': claim['entity-id'], 'claim_id': claim['claim-id']})
    relations = list(bundle['relations'])
    for snapshot in bundle['snapshots']:
        if snapshot['kind'] != 'segment':
            continue
        data = snapshot['data']
        for target in data['downstream']:
            meta = data.get('downstream-relations', {}).get(target, {})
            relations.append({'id': 'segment-' + data['segment'] + '-to-' + target,
                'source': snapshot['entity_id'], 'target': 'segment-' + target,
                'kind': 'segment-feedback' if meta.get('kind') == 'demand-feedback' else 'segment-supply',
                'direction': 'directed', 'mechanism': meta.get('summary', '既有上下游結構；尚未核對交付條件。'),
                'conditions': meta.get('conditions', ['僅環節拓樸，不證明公司交易。']),
                'confidence': meta.get('confidence', 'needs-verification'), 'reviewed': meta.get('reviewed'),
                'legacy': True, 'metadata': meta})
    for old in bundle['legacy_relations']:
        relations.append({'id': 'legacy-' + old['id'], 'source': legacy_company[old['source']],
            'target': legacy_company[old['target']], 'kind': 'named-supply' if old['kind'] == 'supply' else 'partnership',
            'direction': 'symmetric' if old['direction'] == 'two_way' else 'directed',
            'mechanism': old['reason'], 'conditions': [old['relevance_reason']],
            'confidence': 'well-supported' if old['review_status'] == 'confirmed' else 'inference',
            'reviewed': old['checked'], 'legacy': True, 'original': old, 'review_status': old['review_status']})
    for relation in relations:
        source, target = relation['source'], relation['target']
        if relation['direction'] == 'symmetric':
            source, target = sorted([source, target])
        insert(connection, 'relations', {'release_id': release, 'relation_id': relation['id'],
            'source_id': source, 'target_id': target, 'kind': relation['kind'], 'direction': relation['direction'],
            'mechanism': relation['mechanism'], 'conditions': relation['conditions'], 'confidence': relation['confidence'],
            'reviewed': relation.get('reviewed'), 'product_id': relation.get('product'),
            'application_id': relation.get('application'), 'data': relation})
        for claim in relation.get('claim-refs', []):
            insert(connection, 'relation_claims', {'release_id': release, 'relation_id': relation['id'],
                'entity_id': claim['entity-id'], 'claim_id': claim['claim-id']})
    for key, asset in bundle['assets'].items():
        if not any(key in s['data'].get('diagram-assets', []) for s in bundle['snapshots']):
            continue
        storage = Path('/home/app/research-assets')
        storage.mkdir(parents=True, exist_ok=True)
        target = storage / asset['sha256']
        content = bytes.fromhex(bundle['asset_bytes'][key])
        if target.exists() and target.read_bytes() != content:
            raise ValueError('Asset storage hash collision')
        if not target.exists():
            with target.open('xb') as output:
                output.write(content)
        insert(connection, 'assets', {'sha256': asset['sha256'], 'storage_key': asset['sha256'],
            'media_type': asset['media-type'], 'byte_size': len(content)}, True)
        insert(connection, 'release_assets', {'release_id': release, 'asset_id': key, 'sha256': asset['sha256'], 'metadata': asset})
    legacy_history(connection, release, mappings)
    connection.execute(text("UPDATE research.research_releases SET status='ready' WHERE release_id=:id"), {'id': release})
    if publish:
        activate_bootstrap(connection, release, commit, content_hash, reason)
    return {'release_id': str(release), 'content_hash': content_hash, 'status': 'published' if publish else 'ready',
            'reused': False, 'entities': len(mappings)}


def activate_bootstrap(connection, release, commit, content_hash, reason):
    connection.execute(text('SELECT pg_advisory_xact_lock(38109071)'))
    if connection.execute(text('SELECT count(*) FROM research.release_head')).scalar_one():
        raise ValueError('Bootstrap refuses to replace an existing head; use owner publication')
    connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"), {'id': release})
    insert(connection, 'release_head', {'singleton': True, 'release_id': release, 'generation': 1})
    insert(connection, 'audit_log', {'actor': 'bootstrap-cli', 'operation': 'bootstrap', 'release_id': release,
        'detail': {'git_commit': commit, 'content_hash': content_hash, 'reason': reason}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--bootstrap', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40,64}', args.commit):
        raise ValueError('Full Git commit required')
    engine = create_engine(DATABASE_URL, hide_parameters=True)
    if engine.url.database not in ('industry_research', 'industry_research_test'):
        raise ValueError('Explicit isolated research database required')
    bundle = compile_archive(sys.stdin.buffer.read(100 * 1024 * 1024 + 1))
    with engine.begin() as connection:
        result = project(connection, bundle, args.commit, args.bootstrap)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
