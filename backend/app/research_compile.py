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
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import unicodedata
import uuid
from sqlalchemy import create_engine, text
from .config import ROOT, DATABASE_URL

SCHEMA = 'research-v1'
COMPILE_LOCK = threading.RLock()


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
        with COMPILE_LOCK:
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


# Every table project() writes, parents before children: the batched writer sends the tables in this order, so
# each foreign key's parent rows exist first. A new projection table MUST be added here, after every table it
# references; ProjectionWriter refuses tables that are not listed.
PROJECTION_ORDER = ('research_releases', 'entities', 'entity_snapshots', 'legacy_mappings', 'listings',
                    'source_identifiers', 'entity_aliases', 'release_sources', 'documents', 'document_revisions',
                    'release_documents', 'research_claims', 'claim_evidence', 'taxonomy_links', 'company_offerings',
                    'offering_claims', 'relations', 'relation_claims', 'assets', 'release_assets', 'legacy_history')
BATCH_ROWS = 1000
STATEMENTS = {}


def statement(table, values, conflict=False):
    """(SQL, parameters) for one row. All table/column names originate in this module, never request strings."""
    json_columns = tuple(isinstance(value, (dict, list)) for value in values.values())
    key = (table, tuple(values), json_columns, conflict)
    sql = STATEMENTS.get(key)
    if sql is None:
        expressions = ['CAST(:' + column + ' AS jsonb)' if is_json else ':' + column
                       for column, is_json in zip(values, json_columns)]
        sql = ('INSERT INTO research.' + table + ' (' + ','.join(values) + ') VALUES (' + ','.join(expressions) + ')' +
               (' ON CONFLICT DO NOTHING' if conflict else ''))
        if len(STATEMENTS) > 1000:  # a few dozen shapes in practice; bound it anyway
            STATEMENTS.clear()
        STATEMENTS[key] = sql
    parameters = {column: canonical(value) if is_json else value
                  for (column, value), is_json in zip(values.items(), json_columns)}
    return sql, parameters


def insert(connection, table, values, conflict=False):
    """Write one row now (callers outside project(), and tests that prepare data)."""
    sql, parameters = statement(table, values, conflict)
    connection.execute(text(sql), parameters)


def write_document(write, release, document_id, version, title, url, kind, data, cited=True):
    revision = digest([document_id, version, title, url, kind, data])
    write('documents', {'document_id': document_id}, True)
    write('document_revisions', {'revision_id': revision, 'document_id': document_id,
        'version_key': version, 'title': title, 'url': url, 'doc_kind': kind, 'data': data}, True)
    if cited:
        write('release_documents', {'release_id': release, 'revision_id': revision}, True)
    return revision


def document(connection, release, document_id, version, title, url, kind, data, cited=True):
    """Write a document revision now; project() uses ProjectionWriter.document instead."""
    return write_document(lambda table, values, conflict=False: insert(connection, table, values, conflict),
                          release, document_id, version, title, url, kind, data, cited)


class ProjectionWriter:
    """Collects project()'s rows and sends them per table in PROJECTION_ORDER, up to BATCH_ROWS rows per execute
    (psycopg runs a multi-row execute as a pipelined executemany). Rows of one table keep the order they were
    added in, so ON CONFLICT DO NOTHING keeps the same row as writing them one by one. immediate=True writes each
    row when it is added, exactly as before batching; only the equivalence checks use it."""

    def __init__(self, connection, immediate=False):
        self.connection, self.immediate = connection, immediate
        self.pending = {table: [] for table in PROJECTION_ORDER}  # table -> [[sql, rows], ...] in add order
        self.texts = {}

    def text(self, sql):
        if sql not in self.texts:
            self.texts[sql] = text(sql)
        return self.texts[sql]

    def insert(self, table, values, conflict=False):
        if table not in self.pending:
            raise ValueError('Projection table missing from PROJECTION_ORDER: ' + table)
        sql, parameters = statement(table, values, conflict)
        if self.immediate:
            self.connection.execute(self.text(sql), parameters)
            return
        runs = self.pending[table]
        if runs and runs[-1][0] == sql:
            runs[-1][1].append(parameters)
        else:  # a new column shape or conflict rule starts a new run; runs are sent in order
            runs.append([sql, [parameters]])

    def document(self, release, document_id, version, title, url, kind, data, cited=True):
        return write_document(self.insert, release, document_id, version, title, url, kind, data, cited)

    def flush(self):
        for table in PROJECTION_ORDER:
            for sql, rows in self.pending[table]:
                for start in range(0, len(rows), BATCH_ROWS):
                    self.connection.execute(self.text(sql), rows[start:start + BATCH_ROWS])
            self.pending[table] = []


