"""Crash checkpoints and replay against disposable PostgreSQL and managed Git."""
import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
import uuid
import re
import pytest
from sqlalchemy import text
from app import research_publication as publication
from app.research_git import ManagedGit, make_archive
from app.research_compile import compile_archive, project
from test_research_auth import owner
from test_research_documents import authored
from test_research_drafts import draft_context
deliver = publication.dispatch_job


@pytest.fixture
def publishing(draft_context, monkeypatch):
    client, engine, release, headers = draft_context
    monkeypatch.setattr(publication, 'writer_engine', lambda: engine)
    async def offline(*args, **kwargs):
        return False
    monkeypatch.setattr(publication, 'dispatch_job', offline)
    # Head replacement is confined to the explicit disposable DB.
    with engine.begin() as connection:
        connection.execute(text('INSERT INTO research.release_head VALUES(true,:release,1,now()) ON CONFLICT(singleton) DO UPDATE SET release_id=excluded.release_id'), {'release': release})
    draft = client.post('/api/admin/drafts', json={'base_release_id': release}, headers=headers).json()
    url = '/api/admin/drafts/' + draft['draft_id']
    path = 'industry-map/companies/company-auras.md'
    parts = client.get(url+'/document', params={'path': path}).json()
    parts['frontmatter']['summary'] = '合成發布測試 ' + uuid.uuid4().hex
    response = client.patch(url, json={'changes': [{'path': path, 'frontmatter': parts['frontmatter'], 'markdown': parts['markdown']}]}, headers={**headers, 'If-Match': '"1"'})
    assert response.status_code == 200
    payload = {'base_release_id': release, 'revision': 2, 'reason': 'Synthetic publication interruption test'}
    headers = {**headers, 'Idempotency-Key': uuid.uuid4().hex}
    response = client.post(url+'/publish', json=payload, headers=headers)
    assert response.status_code == 202, response.text
    return client, engine, release, headers, url, payload, response.json()['job_id']


@pytest.mark.parametrize('stage', ['git', 'assets', 'projection', 'before-activation', 'activation-transaction', 'after-activation'])
def test_failure_keeps_old_head_and_resumes_without_duplicate_release(publishing, stage):
    client, engine, base, headers, url, payload, key = publishing
    def interrupt(current):
        if current == stage:
            raise RuntimeError('Synthetic process interruption')
    with pytest.raises(RuntimeError):
        publication.run_job(key, engine, inject=interrupt)
    with engine.connect() as connection:
        head = str(connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one())
        state = publication.job(connection, key)
        assert (state['status'] == 'published') == (stage == 'after-activation')
        if stage != 'after-activation':
            assert head == base
        refs_before = ManagedGit().command('for-each-ref', '--format=%(objectname)', 'refs/research/jobs/'+key)
    result = publication.run_job(key, engine)
    assert result['status'] == 'published'
    target = str(result['target_release_id'])
    with engine.connect() as connection:
        assert str(connection.execute(text('SELECT release_id FROM research.release_head')).scalar_one()) == target != base
        assert connection.execute(text("SELECT count(*) FROM research.audit_log WHERE job_id=:id AND operation='publish'"), {'id': key}).scalar_one() == 1
        assert connection.execute(text('SELECT count(*) FROM research.research_releases WHERE release_id=:target'), {'target': target}).scalar_one() == 1
    assert ManagedGit().command('for-each-ref', '--format=%(objectname)', 'refs/research/jobs/'+key) == refs_before
    replay = client.post(url+'/publish', json=payload, headers=headers)
    assert replay.status_code == 202 and replay.json()['job_id'] == key
    conflict = client.post(url+'/publish', json={**payload, 'reason':'Different request'}, headers=headers)
    assert conflict.status_code == 409
    assert client.get('/api/admin/jobs/'+key).json()['status'] == 'published'


def test_outbox_survives_orchestrator_absence_and_duplicate_workers_are_locked(publishing):
    client, engine, _, _, _, _, key = publishing
    # The HTTP background delivery was deliberately offline, but the committed job remains.
    with engine.connect() as guard:
        assert publication.job(guard, key)['status'] == 'queued'
        guard.execute(text('SELECT pg_advisory_lock(hashtextextended(:id,38109073))'), {'id':key})
        guard.commit()
        try:
            assert publication.run_job(key, engine) == {'busy':True}
        finally:
            guard.execute(text('SELECT pg_advisory_unlock(hashtextextended(:id,38109073))'), {'id':key})
            guard.commit()
    assert publication.run_job(key, engine)['status'] == 'published'


