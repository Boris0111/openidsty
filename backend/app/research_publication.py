"""Durable publication outbox. Only workers write managed Git or activate a head."""
import asyncio
import json
import os
import re
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from .research_auth import require_owner, require_owner_write
from .research_db import get_admin_connection, writer_engine
from .research_http import ResearchError
from .research_compile import SCHEMA, canonical, digest, project, compile_archive
from .research_documents import validate_payload, materialize
from .research_git import ManagedGit, make_archive
from .research_drafts import body, base_release, get_draft, respond, asset_root, protect_baseline, validated

router = APIRouter(prefix='/api/admin', tags=['publication'])
HEAD_LOCK = 38109071


def active(connection):
    row = connection.execute(text('SELECT release_id,generation FROM research.release_head WHERE singleton')).mappings().first()
    if not row:
        raise ResearchError(409, 'publication-base-missing', '尚未建立完整正式研究。')
    return row


@router.get('/releases')
def releases(owner=Depends(require_owner), connection=Depends(get_admin_connection),
             limit: int = Query(50, ge=1, le=100), cursor: uuid.UUID | None = None):
    rows = connection.execute(text('''SELECT release_id,git_commit,schema_version,content_hash,published_at,reason
        FROM research.research_releases WHERE status='published' AND
        (CAST(:cursor AS uuid) IS NULL OR (created_at,release_id)<
         (SELECT created_at,release_id FROM research.research_releases WHERE release_id=:cursor))
        ORDER BY created_at DESC,release_id DESC LIMIT :limit'''), {'cursor':cursor,'limit':limit+1}).mappings().all()
    return respond({'items':[dict(row) for row in rows[:limit]], 'has_more':len(rows)>limit,
        'next_cursor':str(rows[limit-1]['release_id']) if len(rows)>limit else None,
        'active_release_id':str(active(connection)['release_id'])})


@router.get('/audit')
def audit(owner=Depends(require_owner), connection=Depends(get_admin_connection),
          limit: int = Query(50, ge=1, le=100), cursor: int | None = Query(None, ge=1)):
    rows = connection.execute(text('''SELECT * FROM research.audit_log WHERE
        (CAST(:cursor AS bigint) IS NULL OR audit_id<:cursor) ORDER BY audit_id DESC LIMIT :limit'''),
        {'cursor':cursor,'limit':limit+1}).mappings().all()
    return respond({'items':[dict(row) for row in rows[:limit]],'has_more':len(rows)>limit,
        'next_cursor':rows[limit-1]['audit_id'] if len(rows)>limit else None})


@router.get('/sources')
def sources(owner=Depends(require_owner), connection=Depends(get_admin_connection),
            limit: int = Query(50, ge=1, le=100), cursor: str | None = Query(None, max_length=100)):
    rows = connection.execute(text('''SELECT id,name,url,status,last_attempt,last_success,new_count,left(error,4096) AS error,data->>'adapter' AS adapter
        FROM public.sources WHERE (CAST(:cursor AS text) IS NULL OR id>:cursor) ORDER BY id LIMIT :limit'''),
        {'cursor':cursor,'limit':limit+1}).mappings().all()
    return respond({'items':[dict(row) for row in rows[:limit]],'has_more':len(rows)>limit,
        'next_cursor':rows[limit-1]['id'] if len(rows)>limit else None})


def job(connection, job_id, lock=False):
    row = connection.execute(text('SELECT * FROM research.publish_jobs WHERE job_id=:id' + (' FOR UPDATE' if lock else '')), {'id': job_id}).mappings().first()
    if not row:
        raise ResearchError(404, 'job-not-found', '找不到這份發布作業。')
    return dict(row)