def projection_tables(connection, release):
    """Row count and md5 for every projection table: the release's rows, or the whole table for tables that
    releases share (entities, documents, document_revisions, assets), ordered by primary key. Two projections of
    one bundle wrote the same rows exactly when these match (rebuild-check and the writer tests compare them)."""
    result = {}
    for table in PROJECTION_ORDER:
        keys = connection.execute(text(
            'SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) '
            'WHERE i.indrelid=CAST(:name AS regclass) AND i.indisprimary ORDER BY array_position(CAST(i.indkey AS int2[]), a.attnum)'),
            {'name': 'research.' + table}).scalars().all()
        scoped = connection.execute(text(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='research' AND table_name=:name "
            "AND column_name='release_id'"), {'name': table}).scalar_one()
        order = ','.join('t."' + key + '"' for key in keys)  # catalog names of a table listed in this module
        where = ' WHERE t.release_id=CAST(:release AS uuid)' if scoped else ''
        rows, checksum = connection.execute(text(
            "SELECT count(*), md5(coalesce(string_agg(CAST(t AS text), E'\\n' ORDER BY " + order + "), '')) "
            'FROM research.' + table + ' t' + where), {'release': str(release)}).one()
        result[table] = {'rows': rows, 'md5': checksum}
    return result


LEGACY_TABLES = [('theme_assessment_versions', 'assessment'), ('indicators', 'indicator-definition'),
                 ('indicator_observations', 'indicator-observation'), ('technical_documents', 'technical-document'),
                 ('technical_observations', 'technical-observation'), ('technical_reviews', 'technical-review')]


def missing_row():
    from sqlalchemy.exc import NoResultFound
    return NoResultFound('No row was found when one was required')


def legacy_history(connection, release, mappings, writer=None):
    """Copy legacy lineage, retaining original precision, dates and review state. The lookup tables are read
    once each; rows go through `writer` (project()'s ProjectionWriter) or are written now."""
    write = writer.insert if writer else (lambda table, values, conflict=False: insert(connection, table, values, conflict))
    themes_by_indicator = {}
    for indicator_id, theme_id in connection.execute(text('SELECT indicator_id,theme_id FROM public.theme_indicators')):
        themes_by_indicator.setdefault(indicator_id, []).append(theme_id)
    observation_documents = dict(connection.execute(text('SELECT id,document_id FROM public.technical_observations')).all())
    document_scopes = dict(connection.execute(text('SELECT id,data FROM public.technical_documents')).all())
    for table, kind in LEGACY_TABLES:
        for row in connection.execute(text('SELECT * FROM public.' + table + ' ORDER BY id')).mappings():
            payload = clean(dict(row))
            if kind == 'assessment':
                entities = ['theme-' + row['theme_id']]
            elif kind.startswith('indicator-'):
                indicator_id = row['id'] if kind == 'indicator-definition' else row['indicator_id']
                entities = ['theme-' + t for t in themes_by_indicator.get(indicator_id, [])]
            else:
                doc_id = row['id'] if kind == 'technical-document' else row.get('document_id')
                if kind == 'technical-review':
                    if row['observation_id'] not in observation_documents:
                        raise missing_row()
                    doc_id = observation_documents[row['observation_id']]
                if doc_id not in document_scopes:
                    raise missing_row()
                scopes = document_scopes[doc_id]
                entities = ['segment-' + key for key in scopes.get('segments', [])] + ['theme-' + key for key in scopes.get('themes', [])]
            for entity in entities:
                if entity not in mappings:
                    raise ValueError('Legacy history references missing entity ' + entity)
                write('legacy_history', {'release_id': release, 'entity_id': entity, 'history_kind': kind,
                    'legacy_id': entity + ':' + str(row['id']), 'content_hash': digest(payload), 'data': payload})