def test_late_base_conflict_does_not_overwrite_another_publication(publishing):
    client, engine, base, headers, url, payload, key = publishing
    def change_base(stage):
        if stage == 'before-activation':
            # Simulate another valid head activation without touching the draft.
            with engine.begin() as connection:
                base_row = publication.base_release(connection, base)
                managed = ManagedGit()
                files = managed.files(base_row['git_commit'])
                path = 'industry-map/companies/company-auras.md'
                files[path] = re.sub(br'^summary:.*$', b'summary: Synthetic competing publication', files[path], flags=re.M)
                commit = managed.prepare_job(uuid.uuid4(), base_row['git_commit'], files)
                other = project(connection, compile_archive(make_archive(files)), commit, reason='Synthetic competing publication')
                managed.protect_release(other['release_id'], commit)
                connection.execute(text("UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=:id"), {'id':other['release_id']})
                connection.execute(text('UPDATE research.release_head SET release_id=:id,generation=generation+1'), {'id':other['release_id']})
    with pytest.raises(publication.ResearchError) as error:
        publication.run_job(key, engine, inject=change_base)
    assert error.value.code == 'publication-base-conflict'
    state = client.get('/api/admin/jobs/'+key).json()
    assert state['status']=='failed' and state['failure']['retryable'] is False
    assert client.post('/api/admin/jobs/'+key+'/retry', headers=headers).status_code == 409
    comparison = client.get(url+'/diff?against=active')
    assert comparison.status_code == 200
    assert comparison.json()['compared_release_id'] != base
    assert comparison.json()['draft_base_release_id'] == base


def test_abrupt_worker_exit_is_reconciled_after_lease_expiry(publishing, monkeypatch):
    _, engine, _, _, _, _, key = publishing
    class Crash(BaseException):
        pass
    def crash(stage):
        if stage == 'projection':
            raise Crash()
    with pytest.raises(Crash):
        publication.run_job(key, engine, inject=crash)
    with engine.begin() as connection:
        assert publication.job(connection, key)['status'] == 'ready'
        connection.execute(text("UPDATE research.publish_jobs SET lease_until=now()+interval '1 day' WHERE job_id<>:id AND status<>'published'"), {'id':key})
        connection.execute(text("UPDATE research.publish_jobs SET lease_until=now()-interval '1 second' WHERE job_id=:id"), {'id':key})
    sent = []
    async def enqueue(job_id, _):
        sent.append(str(job_id))
        return True
    monkeypatch.setattr(publication, 'dispatch_job', enqueue)
    assert asyncio.run(publication.reconcile(engine)) >= 1
    assert key in sent
    assert publication.run_job(key, engine)['status'] == 'published'


def test_restore_preserves_dynamic_history_and_late_ref_sync_uses_current_head(publishing):
    client, engine, base, headers, _, _, key = publishing
    published = publication.run_job(key, engine)
    target = str(published['target_release_id'])
    with engine.connect() as connection:
        events = connection.execute(text('SELECT count(*) FROM public.events')).scalar_one()
        indicators = connection.execute(text('SELECT count(*) FROM public.indicator_observations')).scalar_one()
        late_sync = connection.execute(text("SELECT job_id FROM research.publish_jobs WHERE operation='sync-ref' AND target_release_id=:target ORDER BY created_at DESC LIMIT 1"), {'target':target}).scalar_one()
    restore_headers = {**headers, 'Idempotency-Key': uuid.uuid4().hex}
    payload = {'base_release_id':target, 'reason':'Synthetic return to known complete research'}
    restored = client.post('/api/admin/releases/'+base+'/restore', json=payload, headers=restore_headers)
    assert restored.status_code == 202, restored.text
    restore_key = restored.json()['job_id']
    assert publication.run_job(restore_key, engine)['status'] == 'published'
    assert client.post('/api/admin/releases/'+base+'/restore', json=payload, headers=restore_headers).json()['job_id'] == restore_key
    publication.run_job(late_sync, engine)
    with engine.connect() as connection:
        assert str(publication.active(connection)['release_id']) == base
        original = publication.base_release(connection, base)
        assert connection.execute(text('SELECT count(*) FROM public.events')).scalar_one() == events
        assert connection.execute(text('SELECT count(*) FROM public.indicator_observations')).scalar_one() == indicators
        assert publication.job(connection, late_sync)['target_release_id'] == original['release_id']
    assert ManagedGit().command('rev-parse', 'refs/heads/research/published').decode().strip() == original['git_commit']