def create_job(connection, request, operation, payload, draft=None, target=None):
    key = request.headers.get('idempotency-key', '')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{7,127}', key):
        raise ResearchError(422, 'invalid-idempotency-key', '請提供 8–128 字元的 Idempotency-Key。')
    # Serialize only the key; a concurrent different key is checked again at activation.
    connection.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,38109072))'), {'key': key})
    identity = {'operation': operation, **payload}
    hashed = digest(identity)
    existing = connection.execute(text('SELECT * FROM research.publish_jobs WHERE idempotency_key=:key'), {'key': key}).mappings().first()
    if existing:
        if existing['payload_hash'] != hashed:
            raise ResearchError(409, 'idempotency-conflict', '相同請求識別已用於不同內容，請勿覆寫原作業。')
        return dict(existing)
    head = active(connection)
    if str(head['release_id']) != payload['base_release_id']:
        raise ResearchError(409, 'publication-base-conflict', '正式研究已有較新版本，草稿已保留，請先整合差異。')
    key_id = uuid.uuid4()
    connection.execute(text('''INSERT INTO research.publish_jobs(job_id,draft_id,draft_revision,operation,
        base_release_id,target_release_id,idempotency_key,payload_hash,status,stage,reason,request_payload)
        VALUES(:id,:draft,:revision,:operation,:base,:target,:key,:hash,'queued','queued',:reason,CAST(:payload AS jsonb))'''),
        {'id': key_id, 'draft': draft['draft_id'] if draft else None, 'revision': draft['revision'] if draft else None,
         'operation': operation, 'base': payload['base_release_id'], 'target': target, 'key': key,
         'hash': hashed, 'reason': payload['reason'], 'payload': canonical(identity)})
    return job(connection, key_id)