class Stopwatch:
    """Milliseconds per projection stage; numbers only, never content."""

    def __init__(self):
        self.timings, self.mark = {}, time.perf_counter()

    def lap(self, stage):
        now = time.perf_counter()
        self.timings[stage] = round((now - self.mark) * 1000, 1)
        self.mark = now


def project(connection, bundle, commit, publish=False, reason='Initial legacy migration', *, immediate=False):
    """Project a compiled bundle as a release. Rows are batched per table (ProjectionWriter); immediate=True writes
    them one by one as before and is only for checking that both produce the same projection."""
    clock = Stopwatch()
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
        clock.lap('reused')
        return {'release_id': str(release), 'content_hash': content_hash, 'status': existing['status'], 'reused': True,
                'entities': len(actual), 'timings': clock.timings}
    clock.lap('prepare')
    writer = ProjectionWriter(connection, immediate)
    write = writer.insert
    write('research_releases', {'release_id': release, 'git_commit': commit,
        'schema_version': SCHEMA, 'content_hash': content_hash, 'status': 'preparing', 'reason': reason})
    mappings = {s['entity_id']: s for s in bundle['snapshots']}
    legacy_company = {}
    for snapshot in bundle['snapshots']:
        entity = snapshot['entity_id']
        write('entities', {'entity_id': entity, 'kind': snapshot['kind']}, True)
        write('entity_snapshots', {'release_id': release, **snapshot})
        data = snapshot['data']
        aliases = [(snapshot['name'], 'name')] + [(a, 'alias') for a in data.get('aliases', [])]
        if snapshot['kind'] in ('segment', 'theme'):
            old = data[snapshot['kind']]
            write('legacy_mappings', {'release_id': release, 'kind': snapshot['kind'], 'legacy_key': old, 'entity_id': entity})
        for old in data.get('legacy-keys', []):
            legacy_company[old] = entity
            write('legacy_mappings', {'release_id': release, 'kind': 'company', 'legacy_key': old, 'entity_id': entity})
            aliases.append((old, 'legacy'))
        for listing in data.get('listings', []):
            write('listings', {'release_id': release, 'listing_id': digest([entity, listing]),
                'company_id': entity, **{k.replace('-', '_'): v for k, v in listing.items()}})
            aliases.append((listing['ticker'], 'ticker'))
        for ident in data.get('source-identifiers', []):
            write('source_identifiers', {'release_id': release, 'company_id': entity,
                'provider': ident['provider'], 'value': ident['value'].lstrip('0') if ident['provider'] == 'sec-cik' else ident['value']})
        for alias, kind in aliases:
            write('entity_aliases', {'release_id': release, 'entity_id': entity,
                'alias': alias, 'normalized': normalize(alias), 'alias_kind': kind}, True)
    clock.lap('snapshots')
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
        write('release_sources', {'release_id': release, 'source_id': source['id'],
            'name': source['name'], 'url': source['url'], 'data': source})
    for doc in bundle['documents']:
        for version in doc['versions']:
            revisions[(doc['id'], version['id'])] = writer.document(release, doc['id'], version['id'],
                doc['title'], version['url'], doc['doc-kind'],
                {'document': {k: v for k, v in doc.items() if k != 'versions'}, 'version': version},
                (doc['id'], version['id']) in cited_documents)
    clock.lap('documents')
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
            write('research_claims', {'release_id': release, 'entity_id': entity, 'claim_id': claim['id'],
                **{k: claim[k] for k in ('statement', 'confidence', 'conditions', 'reviewed')}})
            for ordinal, evidence in enumerate(claim['evidence']):
                revision = revisions[(evidence['document-id'], evidence['version-id'])] if 'document-id' in evidence else writer.document(
                    release, 'page-' + digest([evidence['source-id'], evidence['url']]), digest(evidence),
                    evidence['locator'], evidence['url'], 'informative', evidence)
                write('claim_evidence', {'release_id': release, 'entity_id': entity, 'claim_id': claim['id'],
                    'ordinal': ordinal, 'revision_id': revision, 'locator': evidence['locator'],
                    'stance': evidence['stance'], 'applicable_period': evidence['applicable-period'], 'data': evidence})
    clock.lap('claims')
    for item in bundle['taxonomy']:
        write('taxonomy_links', {'release_id': release, 'link_id': item['id'], 'parent_id': item['parent'], 'child_id': item['child']})
    for snapshot in bundle['snapshots']:
        for role in snapshot['data'].get('roles', []):
            write('taxonomy_links', {'release_id': release, 'link_id': 'baseline-' + digest([snapshot['entity_id'], role['segment-id']]),
                'parent_id': role['segment-id'], 'child_id': snapshot['entity_id']}, True)
    for item in bundle['offerings']:
        write('company_offerings', {'release_id': release, 'offering_id': item['id'],
            'company_id': item['company'], 'product_id': item['product'], 'role_id': item['role'], 'conditions': item['conditions']})
        for claim in item['claim-refs']:
            write('offering_claims', {'release_id': release, 'offering_id': item['id'],
                'entity_id': claim['entity-id'], 'claim_id': claim['claim-id']})
    clock.lap('taxonomy_offerings')
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
        write('relations', {'release_id': release, 'relation_id': relation['id'],
            'source_id': source, 'target_id': target, 'kind': relation['kind'], 'direction': relation['direction'],
            'mechanism': relation['mechanism'], 'conditions': relation['conditions'], 'confidence': relation['confidence'],
            'reviewed': relation.get('reviewed'), 'product_id': relation.get('product'),
            'application_id': relation.get('application'), 'data': relation})
        for claim in relation.get('claim-refs', []):
            write('relation_claims', {'release_id': release, 'relation_id': relation['id'],
                'entity_id': claim['entity-id'], 'claim_id': claim['claim-id']})
    clock.lap('relations')
    for key, asset in bundle['assets'].items():
        if not any(key in s['data'].get('diagram-assets', []) for s in bundle['snapshots']):
            continue
        storage = Path(os.getenv('RESEARCH_ASSET_ROOT', '/home/app/research-assets'))
        storage.mkdir(parents=True, exist_ok=True)
        target = storage / asset['sha256']
        content = bytes.fromhex(bundle['asset_bytes'][key])
        if target.exists() and target.read_bytes() != content:
            raise ValueError('Asset storage hash collision')
        if not target.exists():
            with target.open('xb') as output:
                output.write(content)
        write('assets', {'sha256': asset['sha256'], 'storage_key': asset['sha256'],
            'media_type': asset['media-type'], 'byte_size': len(content)}, True)
        write('release_assets', {'release_id': release, 'asset_id': key, 'sha256': asset['sha256'], 'metadata': asset})
    clock.lap('assets')
    legacy_history(connection, release, mappings, writer)
    clock.lap('legacy_history')
    # Nothing above reads the projection tables back, so the rows can wait until here. They must be in the DB
    # before the release turns ready and before activate_bootstrap reads release_head.
    writer.flush()
    clock.lap('flush')
    connection.execute(text("UPDATE research.research_releases SET status='ready' WHERE release_id=:id"), {'id': release})
    if publish:
        writer.flush()
        activate_bootstrap(connection, release, commit, content_hash, reason)
    clock.lap('finish')
    return {'release_id': str(release), 'content_hash': content_hash, 'status': 'published' if publish else 'ready',
            'reused': False, 'entities': len(mappings), 'timings': clock.timings}


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
