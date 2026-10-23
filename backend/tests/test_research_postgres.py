"""Actual PostgreSQL contracts; requires an explicit disposable database."""
import os
import uuid
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError


def execute(conn, statement, **params):
    return conn.execute(text(statement), params)


def rejected(conn, statement, code, **params):
    with pytest.raises(DBAPIError) as caught:
        with conn.begin_nested():
            execute(conn, statement, **params)
    assert caught.value.orig.sqlstate == code


@pytest.fixture(scope='module')
def pg():
    url = os.environ.get('RESEARCH_PG_TEST_URL')
    if not url:
        pytest.skip('explicit disposable research PostgreSQL environment required')
    admin = create_engine(url, hide_parameters=True)
    if admin.url.database != 'industry_research_test':
        raise RuntimeError('Refusing fixtures outside industry_research_test')
    reader = create_engine(os.environ['RESEARCH_PG_READER_URL'], hide_parameters=True)
    writer = create_engine(os.environ['RESEARCH_PG_WRITER_URL'], hide_parameters=True)
    token = uuid.uuid4().hex
    data = {'a': str(uuid.uuid4()), 'b': str(uuid.uuid4()),
            'company': 'company-test-' + token, 'private': 'company-private-' + token,
            'revision': token * 2}
    with admin.begin() as c:
        for release in ('a', 'b'):
            execute(c, "INSERT INTO research.research_releases VALUES (CAST(:id AS uuid),:commit,'research-v1',:hash,'ready',now(),NULL,'isolated test')",
                    id=data[release], commit=(uuid.uuid4().hex + '00000000'), hash=uuid.uuid4().hex * 2)
        for entity, release in [('company', 'a'), ('private', 'b')]:
            execute(c, "INSERT INTO research.entities VALUES (:id,'company')", id=data[entity])
            execute(c, "INSERT INTO research.entity_snapshots VALUES (CAST(:r AS uuid),:id,'company','test','test','test','{}',:hash,NULL)",
                    r=data[release], id=data[entity], hash=token * 2)
        execute(c, "INSERT INTO research.documents VALUES (:id)", id='document-' + token)
        execute(c, "INSERT INTO research.document_revisions VALUES (:rev,:doc,'v1','test','https://example.org','informative','{}')", rev=data['revision'], doc='document-' + token)
        execute(c, "INSERT INTO research.release_documents VALUES (CAST(:r AS uuid),:rev)", r=data['b'], rev=data['revision'])
    yield admin, reader, writer, data
    for engine in (admin, reader, writer):
        engine.dispose()


def test_composite_fk_rejects_cross_release_endpoints(pg):
    admin, _, _, d = pg
    with admin.begin() as c:
        rejected(c, "INSERT INTO research.taxonomy_links VALUES (CAST(:r AS uuid),'taxonomy-test',:a,:b)", '23503',
                 r=d['a'], a=d['company'], b=d['private'])
        rejected(c, "INSERT INTO research.relations VALUES (CAST(:r AS uuid),'relation-test',:a,:b,'partnership','directed','test','[]','inference',NULL,NULL,NULL,'{}')", '23503',
                 r=d['a'], a=d['company'], b=d['private'])
        rejected(c, "INSERT INTO research.research_claims VALUES (CAST(:r AS uuid),:id,'test','test','inference','[]','2026-10-16')", '23503',
                 r=d['a'], id=d['private'])
        execute(c, "INSERT INTO research.research_claims VALUES (CAST(:r AS uuid),:id,'test','test','inference','[]','2026-10-16')", r=d['a'], id=d['company'])
        rejected(c, "INSERT INTO research.claim_evidence VALUES (CAST(:r AS uuid),:id,'test',0,:rev,'section','supporting','test','{}')", '23503',
                 r=d['a'], id=d['company'], rev=d['revision'])


def test_ready_release_cannot_become_head(pg):
    admin, _, _, d = pg
    with admin.begin() as c:
        with pytest.raises(DBAPIError) as caught:
            with c.begin_nested():
                execute(c, 'INSERT INTO research.release_head VALUES (true,CAST(:id AS uuid),1,now()) ON CONFLICT (singleton) DO UPDATE SET release_id=excluded.release_id', id=d['b'])
                execute(c, 'SET CONSTRAINTS ALL IMMEDIATE')
        assert caught.value.orig.sqlstate == '23514'


