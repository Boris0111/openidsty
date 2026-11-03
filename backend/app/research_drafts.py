"""Versioned owner drafts; never changes the published research head."""
from collections import OrderedDict
import difflib
import json
import logging
import os
import re
from pathlib import Path
import threading
import time
import uuid
from typing import Literal
import yaml
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from .research_auth import require_owner, require_owner_write
from .research_db import get_admin_connection
from .research_documents import (MAX_DRAFT, SCHEMA, ASSET_STORE_ERRORS, export_files, normalize_changes, safe_yaml,
                                 form_document, validate_payload, check_document, upload_asset, MAX_ASSET)
from .research_git import ManagedGit, MissingResearchFile, safe_path
from .research_compile import canonical, digest, project
from .research_http import ResearchError
from .research_v2 import detail_payload, entity
from .research_graph_v2 import graph_payload

router = APIRouter(prefix='/api/admin/drafts', tags=['drafts'])
# uvicorn's logger already prints INFO; the drill benchmark counts full validations from these lines.
log = logging.getLogger('uvicorn.error')


def asset_root():
    return Path(os.getenv('RESEARCH_ASSET_ROOT', '/home/app/research-assets'))


class SharedResults:
    """A small LRU for results of immutable inputs (a commit, a revision's content hash). Concurrent
    misses on one key share a single computation; waiters give up with a retryable 503."""

    def __init__(self, limit, wait=60):
        self.limit, self.wait = limit, wait
        self.lock = threading.Lock()
        self.values = OrderedDict()
        self.running = {}

    def get(self, key, compute, keep=lambda value: True):
        with self.lock:
            if key in self.values:
                self.values.move_to_end(key)
                return self.values[key]
            job = self.running.get(key)
            owner = job is None
            if owner:
                job = self.running[key] = {'done': threading.Event()}
        if not owner:
            if not job['done'].wait(self.wait):
                raise ResearchError(503, 'draft-busy', '同一份草稿仍在處理中，請稍後重試。', retryable=True)
            if 'error' in job:
                raise job['error']
            return job['value']
        try:
            job['value'] = compute()
            if keep(job['value']):
                with self.lock:
                    self.values[key] = job['value']
                    while len(self.values) > self.limit:
                        self.values.popitem(last=False)
            return job['value']
        except BaseException as error:
            job['error'] = error
            raise
        finally:
            with self.lock:
                self.running.pop(key, None)
            job['done'].set()

    def clear(self):
        with self.lock:
            self.values.clear()


# Commits are immutable and assets content-addressed, so a base export never goes stale.
BASE_EXPORTS = SharedResults(2)
# Keyed by draft_revisions.payload_hash; a deploy restarts the process and so drops old validator results.
VALIDATIONS = SharedResults(2)


def base_export(commit):
    return BASE_EXPORTS.get(commit, lambda: export_files(ManagedGit().files(commit), asset_root()))


def validated(current):
    """(result, bundle) for this revision's content; the full compile runs once per content hash."""
    def compute():
        log.info('draft-validation computed draft=%s revision=%s', current['draft_id'], current['revision'])
        return validate_payload(current['payload'], asset_root())
    # Missing or mismatched store files are about the asset store, not the content: retry after a fix.
    return VALIDATIONS.get(current['payload_hash'], compute,
                           keep=lambda value: not set(value[0]['errors']) & ASSET_STORE_ERRORS)


def respond(data, revision=None, status=200):
    headers = {'Cache-Control': 'no-store'}
    if revision is not None:
        headers['ETag'] = '"' + str(revision) + '"'
    return JSONResponse(jsonable_encoder(data), status_code=status, headers=headers)


async def body(request):
    content = bytearray()
    async for part in request.stream():
        content.extend(part)
        if len(content) > MAX_DRAFT:
            raise ResearchError(413, 'draft-too-large', '草稿超過 5 MiB。')
    try:
        value = json.loads(content, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, RecursionError, UnicodeError):
        raise ResearchError(422, 'invalid-draft', '草稿 JSON 格式不正確。') from None


