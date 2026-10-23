"""Public static snapshot of one published research release: structure only, never events, indicators or runtime state.

The route table here and frontend/lib/snapshot-routes.ts must agree; frontend/tests/static/route-cases.json is
checked by both test suites. Run inside the API container: python -m app.public_snapshot --out /export
"""
import argparse
import json
import os
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

COLLECTIONS = ('companies', 'products', 'themes', 'concepts', 'research', 'applications', 'roles', 'segments')
# Directory filters the reader can choose; each value's member list comes from the API, the browser only intersects.
DIRECTORY_FILTERS = {'companies': ('market', 'role', 'category'), 'products': ('category',), 'roles': ('category',)}
MARKETS = ('TW', 'US', 'KR', 'JP', 'HK', 'DE', 'NL')
ID = r'[A-Za-z0-9][A-Za-z0-9._:-]{0,199}'
# (path pattern, exact query keys besides release_id, snapshot file); None marks a key computed in the browser.
ROUTES = [
    (r'/api/industries', (), 'legacy/industries.json'),
    (r'/api/industries/(ai-server|semiconductor)/graph', (), 'legacy/industries/{0}/graph.json'),
    (r'/api/segments', (), 'legacy/segments.json'),
    (r'/api/segments/([a-z0-9-]+)', (), 'legacy/segments/{0}.json'),
    (r'/api/themes', (), 'legacy/themes.json'),
    (r'/api/themes/([a-z0-9-]+)', (), 'legacy/themes/{0}.json'),
    (r'/api/themes/([a-z0-9-]+)/assessment', (), 'legacy/themes/{0}/assessment.json'),
    (r'/api/technical-documents/(' + ID + ')', (('limit', '10'), ('offset', '0')), 'legacy/technical-documents/{0}.json'),
    (r'/api/v2/manifest', (), 'v2/manifest.json'),
    (r'/api/v2/chains', ('release_id',), 'v2/chains.json'),
    (r'/api/v2/chains', (('segment', r'segment-[a-z0-9-]+'),), 'v2/chains/{segment}.json'),
    (r'/api/v2/graphs', (('depth', '1'), 'release_id', ('root', ID)), 'v2/graphs/{root}.json'),
    (r'/api/v2/documents/(' + ID + ')/revisions/(' + ID + ')', ('release_id',), 'v2/documents/{0}/{1}.json'),
    (r'/api/v2/(' + '|'.join(COLLECTIONS) + ')/(' + ID + ')', ('release_id',), 'v2/{0}/{1}.json'),
    (r'/api/v2/resolve', None, 'resolve'),
    (r'/api/v2/search', None, 'search'),
    (r'/api/v2/compare', None, 'compare'),
    (r'/api/v2/(' + '|'.join(COLLECTIONS) + ')', None, 'directory'),
]

# Fields that carry events, monitoring or source runtime state; their presence anywhere in a snapshot is a leak.
FORBIDDEN_KEYS = {'events', 'undated_candidates', 'candidate_count', 'unknown_date_count', 'runtime',
                  'history', 'last_attempt', 'last_success', 'current_version_id', 'list_url'}
# In an assessment `candidates` are event candidates; an ambiguous resolve lists company candidates, which is public.
ASSESSMENT_FORBIDDEN_KEYS = {'candidates'}
ASSET_URL = re.compile(r'/api/v2/assets/([0-9a-f]{64})\?release_id=([0-9a-f-]{36})')
ASSET_EXTENSIONS = {'image/svg+xml': 'svg', 'image/png': 'png', 'image/webp': 'webp', 'image/jpeg': 'jpg', 'image/gif': 'gif'}


def snapshot_route(key, release):
    """Map a normalized reader key (path + sorted query) to ('file', path), ('computed', kind), ('release',) or None."""
    parts = urlsplit(key)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    if len(query) != len(parse_qsl(parts.query, keep_blank_values=True)):
        return None
    for pattern, keys, target in ROUTES:
        match = re.fullmatch(pattern, parts.path)
        if not match:
            continue
        if 'release_id' in query and query['release_id'].lower() != release.lower():
            return ('release',)
        if keys is None:
            return ('computed', target)
        names = {key if isinstance(key, str) else key[0] for key in keys}
        if set(query) != names or any(not isinstance(key, str) and not re.fullmatch(key[1], query[key[0]]) for key in keys):
            continue
        return ('file', target.format(*match.groups(), **query))
    return None


def public_segment(payload):
    return {key: value for key, value in payload.items() if key != 'events'}