def test_reader_hides_unpublished_data_and_has_no_admin_grants(pg):
    admin, reader, _, d = pg
    with admin.begin() as c:
        execute(c, "UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=CAST(:id AS uuid) AND status<>'published'", id=d['a'])
    with reader.connect() as c:
        assert execute(c, 'SHOW default_transaction_read_only').scalar_one() == 'on'
        assert execute(c, 'SELECT count(*) FROM research.entity_snapshots WHERE entity_id=:id', id=d['company']).scalar_one() == 1
        assert execute(c, 'SELECT count(*) FROM research.entity_snapshots WHERE entity_id=:id', id=d['private']).scalar_one() == 0
        assert execute(c, 'SELECT count(*) FROM research.entities WHERE entity_id=:id', id=d['private']).scalar_one() == 0
        assert execute(c, 'SELECT count(*) FROM research.document_revisions WHERE revision_id=:id', id=d['revision']).scalar_one() == 0
        assert execute(c, 'SELECT rolsuper OR rolbypassrls OR rolcreatedb OR rolcreaterole FROM pg_roles WHERE rolname=current_user').scalar_one() is False
    for table in ('editor_drafts','draft_revisions','publish_jobs','audit_log','admin_owner','admin_sessions','login_attempts'):
        with reader.begin() as c:
            rejected(c, 'SELECT * FROM research.' + table, '42501')
    with reader.connect().execution_options(isolation_level='AUTOCOMMIT') as c:
        execute(c, 'SET default_transaction_read_only=off')
        with pytest.raises(DBAPIError) as caught:
            execute(c, "INSERT INTO research.entities VALUES ('company-forbidden','company')")
        assert caught.value.orig.sqlstate == '42501'
        execute(c, 'SET default_transaction_read_only=on')


def test_writer_cannot_change_published_snapshot_or_create_tables(pg):
    admin, _, writer, d = pg
    with admin.begin() as c:
        execute(c, "UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=CAST(:id AS uuid) AND status<>'published'", id=d['a'])
    with writer.begin() as c:
        rejected(c, "UPDATE research.entity_snapshots SET summary='changed' WHERE entity_id=:id", '23514', id=d['company'])
        rejected(c, "UPDATE research.research_releases SET status='ready' WHERE release_id=CAST(:id AS uuid)", '23514', id=d['a'])
        rejected(c, 'CREATE TABLE research.forbidden (id integer)', '42501')


def test_publish_job_idempotency_constraint(pg):
    admin, _, _, _ = pg
    with admin.begin() as c:
        job = "INSERT INTO research.publish_jobs (job_id,operation,idempotency_key,payload_hash,status,stage,reason) VALUES (CAST(:id AS uuid),'restore',:key,'hash','queued','queued','isolated test')"
        key = 'check-' + str(uuid.uuid4())
        execute(c, job, id=str(uuid.uuid4()), key=key)
        rejected(c, job, '23505', id=str(uuid.uuid4()), key=key)


def test_company_financial_store_is_gone_and_reader_still_reads_research(pg):
    admin, reader, _, d = pg
    with admin.begin() as c:
        execute(c, "UPDATE research.research_releases SET status='published',published_at=now() WHERE release_id=CAST(:id AS uuid) AND status<>'published'", id=d['a'])
        # Migration 0017 drops every company financial object; the shared immutability guard stays.
        assert execute(c, "SELECT count(*) FROM pg_class WHERE relnamespace='research'::regnamespace AND relname LIKE 'financial%'").scalar_one() == 0
        assert execute(c, "SELECT to_regclass('research.observation_provenance')").scalar_one() is None
        assert execute(c, "SELECT to_regprocedure('research.guard_financial_import()')").scalar_one() is None
        assert execute(c, "SELECT to_regprocedure('research.guard_immutable_row()')").scalar_one() is not None
        assert execute(c, "SELECT to_regclass('public.financials')").scalar_one() is not None
    with reader.connect() as c:
        assert execute(c, 'SELECT count(*) FROM research.entity_snapshots WHERE entity_id=:id', id=d['company']).scalar_one() == 1
        assert execute(c, 'SELECT count(*) FROM research.event_entity_links').scalar_one() >= 0