def base_release(connection, release_id=None):
    row = connection.execute(text('''SELECT * FROM research.research_releases WHERE status='published'
        AND release_id=COALESCE(CAST(:id AS uuid),(SELECT release_id FROM research.release_head))'''), {'id': release_id}).mappings().first()
    if not row:
        raise ResearchError(409, 'draft-base-unavailable', '請選擇完整且已發布的研究基準。')
    return row


def get_draft(connection, draft_id, revision=None, *, lock=False):
    draft = connection.execute(text('SELECT * FROM research.editor_drafts WHERE draft_id=:id' + (' FOR UPDATE' if lock else '')),
                               {'id': draft_id}).mappings().first()
    if not draft:
        raise ResearchError(404, 'draft-not-found', '找不到這份草稿。')
    number = revision if revision is not None else draft['current_revision']
    row = connection.execute(text('SELECT * FROM research.draft_revisions WHERE draft_id=:id AND revision=:revision'),
                             {'id': draft_id, 'revision': number}).mappings().first()
    if not row:
        raise ResearchError(404, 'draft-revision-not-found', '找不到這份草稿修訂。')
    return {**dict(draft), 'revision': number, 'payload': row['payload'], 'payload_hash': row['payload_hash'], 'origin': row['origin']}


def export_draft(draft):
    return {'draft_id': str(draft['draft_id']), 'base_release_id': str(draft['base_release_id']),
            'revision': draft['revision'], **draft['payload']}


def draft_summary(draft):
    """Revision, file list and asset map without any file contents (the editor's working view)."""
    return {'draft_id': str(draft['draft_id']), 'base_release_id': str(draft['base_release_id']),
            'revision': draft['revision'], 'schema_version': draft['payload']['schema_version'],
            'paths': sorted(draft['payload']['files']), 'assets': draft['payload']['assets']}


def document_parts(path, content):
    check_document(path, content)
    return split_document(path, content)


def split_document(path, content):
    """Form representation of content that already passed check_document."""
    if path.endswith('.md') and content.startswith('---'):
        sections = re.split(r'^---\s*$', content, maxsplit=2, flags=re.M)
        if len(sections) != 3:
            raise ValueError('Markdown frontmatter 未結束。')
        fields = safe_yaml(sections[1])
        if not isinstance(fields, dict):
            raise ValueError('Frontmatter 必須是欄位物件。')
        return {'path': path, 'content': content, 'frontmatter': fields, 'markdown': sections[2].lstrip('\r\n')}
    return {'path': path, 'content': content, 'frontmatter': None, 'markdown': content}


def protect_baseline(connection, draft, payload):
    base = base_release(connection, draft['base_release_id'])
    try:
        try:
            before = ManagedGit().file(base['git_commit'], 'industry-map/README.md').decode('utf-8')
        except MissingResearchFile:
            before = ''
        if payload['files'].get('industry-map/README.md') != before:
            raise ValueError('網站草稿不可修改 Schema 說明文件。')
    except ValueError as error:
        raise ResearchError(422, 'draft-rejected', str(error)) from None


def save_revision(connection, draft, payload, expected, origin):
    if expected != '"' + str(draft['current_revision']) + '"':
        raise ResearchError(409, 'draft-conflict', '草稿已有較新修訂，請先比對差異；原內容未被覆寫。',
                            current_revision=draft['current_revision'])
    if draft['status'] != 'editing':
        raise ResearchError(409, 'draft-closed', '這份草稿已結束編輯，請另建草稿。')
    try:
        # The current revision passed these checks when it was saved; only edited files are re-checked.
        payload = normalize_changes(draft['payload'], payload)
    except (ValueError, yaml.YAMLError, RecursionError, UnicodeError) as error:
        raise ResearchError(422, 'draft-rejected', str(error)[:12000]) from None
    protect_baseline(connection, draft, payload)
    current_hash = digest(payload)
    if current_hash == draft['payload_hash']:
        return draft  # Saving the same content does not invent a revision.
    revision = draft['current_revision'] + 1
    connection.execute(text('''INSERT INTO research.draft_revisions(draft_id,revision,origin,payload,payload_hash)
        VALUES (:id,:revision,:origin,CAST(:payload AS jsonb),:hash)'''),
        {'id': draft['draft_id'], 'revision': revision, 'origin': origin, 'payload': canonical(payload), 'hash': current_hash})
    connection.execute(text('UPDATE research.editor_drafts SET current_revision=:revision WHERE draft_id=:id'),
                       {'id': draft['draft_id'], 'revision': revision})
    connection.execute(text('''INSERT INTO research.audit_log(actor,operation,detail)
        VALUES ('owner','draft-save',CAST(:detail AS jsonb))'''),
        {'detail': json.dumps({'draft_id': str(draft['draft_id']), 'revision': revision, 'origin': origin})})
    # Same shape as get_draft, built from what was just written instead of re-reading the payload.
    return {**draft, 'current_revision': revision, 'revision': revision, 'payload': payload,
            'payload_hash': current_hash, 'origin': origin}