def public_theme(payload):
    return {key: value for key, value in payload.items() if key != 'events'}


def public_assessment(payload):
    """Keep the judgment and cited source names; event candidates, version pointers and source runtime stay private."""
    drop = {'candidates', 'undated_candidates', 'candidate_count', 'unknown_date_count', 'current_version_id'}
    result = {key: value for key, value in payload.items() if key not in drop}
    result['evidence_sources'] = {key: {name: value for name, value in source.items() if name != 'runtime'}
                                  for key, source in payload.get('evidence_sources', {}).items()}
    # An unverified source is part of the research note; failed or partial fetches are runtime state.
    result['source_warnings'] = [{'source_id': warning['source_id'], 'kind': warning['kind'], 'message': warning.get('message')}
                                 for warning in payload.get('source_warnings', []) if warning.get('kind') == 'unverified']
    return result


def public_graph(payload):
    """The catalog link points at the private API and no reader page follows it."""
    return {**payload, 'data': {key: value for key, value in payload['data'].items() if key != 'list_url'}}


def public_technical_document(payload):
    return {'id': payload['id'], 'definition': payload['definition']}


def rewrite_assets(value, release, extensions):
    """Point published illustration URLs at the snapshot copy; any other release's asset is a build error."""
    if isinstance(value, dict):
        return {key: rewrite_assets(item, release, extensions) for key, item in value.items()}
    if isinstance(value, list):
        return [rewrite_assets(item, release, extensions) for item in value]
    if isinstance(value, str):
        def replace(match):
            sha, owner = match.groups()
            if owner != release or sha not in extensions:
                raise ValueError(f'asset {sha} is not part of release {release}')
            return f'/snapshot/{release}/assets/{sha}.{extensions[sha]}'
        return ASSET_URL.sub(replace, value)
    return value