def test_prefect_delivery_failure_stays_durable_then_reconciliation_can_submit(publishing, monkeypatch):
    _, engine, _, _, _, _, key = publishing
    import prefect.client.orchestration
    monkeypatch.setenv('PREFECT_API_URL', 'http://orchestrator.invalid/api')
    sent, fail = [], [True]
    class FakeClient:
        async def read_deployment_by_name(self, name):
            assert name == 'research-publication/publish'
            if fail[0]:
                raise OSError('Synthetic orchestrator outage')
            return SimpleNamespace(id=uuid.uuid4())
        async def create_flow_run_from_deployment(self, deployment, **kwargs):
            sent.append(kwargs)
            return SimpleNamespace(id=uuid.uuid4())
    @asynccontextmanager
    async def get_client():
        yield FakeClient()
    monkeypatch.setattr(prefect.client.orchestration, 'get_client', get_client)
    assert asyncio.run(deliver(key, engine)) is False
    with engine.begin() as connection:
        assert publication.job(connection, key)['status'] == 'queued'
        connection.execute(text("UPDATE research.publish_jobs SET lease_until=now()-interval '1 second' WHERE job_id=:id"), {'id':key})
    fail[0] = False
    assert asyncio.run(deliver(key, engine)) is True
    assert sent[0]['parameters'] == {'job_id':key}
    assert sent[0]['idempotency_key'].startswith('research-publication:'+key+':')
    with engine.connect() as connection:
        assert publication.job(connection, key)['prefect_run_id'] is not None


def test_semantically_identical_publication_does_not_create_fake_version(publishing):
    client, engine, base, headers, _, _, _ = publishing
    draft = client.post('/api/admin/drafts', json={'base_release_id':base}, headers=headers).json()
    payload = {'base_release_id':base, 'revision':1, 'reason':'Synthetic unchanged-content publication'}
    with engine.connect() as connection:
        before = connection.execute(text('SELECT count(*) FROM research.research_releases')).scalar_one()
        generation = publication.active(connection)['generation']
    result = client.post('/api/admin/drafts/'+draft['draft_id']+'/publish', json=payload,
        headers={**headers, 'Idempotency-Key':uuid.uuid4().hex})
    assert result.status_code == 202
    published = publication.run_job(result.json()['job_id'], engine)
    assert str(published['target_release_id']) == base
    with engine.connect() as connection:
        assert connection.execute(text('SELECT count(*) FROM research.research_releases')).scalar_one() == before
        assert publication.active(connection)['generation'] == generation


@pytest.mark.parametrize('operation', ['git', 'asset', 'projection'])
def test_storage_and_projection_failures_preserve_old_reader_and_retry(publishing, monkeypatch, operation):
    _, engine, base, _, _, _, key = publishing
    with engine.connect() as connection:
        count_before = connection.execute(text('SELECT count(*) FROM research.research_releases')).scalar_one()
    with monkeypatch.context() as patch:
        if operation == 'git':
            def fail_git(*args, **kwargs):
                raise OSError('Synthetic Git storage failure')
            patch.setattr(ManagedGit, 'prepare_job', fail_git)
        elif operation == 'asset':
            original, calls = publication.materialize, [0]
            def fail_asset(*args, **kwargs):
                calls[0] += 1
                if calls[0] == 2:
                    raise OSError('Synthetic asset storage interruption after Git')
                return original(*args, **kwargs)
            patch.setattr(publication, 'materialize', fail_asset)
        else:
            original = publication.project
            def fail_projection(*args, **kwargs):
                original(*args, **kwargs)
                raise OSError('Synthetic projection transaction interruption')
            patch.setattr(publication, 'project', fail_projection)
        with pytest.raises(OSError):
            publication.run_job(key, engine)
    with engine.connect() as connection:
        assert str(publication.active(connection)['release_id']) == base
        assert publication.job(connection, key)['status'] == 'failed'
        assert connection.execute(text('SELECT count(*) FROM research.research_releases')).scalar_one() == count_before
    assert publication.run_job(key, engine)['status'] == 'published'