@router.get('')
def drafts(owner=Depends(require_owner), connection=Depends(get_admin_connection), limit: int = Query(50, ge=1, le=100)):
    rows = connection.execute(text('SELECT * FROM research.editor_drafts ORDER BY created_at DESC,draft_id LIMIT :limit'), {'limit': limit + 1}).mappings().all()
    return respond({'items': [dict(row) for row in rows[:limit]], 'has_more': len(rows) > limit})


@router.post('')
async def create_draft(request: Request, owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    data = await body(request)
    if set(data) - {'base_release_id'}:
        raise ResearchError(422, 'invalid-draft', '建立草稿只接受研究基準。')
    try:
        selected = str(uuid.UUID(data['base_release_id'])) if data.get('base_release_id') else None
    except (ValueError, TypeError, AttributeError):
        raise ResearchError(422, 'invalid-draft', '研究基準格式不正確。') from None
    base = base_release(connection, selected)
    try:
        files = await run_in_threadpool(ManagedGit().files, base['git_commit'])
        payload = await run_in_threadpool(export_files, files, asset_root())
    except (ValueError, UnicodeError, yaml.YAMLError) as error:
        raise ResearchError(422, 'draft-rejected', str(error)[:12000]) from None
    key = uuid.uuid4()
    connection.execute(text("INSERT INTO research.editor_drafts(draft_id,base_release_id,current_revision,status) VALUES(:id,:base,1,'editing')"), {'id': key, 'base': base['release_id']})
    connection.execute(text("INSERT INTO research.draft_revisions(draft_id,revision,origin,payload,payload_hash) VALUES(:id,1,'web',CAST(:payload AS jsonb),:hash)"), {'id': key, 'payload': canonical(payload), 'hash': digest(payload)})
    return respond(export_draft(get_draft(connection, key)), 1, 201)


@router.post('/render-document')
async def render_document(request: Request, owner=Depends(require_owner_write)):
    data = await body(request)
    try:
        path = safe_path(data.get('path'), write=True)
        if set(data) == {'path', 'frontmatter', 'markdown'}:
            content = form_document(data['frontmatter'], data['markdown'])
        elif set(data) == {'path', 'content'}:
            content = data['content']
        else:
            raise ValueError('文件欄位不正確。')
        return respond(document_parts(path, content))
    except (ValueError, TypeError, yaml.YAMLError, RecursionError) as error:
        raise ResearchError(422, 'document-rejected', str(error)[:12000]) from None


@router.post('/asset-upload')
async def asset_upload(request: Request, path: str = Query(..., max_length=240), owner=Depends(require_owner_write)):
    content = bytearray()
    async for part in request.stream():
        content.extend(part)
        if len(content) > MAX_ASSET:
            raise ResearchError(413, 'asset-too-large', '資產超過 10 MiB。')
    try:
        return respond(upload_asset(asset_root(), path, request.headers.get('content-type'), bytes(content)))
    except ValueError as error:
        raise ResearchError(422, 'asset-rejected', str(error)) from None


@router.get('/{draft_id}')
def draft(draft_id: uuid.UUID, owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    result = get_draft(connection, draft_id)
    return respond(export_draft(result), result['revision'])


@router.get('/{draft_id}/summary')
def draft_summary_view(draft_id: uuid.UUID, owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    result = get_draft(connection, draft_id)
    return respond(draft_summary(result), result['revision'])


@router.get('/{draft_id}/export')
def draft_export(draft_id: uuid.UUID, owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    result = get_draft(connection, draft_id)
    response = respond(export_draft(result), result['revision'])
    response.headers['Content-Disposition'] = 'attachment; filename="research-draft-' + str(draft_id) + '.json"'
    return response


@router.get('/{draft_id}/document')
def draft_document(draft_id: uuid.UUID, path: str = Query(..., max_length=240),
                   owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    current = get_draft(connection, draft_id)
    if path not in current['payload']['files']:
        raise ResearchError(404, 'document-not-found', '草稿中沒有這份文件。')
    try:
        return respond(document_parts(path, current['payload']['files'][path]), current['revision'])
    except (ValueError, TypeError, yaml.YAMLError) as error:
        raise ResearchError(422, 'document-rejected', str(error)) from None


@router.patch('/{draft_id}')
async def patch_draft(draft_id: uuid.UUID, request: Request, owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    data = await body(request)
    if set(data) != {'changes'} or not isinstance(data['changes'], list) or len(data['changes']) > 100:
        raise ResearchError(422, 'invalid-draft', '請提供至多 100 筆檔案變更。')
    current = get_draft(connection, draft_id, lock=True)
    # Changes only add, replace or remove file entries, so copying the file map is enough.
    payload = {**current['payload'], 'files': dict(current['payload']['files'])}
    try:
        seen = set()
        for change in data['changes']:
            if not isinstance(change, dict):
                raise ValueError('每筆變更必須是物件。')
            path = safe_path(change.get('path'), write=True)
            if path in seen:
                raise ValueError('一次修改不得重複指定檔案。')
            seen.add(path)
            if set(change) == {'path', 'delete'} and change['delete'] is True:
                payload['files'].pop(path, None)
            elif set(change) == {'path', 'frontmatter', 'markdown'}:
                payload['files'][path] = form_document(change['frontmatter'], change['markdown'])
            elif set(change) == {'path', 'content'} and isinstance(change['content'], str):
                payload['files'][path] = change['content']
            else:
                raise ValueError('檔案變更欄位不正確。')
    except (ValueError, TypeError, yaml.YAMLError, RecursionError) as error:
        raise ResearchError(422, 'draft-rejected', str(error)[:12000]) from None
    result = await run_in_threadpool(save_revision, connection, current, payload, request.headers.get('if-match'), 'web')
    # The editor continues from this response: no follow-up document or draft-list request is needed.
    files = result['payload']['files']
    documents = {change['path']: split_document(change['path'], files[change['path']])
                 for change in data['changes'] if change['path'] in files}
    return respond({**draft_summary(result), 'documents': documents}, result['revision'])


@router.post('/{draft_id}/import')
async def draft_import(draft_id: uuid.UUID, request: Request, owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    data = await body(request)
    current = get_draft(connection, draft_id, lock=True)
    if set(data) != {'draft_id', 'base_release_id', 'revision', 'schema_version', 'files', 'assets'}:
        raise ResearchError(422, 'invalid-draft', '匯入檔案欄位不正確。')
    if data['draft_id'] != str(draft_id) or data['base_release_id'] != str(current['base_release_id']):
        raise ResearchError(409, 'draft-base-conflict', '匯入檔案屬於不同草稿或研究基準。')
    if type(data['revision']) is not int or request.headers.get('if-match') != '"' + str(data['revision']) + '"':
        raise ResearchError(409, 'draft-conflict', '匯入檔案與預期修訂不一致。')
    result = await run_in_threadpool(save_revision, connection, current, {key: data[key] for key in ('schema_version', 'files', 'assets')},
                           request.headers.get('if-match'), 'cli')
    return respond(export_draft(result), result['revision'])


@router.post('/{draft_id}/validate')
def draft_validate(draft_id: uuid.UUID, owner=Depends(require_owner_write), connection=Depends(get_admin_connection), revision: int | None = Query(None, ge=1)):
    current = get_draft(connection, draft_id, revision)
    result, _ = validated(current)
    return respond({**result, 'draft_id': str(draft_id), 'revision': current['revision']}, current['revision'])


@router.get('/{draft_id}/diff')
def draft_diff(draft_id: uuid.UUID, against: Literal['base', 'active'] = 'base',
               owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    current = get_draft(connection, draft_id)
    base = base_release(connection, current['base_release_id'] if against == 'base' else None)
    original = base_export(base['git_commit'])
    changes, total, truncated = [], 0, False
    for path in sorted(set(original['files']) | set(current['payload']['files'])):
        before, after = original['files'].get(path, ''), current['payload']['files'].get(path, '')
        if before == after:
            continue
        diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=path + ' (published)', tofile=path + ' (draft)'))
        if total + len(diff.encode()) > 1024 * 1024:
            truncated = True
            break
        total += len(diff.encode())
        changes.append({'path': path, 'diff': diff})
    return respond({'revision': current['revision'], 'compared_release_id':str(base['release_id']),
        'draft_base_release_id':str(current['base_release_id']), 'changes': changes,
        'assets_changed': original['assets'] != current['payload']['assets'], 'truncated': truncated}, current['revision'])


@router.get('/{draft_id}/preview')
def draft_preview(draft_id: uuid.UUID, entity_id: str = Query(..., max_length=200), revision: int | None = Query(None, ge=1),
                  owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    current = get_draft(connection, draft_id, revision)
    result, bundle = validated(current)
    if not result['valid']:
        return respond({**result, 'revision': current['revision']}, current['revision'], 422)
    base = base_release(connection, current['base_release_id'])
    # Reuse the exact compiler/projection/reader contract, then roll back every row.
    # No candidate release is exposed through the public reader role.
    with connection.begin_nested() as candidate:
        try:
            started = time.perf_counter()
            projected = project(connection, bundle, base['git_commit'], reason='Owner-only draft preview')
            projected_at = time.perf_counter()
            release = {'release_id': uuid.UUID(projected['release_id'])}
            detail = detail_payload(connection, release, entity(connection, release, entity_id))
            detailed_at = time.perf_counter()
            graph = graph_payload(connection, release, entity_id)
            graphed_at = time.perf_counter()
            for asset in detail['assets']:
                sha = asset['url'].split('/assets/')[1].split('?')[0]
                asset['url'] = f'/api/admin/drafts/{draft_id}/assets/{sha}?revision={current["revision"]}'
            response = respond({'release_id': str(current['base_release_id']), 'schema_version': 'research-v1',
                'data': detail, 'graph': graph, 'draft': {'id': str(draft_id), 'revision': current['revision'], 'content_hash': result['content_hash']}}, current['revision'])
        finally:
            candidate.rollback()
    # Stage times only (numbers), never content; scripts/research_draft_bench.py reads these lines.
    log.info('draft-preview timing draft=%s revision=%s project_ms=%.1f flush_ms=%.1f detail_ms=%.1f graph_ms=%.1f',
             draft_id, current['revision'], (projected_at - started) * 1000, projected['timings'].get('flush', 0.0),
             (detailed_at - projected_at) * 1000, (graphed_at - detailed_at) * 1000)
    return response


@router.get('/{draft_id}/assets/{sha}')
def draft_asset(draft_id: uuid.UUID, sha: str, revision: int | None = Query(None, ge=1),
                owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    current = get_draft(connection, draft_id, revision)
    if sha not in current['payload']['assets'].values():
        raise ResearchError(404, 'asset-not-found', '草稿未引用此資產。')
    # Full validation includes SVG/media verification, even for a guessed asset URL; the revision's
    # shared result means a page of diagrams costs one compile, not one per image.
    result, bundle = validated(current)
    if not result['valid']:
        raise ResearchError(422, 'invalid-preview', '請先修正草稿內容，再預覽圖解。')
    asset = next(item for item in bundle['assets'].values() if item['sha256'] == sha)
    return FileResponse(asset_root() / sha, media_type=asset['media-type'],
                        headers={'Cache-Control': 'no-store', 'Content-Security-Policy': "default-src 'none'; sandbox"})
