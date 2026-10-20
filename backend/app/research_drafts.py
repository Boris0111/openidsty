"""Versioned owner drafts; never changes the published research head."""
import difflib
import json
import os
import re
from pathlib import Path
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
from .research_documents import (MAX_DRAFT, SCHEMA, export_files, normalize_payload, safe_yaml,
                                 form_document, validate_payload, check_document, upload_asset, MAX_ASSET)
from .research_git import ManagedGit, safe_path
from .research_compile import canonical, digest, project
from .research_http import ResearchError
from .research_v2 import detail_payload, entity
from .research_graph_v2 import graph_payload

router = APIRouter(prefix='/api/admin/drafts', tags=['drafts'])


def asset_root():
    return Path(os.getenv('RESEARCH_ASSET_ROOT', '/home/app/research-assets'))


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


def document_parts(path, content):
    check_document(path, content)
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
        baseline = ManagedGit().files(base['git_commit'])
        before = baseline.get('industry-map/README.md', b'').decode('utf-8')
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
        payload = normalize_payload(payload)
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
    return get_draft(connection, draft['draft_id'])


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
    payload = json.loads(json.dumps(current['payload']))
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
    return respond(export_draft(result), result['revision'])


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
    result, _ = validate_payload(current['payload'], asset_root())
    return respond({**result, 'draft_id': str(draft_id), 'revision': current['revision']}, current['revision'])


@router.get('/{draft_id}/diff')
def draft_diff(draft_id: uuid.UUID, against: Literal['base', 'active'] = 'base',
               owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    current = get_draft(connection, draft_id)
    base = base_release(connection, current['base_release_id'] if against == 'base' else None)
    original = export_files(ManagedGit().files(base['git_commit']), asset_root())
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
    result, bundle = validate_payload(current['payload'], asset_root())
    if not result['valid']:
        return respond({**result, 'revision': current['revision']}, current['revision'], 422)
    base = base_release(connection, current['base_release_id'])
    # Reuse the exact compiler/projection/reader contract, then roll back every row.
    # No candidate release is exposed through the public reader role.
    with connection.begin_nested() as candidate:
        try:
            projected = project(connection, bundle, base['git_commit'], reason='Owner-only draft preview')
            release = {'release_id': uuid.UUID(projected['release_id'])}
            detail = detail_payload(connection, release, entity(connection, release, entity_id))
            graph = graph_payload(connection, release, entity_id)
            for asset in detail['assets']:
                sha = asset['url'].split('/assets/')[1].split('?')[0]
                asset['url'] = f'/api/admin/drafts/{draft_id}/assets/{sha}?revision={current["revision"]}'
            response = respond({'release_id': str(current['base_release_id']), 'schema_version': 'research-v1',
                'data': detail, 'graph': graph, 'draft': {'id': str(draft_id), 'revision': current['revision'], 'content_hash': result['content_hash']}}, current['revision'])
        finally:
            candidate.rollback()
    return response


@router.get('/{draft_id}/assets/{sha}')
def draft_asset(draft_id: uuid.UUID, sha: str, revision: int | None = Query(None, ge=1),
                owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    current = get_draft(connection, draft_id, revision)
    if sha not in current['payload']['assets'].values():
        raise ResearchError(404, 'asset-not-found', '草稿未引用此資產。')
    # Full validation includes SVG/media verification, even for a guessed asset URL.
    result, bundle = validate_payload(current['payload'], asset_root())
    if not result['valid']:
        raise ResearchError(422, 'invalid-preview', '請先修正草稿內容，再預覽圖解。')
    asset = next(item for item in bundle['assets'].values() if item['sha256'] == sha)
    return FileResponse(asset_root() / sha, media_type=asset['media-type'],
                        headers={'Cache-Control': 'no-store', 'Content-Security-Policy': "default-src 'none'; sandbox"})