@router.post('/drafts/{draft_id}/publish', status_code=202)
async def publish(draft_id: uuid.UUID, request: Request, background: BackgroundTasks,
                  owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    data = await body(request)
    if set(data) != {'base_release_id', 'revision', 'reason'} or type(data['revision']) is not int or not isinstance(data['reason'], str) or not 1 <= len(data['reason'].strip()) <= 2000:
        raise ResearchError(422, 'invalid-publication', '請提供研究基準、整數修訂號與發布理由。')
    current = get_draft(connection, draft_id, data['revision'])
    if str(current['base_release_id']) != data['base_release_id']:
        raise ResearchError(409, 'publication-base-conflict', '發布基準與草稿不一致。')
    payload = {**data, 'draft_id': str(draft_id), 'payload_hash': current['payload_hash']}
    # Check replay before current revision/status; a successful replay must still work.
    key = request.headers.get('idempotency-key', '')
    existing = connection.execute(text('SELECT payload_hash FROM research.publish_jobs WHERE idempotency_key=:key'), {'key': key}).scalar_one_or_none()
    if existing is None:
        if current['revision'] != current['current_revision'] or current['status'] != 'editing':
            raise ResearchError(409, 'draft-conflict', '請先核對最新草稿修訂再發布。')
        await run_in_threadpool(protect_baseline, connection, current, current['payload'])
        # The worker validates again from scratch; this pre-check may reuse the revision's result.
        result, _ = await run_in_threadpool(validated, current)
        if not result['valid']:
            raise ResearchError(422, 'invalid-publication', '草稿尚未通過完整驗證。', errors=result['errors'])
    result = create_job(connection, request, 'publish', payload, current)
    connection.commit()  # Outbox is durable before any Prefect call or 202 response.
    background.add_task(dispatch_job, result['job_id'])
    return respond(result, status=202)


@router.get('/jobs/{job_id}')
def status(job_id: uuid.UUID, owner=Depends(require_owner), connection=Depends(get_admin_connection)):
    return respond(job(connection, job_id))


@router.post('/releases/{release_id}/restore', status_code=202)
async def restore(release_id: uuid.UUID, request: Request, background: BackgroundTasks,
                  owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    data = await body(request)
    if set(data) != {'base_release_id', 'reason'} or not isinstance(data['reason'], str) or not 1 <= len(data['reason'].strip()) <= 2000:
        raise ResearchError(422, 'invalid-restoration', '還原需要目前研究基準與理由。')
    target = base_release(connection, release_id)
    if target['schema_version'] != SCHEMA:
        raise ResearchError(409, 'incompatible-release', '這個研究版本的 Schema 不相容。')
    payload = {**data, 'target_release_id': str(release_id)}
    result = create_job(connection, request, 'restore', payload, target=release_id)
    connection.commit()
    background.add_task(dispatch_job, result['job_id'])
    return respond(result, status=202)


@router.post('/jobs/{job_id}/retry', status_code=202)
def retry(job_id: uuid.UUID, background: BackgroundTasks, owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    current = job(connection, job_id, lock=True)
    if current['status'] == 'failed':
        if not current['failure'].get('retryable'):
            raise ResearchError(409, 'publication-needs-review', '此作業需要整合基準或修正內容，不能直接重試。')
        connection.execute(text("UPDATE research.publish_jobs SET status='queued',available_at=now(),lease_until=NULL,updated_at=now() WHERE job_id=:id"), {'id': job_id})
    result = job(connection, job_id)
    connection.commit()
    background.add_task(dispatch_job, job_id)
    return respond(result, status=202)


async def dispatch_job(job_id, engine=None):
    """Best effort delivery; a missing Prefect never deletes a committed DB job."""
    engine = engine or writer_engine()
    if not os.getenv('PREFECT_API_URL'):
        return False  # Never start an ephemeral orchestration server in an API worker.
    with engine.begin() as connection:
        current = job(connection, job_id, lock=True)
        if current['status'] == 'published':
            return False
        eligible = connection.execute(text('''SELECT (available_at<=now() AND (lease_until IS NULL OR lease_until<now()))
            FROM research.publish_jobs WHERE job_id=:id'''), {'id': job_id}).scalar_one()
        if not eligible or current['status'] == 'failed' and (not (current['failure'] or {}).get('retryable') or current['attempts'] >= 3):
            return False
        dispatch = int(current['checkpoint'].get('dispatch', 0)) + 1
        connection.execute(text('''UPDATE research.publish_jobs SET checkpoint=checkpoint||CAST(:checkpoint AS jsonb),
            lease_until=now()+interval '2 minutes',updated_at=now() WHERE job_id=:id'''),
            {'id': job_id, 'checkpoint': json.dumps({'dispatch': dispatch})})
    try:
        from prefect.client.orchestration import get_client
        async with asyncio.timeout(5):
            async with get_client() as client:
                deployment = await client.read_deployment_by_name('research-publication/publish')
                run = await client.create_flow_run_from_deployment(deployment.id, parameters={'job_id': str(job_id)},
                    idempotency_key=f'research-publication:{job_id}:{dispatch}')
        with engine.begin() as connection:
            connection.execute(text("UPDATE research.publish_jobs SET prefect_run_id=:run,failure=CASE WHEN status='queued' THEN NULL ELSE failure END,updated_at=now() WHERE job_id=:id"), {'id': job_id, 'run': run.id})
        return True
    except Exception:
        # Bounded timeout and durable due time; reconciliation will retry later.
        try:
            with engine.begin() as connection:
                connection.execute(text("UPDATE research.publish_jobs SET failure=CAST(:failure AS jsonb),updated_at=now() WHERE job_id=:id AND status='queued'"),
                    {'id':job_id,'failure':canonical({'code':'publication-queue-unavailable','stage':'dispatch',
                        'message':'Prefect 暫時無法接收，發布作業已保留，等待補送。','retryable':True})})
        except Exception:
            pass  # A DB outage does not make the already committed outbox disappear.
        return False


async def reconcile(engine=None):
    engine = engine or writer_engine()
    with engine.connect() as connection:
        keys = list(connection.execute(text('''SELECT job_id FROM research.publish_jobs
            WHERE status<>'published' AND available_at<=now() AND (lease_until IS NULL OR lease_until<now())
            AND (status<>'failed' OR (failure->>'retryable'='true' AND attempts<3))
            ORDER BY available_at,job_id LIMIT 50''')).scalars())
    return sum([await dispatch_job(key, engine) for key in keys])


def checkpoint(connection, job_id, stage, values=None, target=None):
    connection.execute(text('''UPDATE research.publish_jobs SET stage=:stage,
        checkpoint=checkpoint||CAST(:values AS jsonb),target_release_id=COALESCE(:target,target_release_id),
        updated_at=now(),lease_until=now()+interval '5 minutes' WHERE job_id=:id'''),
        {'id': job_id, 'stage': stage, 'values': canonical(values or {}), 'target': target})


def activate(connection, current, release):
    connection.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': HEAD_LOCK})
    head = active(connection)
    if head['release_id'] != current['base_release_id']:
        raise ResearchError(409, 'publication-base-conflict', '正式研究已有較新版本，請先整合差異。')
    target = base_release(connection, release) if current['operation'] == 'restore' else connection.execute(
        text('SELECT * FROM research.research_releases WHERE release_id=:id'), {'id': release}).mappings().one()
    if target['schema_version'] != SCHEMA or target['status'] not in ('ready', 'published'):
        raise ValueError('候選研究尚未完整備妥。')
    if target['status'] == 'ready':
        connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"), {'id': release})
    changed = head['release_id'] != uuid.UUID(str(release))
    if changed:
        connection.execute(text('UPDATE research.release_head SET release_id=:id,generation=generation+1,activated_at=now() WHERE singleton'), {'id': release})
    generation = head['generation'] + int(changed)
    connection.execute(text("UPDATE research.publish_jobs SET status='published',stage='complete',target_release_id=:release,lease_until=NULL,failure=NULL,updated_at=now() WHERE job_id=:id"), {'id': current['job_id'], 'release': release})
    if current['draft_id']:
        connection.execute(text("UPDATE research.editor_drafts SET status='published' WHERE draft_id=:id AND current_revision=:revision"), {'id': current['draft_id'], 'revision': current['draft_revision']})
    detail = {'base_release_id': str(head['release_id']), 'generation': generation,
        'git_commit': target['git_commit'], 'content_hash': target['content_hash'], 'reason': current['reason'], 'changed': changed}
    connection.execute(text('''INSERT INTO research.audit_log(actor,operation,job_id,release_id,detail)
        VALUES('owner',:operation,:job,:release,CAST(:detail AS jsonb))'''),
        {'operation': current['operation'], 'job': current['job_id'], 'release': release, 'detail': canonical(detail)})
    sync_key = f'sync-ref:{generation}:{release}'
    connection.execute(text('''INSERT INTO research.publish_jobs(job_id,operation,target_release_id,idempotency_key,
        payload_hash,status,stage,reason) VALUES(:id,'sync-ref',:release,:key,:hash,'queued','queued','Synchronize current published index')
        ON CONFLICT(idempotency_key) DO NOTHING'''), {'id': uuid.uuid4(), 'release': release, 'key': sync_key, 'hash': digest(detail)})


def run_job(job_id, engine=None, inject=None):
    engine, managed = engine or writer_engine(), ManagedGit()
    key = str(uuid.UUID(str(job_id)))
    def point(stage):
        if inject:
            inject(stage)
    # Session lock survives intermediate commits and disappears on process death.
    with engine.connect() as guard:
        locked = guard.execute(text('SELECT pg_try_advisory_lock(hashtextextended(:id,38109073))'), {'id': key}).scalar_one()
        guard.commit()
        if not locked:
            return {'busy': True}
        try:
            with engine.begin() as connection:
                current = job(connection, key, lock=True)
                if current['status'] == 'published':
                    return current
                if current['status'] == 'failed' and not (current['failure'] or {}).get('retryable'):
                    return current
                connection.execute(text("UPDATE research.publish_jobs SET status='preparing',attempts=attempts+1,lease_until=now()+interval '5 minutes',updated_at=now() WHERE job_id=:id"), {'id': key})
                if current['operation'] == 'sync-ref':
                    connection.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': HEAD_LOCK})
                    head = base_release(connection, active(connection)['release_id'])
                    managed.verify(head['git_commit'])
                    managed.command('update-ref', 'refs/heads/research/published', head['git_commit'])
                    point('sync-ref')
                    connection.execute(text("UPDATE research.publish_jobs SET status='published',stage='complete',target_release_id=:target,lease_until=NULL,failure=NULL,updated_at=now() WHERE job_id=:id"), {'id': key, 'target': head['release_id']})
                    return job(connection, key)
                if active(connection)['release_id'] != current['base_release_id']:
                    raise ResearchError(409, 'publication-base-conflict', '正式研究已有較新版本，請先整合差異。')
                base = dict(base_release(connection, current['base_release_id']))
                draft = get_draft(connection, current['draft_id'], current['draft_revision']) if current['operation'] == 'publish' else None
            if draft:
                result, bundle = validate_payload(draft['payload'], asset_root())
                if not result['valid']:
                    raise ResearchError(422, 'invalid-publication', '草稿內容或資產尚未通過完整驗證。')
                if draft['payload_hash'] != current['request_payload']['payload_hash']:
                    raise ValueError('草稿內容 hash 不一致。')
                commit = base['git_commit'] if result['content_hash'] == base['content_hash'] else managed.prepare_job(key, base['git_commit'], materialize(draft['payload'], asset_root()))
                release = uuid.uuid5(uuid.NAMESPACE_URL, commit + ':' + SCHEMA + ':' + result['content_hash'])
                managed.protect_release(release, commit)
                with engine.begin() as connection:
                    checkpoint(connection, key, 'git', {'git_commit': commit, 'content_hash': result['content_hash']})
                point('git')
                # Materialization checks every asset hash; project writes referenced CAS metadata.
                materialize(draft['payload'], asset_root())
                with engine.begin() as connection:
                    checkpoint(connection, key, 'assets')
                point('assets')
                with engine.begin() as connection:
                    projected = project(connection, bundle, commit, reason=current['reason'])
                    checkpoint(connection, key, 'projection', target=projected['release_id'])
                    connection.execute(text("UPDATE research.publish_jobs SET status='ready' WHERE job_id=:id"), {'id': key})
                point('projection')
            else:
                with engine.connect() as connection:
                    target = dict(base_release(connection, current['target_release_id']))
                commit, release = target['git_commit'], target['release_id']
                bundle = compile_archive(make_archive(managed.files(commit)))
                if digest(bundle) != target['content_hash']:
                    raise ValueError('還原版本內容 hash 不符。')
                managed.protect_release(release, commit)
            point('before-activation')
            # Verify prepared content immediately before the activation transaction.
            restored = compile_archive(make_archive(managed.files(commit)))
            if digest(restored) != digest(bundle):
                raise ValueError('候選 Git 內容不一致。')
            for asset in bundle['assets'].values():
                from hashlib import sha256
                path = asset_root() / asset['sha256']
                if path.is_symlink() or not path.is_file() or sha256(path.read_bytes()).hexdigest() != asset['sha256']:
                    raise ValueError('候選資產尚未完整備妥。')
            with engine.begin() as connection:
                project(connection, bundle, commit, reason=current['reason'])
                activate(connection, current, release)
                point('activation-transaction')
            point('after-activation')
            with engine.connect() as connection:
                return job(connection, key)
        except Exception as error:
            with engine.begin() as connection:
                current = job(connection, key, lock=True)
                if current['status'] != 'published':
                    retryable = not isinstance(error, ResearchError)
                    failure = {'code': getattr(error, 'code', 'publication-interrupted'), 'stage': current['stage'],
                        'message': '發布未完成；正式研究保留原版本。' if retryable else error.message, 'retryable': retryable}
                    connection.execute(text("""UPDATE research.publish_jobs SET status='failed',failure=CAST(:failure AS jsonb),
                        lease_until=NULL,available_at=now()+interval '30 seconds',updated_at=now() WHERE job_id=:id"""), {'id': key, 'failure': canonical(failure)})
            raise
        finally:
            guard.execute(text('SELECT pg_advisory_unlock(hashtextextended(:id,38109073))'), {'id': key})
            guard.commit()