def asset_hashes(value):
    if isinstance(value, dict):
        return set().union(*(asset_hashes(item) for item in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(asset_hashes(item) for item in value)) if value else set()
    return {match.group(1) for match in ASSET_URL.finditer(value)} if isinstance(value, str) else set()


def leak_findings(root, secrets=()):
    """Every forbidden key, API path or secret value found under a snapshot or build directory."""
    findings = []
    secrets = [value for value in secrets if len(value) >= 8]
    def walk(value, where, forbidden):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in forbidden:
                    findings.append(f'{where}: forbidden field {key}')
                walk(item, where, forbidden)
        elif isinstance(value, list):
            for item in value:
                walk(item, where, forbidden)
    for path in sorted(Path(root).rglob('*')):
        if not path.is_file() or path.suffix not in ('.json', '.html', '.js', '.txt', '.css', '') and path.name != '_headers':
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        where = path.relative_to(root).as_posix()
        if path.suffix == '.json':
            walk(json.loads(text), where, FORBIDDEN_KEYS | (ASSESSMENT_FORBIDDEN_KEYS if path.name == 'assessment.json' else set()))
            if '"/api/' in text:
                findings.append(f'{where}: private API path')
        findings.extend(f'{where}: secret value' for value in secrets if value in text)
    return findings


def write_json(root, relative, payload):
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')


class SnapshotError(RuntimeError):
    pass


def references(value, key):
    """Every string under `key` anywhere in a payload, e.g. the technical documents a profile cites."""
    if isinstance(value, dict):
        found = {value[key]} if isinstance(value.get(key), str) else set()
        return found.union(*(references(item, key) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(references(item, key) for item in value)) if value else set()
    return set()


def citations(value):
    if isinstance(value, dict):
        found = {(value['document_id'], value['revision_id'])} if isinstance(value.get('document_id'), str) and isinstance(value.get('revision_id'), str) else set()
        return found.union(*(citations(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(citations(item) for item in value)) if value else set()
    return set()


def environment_secrets(environ):
    """Secret values this process can see; any of them in the output fails the export."""
    from sqlalchemy.engine import make_url
    values = [value for name, value in environ.items() if re.search('PASSWORD|SECRET|TOKEN', name) and value]
    for name, value in environ.items():
        if name.endswith('DATABASE_URL') and value:
            password = make_url(value).password
            if password:
                values.append(password)
    return values


@contextmanager
def reader_session():
    from .research_db import get_research_session
    sessions = get_research_session()
    try:
        yield next(sessions)
    finally:
        sessions.close()


def collect(client, session, release_id=None):
    """Every public reader response for the published release, keyed by snapshot path, plus its asset bytes."""
    from fastapi.encoders import jsonable_encoder
    from sqlalchemy import text
    from .research_compare import company_columns
    from .research_v2 import require_release

    def get(path, params=None, allow=(200,)):
        response = client.get(path, params=params or {})
        if response.status_code not in allow:
            raise SnapshotError(f'{path} {params or ""} returned {response.status_code}: {response.text[:300]}')
        return response

    def pages(path, params):
        items, cursor = [], None
        while True:
            body = get(path, {**params, 'limit': 100, **({'cursor': cursor} if cursor else {})}).json()['data']
            items += body['items']
            if not body['has_more']:
                return items
            cursor = body['next_cursor']

    manifest = get('/api/v2/manifest').json()
    release, schema = manifest['release_id'], manifest['schema_version']
    if release_id and release_id.lower() != release.lower():
        raise SnapshotError(f'目前發布的研究版本是 {release}，不是 {release_id}；請匯出目前發布的版本。')
    scoped = {'release_id': release}
    files = {'v2/manifest.json': manifest}

    directories = {collection: pages(f'/api/v2/{collection}', scoped) for collection in COLLECTIONS}
    choices = {'market': list(MARKETS), 'role': [row['id'] for row in directories['roles'] + directories['segments']],
               'category': [row['id'] for row in directories['applications']]}
    for collection, items in directories.items():
        order = [row['id'] for row in items]
        filters = {}
        for name in DIRECTORY_FILTERS.get(collection, ()):
            filters[name] = {}
            for value in choices[name]:
                members = [row['id'] for row in pages(f'/api/v2/{collection}', {**scoped, name: value})]
                positions = [order.index(member) for member in members]
                if positions != sorted(positions):
                    raise SnapshotError(f'{collection} {name}={value} is not ordered like the full directory')
                filters[name][value] = members
        files[f'v2/directory/{collection}.json'] = {'release_id': release, 'schema_version': schema, 'items': items, 'filters': filters}
        for row in items:
            files[f'v2/{collection}/{row["id"]}.json'] = get(f'/api/v2/{collection}/{row["id"]}', scoped).json()
            files[f'v2/graphs/{row["id"]}.json'] = public_graph(get('/api/v2/graphs', {**scoped, 'root': row['id'], 'depth': 1}).json())

    files['v2/chains.json'] = get('/api/v2/chains', scoped).json()
    segments = get('/api/segments').json()
    files['legacy/segments.json'] = segments
    for segment in segments:
        files[f'v2/chains/segment-{segment["id"]}.json'] = get('/api/v2/chains', {'segment': 'segment-' + segment['id']}).json()
        files[f'legacy/segments/{segment["id"]}.json'] = public_segment(get(f'/api/segments/{segment["id"]}').json())
    industries = get('/api/industries').json()
    files['legacy/industries.json'] = industries
    for industry in industries:
        files[f'legacy/industries/{industry["id"]}/graph.json'] = get(f'/api/industries/{industry["id"]}/graph').json()
    themes = get('/api/themes').json()
    files['legacy/themes.json'] = themes
    for theme in themes:
        files[f'legacy/themes/{theme["theme"]}.json'] = public_theme(get(f'/api/themes/{theme["theme"]}').json())
        files[f'legacy/themes/{theme["theme"]}/assessment.json'] = public_assessment(get(f'/api/themes/{theme["theme"]}/assessment').json())

    for document, revision in sorted(citations(list(files.values()))):
        files[f'v2/documents/{document}/{revision}.json'] = get(f'/api/v2/documents/{document}/revisions/{revision}', scoped).json()
    for document in sorted(references(list(files.values()), 'document-id')):
        files[f'legacy/technical-documents/{document}.json'] = public_technical_document(
            get(f'/api/technical-documents/{document}', {'limit': 10, 'offset': 0}).json())

    head = require_release(session, None)
    if str(head['release_id']) != release:
        raise SnapshotError('研究版本在匯出途中改變，請重新匯出。')
    columns = {}
    for row in directories['companies']:
        columns[row['id']] = jsonable_encoder(company_columns(session, head, [row['id']])[0])
        files[f'v2/compare/{row["id"]}.json'] = {'release_id': release, 'schema_version': schema, 'data': columns[row['id']]}
    entities = session.execute(text('''SELECT entity_id,kind,name,summary,reviewed,data->'roles' AS roles
        FROM research.entity_snapshots WHERE release_id=:r ORDER BY entity_id'''), {'r': release}).mappings().all()
    # Aliases keep the database's collation order, which the search ranks and matched_aliases rely on.
    aliases = session.execute(text('''SELECT alias,normalized,entity_id FROM research.entity_aliases
        WHERE release_id=:r ORDER BY alias,entity_id'''), {'r': release}).all()
    files['v2/search.json'] = {'release_id': release, 'schema_version': schema, 'entities': jsonable_encoder([
        {'id': row['entity_id'], 'kind': row['kind'], 'name': row['name'], 'summary': row['summary'], 'reviewed': row['reviewed'],
         'roles': [role['description'] for role in row['roles'] or []]} for row in entities]),
        'aliases': [list(row) for row in aliases]}
    keys = {row[0] for row in session.execute(text('''SELECT legacy_key FROM research.legacy_mappings WHERE release_id=:r AND kind='company'
        UNION SELECT ticker FROM research.listings WHERE release_id=:r'''), {'r': release})}
    keys |= {company['ticker'] for path, payload in files.items() if path.startswith('legacy/segments/') for company in payload.get('companies', [])}
    resolved = {}
    for key in sorted(keys):
        response = get('/api/v2/resolve', {'kind': 'company', 'key': key}, allow=(200, 404, 409))
        # An error's request_id only traces a private-service request and differs on every export.
        resolved[key] = {'status': response.status_code, 'body': {name: value for name, value in response.json().items() if name != 'request_id'}}
    files['v2/resolve.json'] = {'release_id': release, 'keys': resolved}

    assets, extensions = {}, {}
    for sha in sorted(asset_hashes(list(files.values()))):
        response = get(f'/api/v2/assets/{sha}', scoped)
        media = response.headers['content-type'].split(';')[0]
        if media not in ASSET_EXTENSIONS:
            raise SnapshotError(f'asset {sha} has unsupported media type {media}')
        extensions[sha] = ASSET_EXTENSIONS[media]
        assets[f'assets/{sha}.{extensions[sha]}'] = response.content
    files = {path: rewrite_assets(payload, release, extensions) for path, payload in files.items()}
    if get('/api/v2/manifest').json()['release_id'] != release:
        raise SnapshotError('研究版本在匯出途中改變，請重新匯出。')
    counts = {collection: len(items) for collection, items in directories.items()}
    counts.update(documents=sum(path.startswith('v2/documents/') for path in files), assets=len(assets), aliases=len(aliases),
                  technical_documents=sum(path.startswith('legacy/technical-documents/') for path in files),
                  legacy_segments=len(segments), legacy_themes=len(themes), resolve_keys=len(resolved))
    files['manifest.json'] = {'release_id': release, 'schema_version': schema, 'published_at': manifest['data']['published_at'],
                              'generation': manifest['data']['generation'], 'counts': counts}
    return release, files, assets


def export(out, release_id=None, session=None, secrets=()):
    """Write the snapshot to <out>/<release_id>; a failed export or leak leaves any previous copy untouched."""
    import shutil
    from fastapi.testclient import TestClient
    from .main import app
    out = Path(out)
    with TestClient(app) as client:
        if session is None:
            with reader_session() as own:
                release, files, assets = collect(client, own, release_id)
        else:
            release, files, assets = collect(client, session, release_id)
    partial, final = out / f'.{release}.partial', out / release
    shutil.rmtree(partial, ignore_errors=True)
    for relative, payload in sorted(files.items()):
        write_json(partial, relative, payload)
    for relative, content in sorted(assets.items()):
        (partial / relative).parent.mkdir(parents=True, exist_ok=True)
        (partial / relative).write_bytes(content)
    findings = leak_findings(partial, list(secrets) + environment_secrets(os.environ))
    if findings:
        shutil.rmtree(partial, ignore_errors=True)
        raise SnapshotError('快照含有不得公開的內容：\n' + '\n'.join(findings[:50]))
    # Kept apart from manifest.json so two exports of one release are byte-identical everywhere else.
    write_json(partial, 'export.json', {'exported_at': datetime.now(timezone.utc).isoformat(timespec='seconds')})
    shutil.rmtree(final, ignore_errors=True)
    partial.rename(final)
    return final, files['manifest.json']


def main():
    parser = argparse.ArgumentParser(description='Export the published research release as a public static snapshot.')
    parser.add_argument('--out', required=True)
    parser.add_argument('--release-id')
    args = parser.parse_args()
    try:
        folder, manifest = export(args.out, args.release_id)
    except SnapshotError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({'folder': folder.name, **manifest}, ensure_ascii=False))


if __name__ == '__main__':
    main()
