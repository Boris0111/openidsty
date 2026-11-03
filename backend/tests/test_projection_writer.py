"""Batched projection writes exactly what row-by-row writing wrote (design D1, D2, D5).

The writer's ordering rules are checked offline; the equivalence, legacy-history and failure cases need the
explicit disposable PostgreSQL (research_pg_checks.py) and run in one transaction that is always rolled back.
"""
from datetime import date
from decimal import Decimal
import os
import uuid
import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from app.config import ROOT
from app.research_compile import (BATCH_ROWS, PROJECTION_ORDER, SCHEMA, ProjectionWriter, clean, compile_archive,
                                  digest, project, projection_tables)
from app.research_documents import validate_payload
from app.research_git import make_archive
from test_research_documents import authored

SHARED = {'entities', 'documents', 'document_revisions', 'assets'}  # tables without release_id
LEGACY_KINDS = {'assessment', 'indicator-definition', 'indicator-observation', 'technical-document',
                'technical-observation', 'technical-review'}


class Recorder:
    """A connection stand-in that records what the writer sends."""

    def __init__(self):
        self.calls = []

    def execute(self, statement, parameters=None):
        self.calls.append((str(statement), parameters))


def test_writer_sends_tables_in_foreign_key_order_and_keeps_row_order():
    recorder = Recorder()
    writer = ProjectionWriter(recorder)
    release = uuid.uuid4()
    rows = BATCH_ROWS * 2 + 500
    for index in range(rows):
        writer.insert('relations', {'release_id': release, 'relation_id': f'r{index:05d}', 'data': {'n': index}})
    writer.insert('taxonomy_links', {'release_id': release, 'link_id': 'authored', 'parent_id': 'a', 'child_id': 'b'})
    writer.insert('taxonomy_links', {'release_id': release, 'link_id': 'baseline', 'parent_id': 'a', 'child_id': 'b'}, True)
    writer.insert('entities', {'entity_id': 'company-a', 'kind': 'company'}, True)
    writer.insert('research_releases', {'release_id': release, 'status': 'preparing'})
    assert recorder.calls == []  # nothing is sent before flush
    writer.flush()
    tables = [sql.split('INSERT INTO research.')[1].split(' ')[0] for sql, _ in recorder.calls]
    assert tables == ['research_releases', 'entities', 'taxonomy_links', 'taxonomy_links', 'relations', 'relations', 'relations']
    assert [len(batch) for sql, batch in recorder.calls if 'relations' in sql] == [BATCH_ROWS, BATCH_ROWS, 500]
    sent = [row['relation_id'] for sql, batch in recorder.calls if 'research.relations' in sql for row in batch]
    assert sent == [f'r{index:05d}' for index in range(rows)]
    links = [(sql.endswith('ON CONFLICT DO NOTHING'), batch[0]['link_id']) for sql, batch in recorder.calls if 'taxonomy_links' in sql]
    assert links == [(False, 'authored'), (True, 'baseline')]  # authored links first, as before batching
    assert all(row['data'] == '{"n":%d}' % index for index, row in enumerate(
        row for sql, batch in recorder.calls if 'research.relations' in sql for row in batch))
    writer.flush()
    assert len(recorder.calls) == 7  # flushed rows are not sent twice


def test_immediate_writer_sends_each_row_when_added():
    recorder = Recorder()
    writer = ProjectionWriter(recorder, immediate=True)
    writer.insert('entities', {'entity_id': 'company-a', 'kind': 'company'}, True)
    assert len(recorder.calls) == 1 and isinstance(recorder.calls[0][1], dict)
    writer.flush()
    assert len(recorder.calls) == 1


def test_writer_refuses_tables_outside_the_order():
    for immediate in (False, True):
        recorder = Recorder()
        with pytest.raises(ValueError, match='PROJECTION_ORDER: release_head'):
            ProjectionWriter(recorder, immediate).insert('release_head', {'singleton': True})
        assert recorder.calls == []
    assert PROJECTION_ORDER[0] == 'research_releases' and PROJECTION_ORDER[-1] == 'legacy_history'


@pytest.fixture(scope='module')
def admin():
    url = os.environ.get('RESEARCH_PG_TEST_URL')
    if not url:
        pytest.skip('explicit disposable research PostgreSQL environment required')
    engine = create_engine(url, hide_parameters=True)
    if engine.url.database != 'industry_research_test':
        raise RuntimeError('Refusing projection checks outside industry_research_test')
    yield engine
    engine.dispose()


@pytest.fixture
def connection(admin, tmp_path, monkeypatch):
    """One transaction per test, always rolled back; nothing written here outlives the test."""
    monkeypatch.setenv('RESEARCH_ASSET_ROOT', str(tmp_path / 'assets'))
    with admin.connect() as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


@pytest.fixture(scope='module')
def published(authored):
    """The research authored at HEAD, compiled the way a draft revision is."""
    payload, assets = authored
    result, bundle = validate_payload(payload, assets)
    assert result['valid'], result['errors'][:5]
    return bundle


def fixture_bundle():
    folder = ROOT / 'tests/fixtures/valid'
    # The API image ships no root tests/ folder, so research_drill.py pg-check skips this; CI runs it from the checkout.
    if not folder.is_dir():
        pytest.skip('tests/fixtures/valid is not in the API image; CI runs this test from the checkout')
    return compile_archive(make_archive({'industry-map/' + path.relative_to(folder).as_posix(): path.read_bytes()
                                         for path in folder.rglob('*') if path.is_file()}))


def synthetic_commit():
    return uuid.uuid4().hex + '00000000'  # never a real commit, so the release is always new


def both_ways(connection, bundle):
    """Project one bundle row by row and batched, each in its own savepoint; the tables must match."""
    commit, outcomes = synthetic_commit(), []
    for immediate in (True, False):
        with connection.begin_nested() as savepoint:
            projected = project(connection, bundle, commit, reason='Writer equivalence check', immediate=immediate)
            outcomes.append({'release_id': projected['release_id'], 'content_hash': projected['content_hash'],
                             'tables': projection_tables(connection, projected['release_id'])})
            savepoint.rollback()
    assert outcomes[0] == outcomes[1]
    return outcomes[1]


def seed_legacy(connection):
    """Legacy lineage of all six kinds in the rolled-back test transaction: the importer's themes, sources and
    technical documents, plus one synthetic indicator, observation, technical observation and review."""
    from sqlalchemy.orm import Session
    from app.import_map import import_map
    from app.models import (Indicator, IndicatorObservation, TechnicalDocument, TechnicalObservation,
                            TechnicalReview, ThemeAssessmentVersion, ThemeIndicator)
    for table in ('technical_reviews', 'technical_observations', 'technical_documents', 'indicator_observations',
                  'theme_indicators', 'indicators', 'theme_assessment_versions'):
        if connection.execute(text('SELECT count(*) FROM public.' + table)).scalar_one():
            raise RuntimeError('Expected empty legacy tables in the research test DB')
    session = Session(bind=connection, expire_on_commit=False, join_transaction_mode='create_savepoint')
    import_map(session)
    source = connection.execute(text('SELECT id FROM public.sources ORDER BY id LIMIT 1')).scalar_one()
    if not connection.execute(text('SELECT count(*) FROM public.theme_assessment_versions')).scalar_one():
        session.add(ThemeAssessmentVersion(theme_id='liquid-cooling', version_number=1, payload={'synthetic': True},
                                           content_hash='0' * 64, reviewed='2026-11-02', reason='合成舊歷史'))
    session.add(Indicator(id='synthetic-legacy-indicator', name='合成指標', kind='proxy', unit='%', frequency='monthly',
                          basis='reported', data={'synthetic': True}))
    session.flush()
    session.add_all([ThemeIndicator(theme_id='liquid-cooling', indicator_id='synthetic-legacy-indicator'),
                     ThemeIndicator(theme_id='hbm4', indicator_id='synthetic-legacy-indicator')])
    session.add(IndicatorObservation(indicator_id='synthetic-legacy-indicator', source_id=source, identity='1' * 64,
        document_identity='synthetic', dataset='synthetic', entity='synthetic', original_period='2026-10',
        period_start=date(2026, 10, 1), period_end=date(2026, 10, 31), basis='reported', scope='合成範圍', unit='%',
        value=Decimal('12.34500000'), url='https://example.org/indicator', raw_excerpt='合成摘錄', raw={'value': '12.345'},
        revision=1, content_hash='2' * 64))
    session.add(TechnicalDocument(id='synthetic-legacy-document', source_id=source, title='合成技術文件', doc_kind='standard',
                                  data={'segments': ['thermal'], 'themes': ['liquid-cooling']}))
    session.flush()
    observation = TechnicalObservation(document_id='synthetic-legacy-document', observation_key='k1', content_hash='3' * 64,
                                       parser_version='synthetic', url='https://example.org/document', data={'synthetic': True})
    session.add(observation)
    session.flush()
    session.add(TechnicalReview(observation_id=observation.id, status='confirmed', reviewed='2026-11-02', reason='合成審查'))
    session.commit()
    session.close()


def reference_rows(connection, mappings):
    """legacy_history rows by the rules before batching, one lookup query per row (the oracle for D2)."""
    rows = []
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
                rows.append((entity, kind, entity + ':' + str(row['id']), digest(payload), payload))
    return sorted(rows, key=lambda row: row[:3])


def test_fixture_map_projects_identically(connection):
    result = both_ways(connection, fixture_bundle())
    assert result['tables']['entity_snapshots']['rows'] == 5 and result['tables']['release_sources']['rows'] == 2


def test_published_research_with_every_legacy_kind_projects_identically(connection, published):
    seed_legacy(connection)
    result = both_ways(connection, published)
    tables = result['tables']
    assert tables['entity_snapshots']['rows'] == len(published['snapshots'])
    for table in ('relations', 'taxonomy_links', 'research_claims', 'claim_evidence', 'release_assets', 'legacy_history'):
        assert tables[table]['rows'] > 0, table


def test_legacy_history_reads_lookups_once_and_keeps_every_row(connection, published):
    seed_legacy(connection)
    mappings = {snapshot['entity_id'] for snapshot in published['snapshots']}
    expected = reference_rows(connection, mappings)
    assert {row[1] for row in expected} == LEGACY_KINDS
    statements = []
    listener = lambda conn, cursor, statement, *args: statements.append(statement)
    for immediate in (True, False):
        statements.clear()
        event.listen(connection, 'before_cursor_execute', listener)
        try:
            with connection.begin_nested() as savepoint:
                projected = project(connection, published, synthetic_commit(), immediate=immediate)
                actual = connection.execute(text('SELECT entity_id,history_kind,legacy_id,content_hash,data FROM research.legacy_history '
                                                 'WHERE release_id=CAST(:id AS uuid)'), {'id': projected['release_id']}).all()
                savepoint.rollback()
        finally:
            event.remove(connection, 'before_cursor_execute', listener)
        assert sorted((tuple(row) for row in actual), key=lambda row: row[:3]) == expected
        # Three lookup tables read once each, plus the six history tables: not one query per history row.
        assert sum('FROM public.' in statement for statement in statements) == 9


def test_missing_entity_message_is_unchanged(connection, published):
    from sqlalchemy.orm import Session
    from app.models import Theme, ThemeAssessmentVersion
    seed_legacy(connection)
    # A retired theme that still has assessment history but no snapshot in the research.
    session = Session(bind=connection, join_transaction_mode='create_savepoint')
    session.add(Theme(id='legacy-only-theme', data={}, prose='', active=False))
    session.flush()
    session.add(ThemeAssessmentVersion(theme_id='legacy-only-theme', version_number=1, payload={'synthetic': True},
                                       content_hash='4' * 64, reviewed='2026-11-03', reason='已退場的合成題材'))
    session.commit()
    session.close()
    bundle = published
    with pytest.raises(ValueError) as before:
        reference_rows(connection, {snapshot['entity_id'] for snapshot in bundle['snapshots']})
    assert str(before.value) == 'Legacy history references missing entity theme-legacy-only-theme'
    for immediate in (True, False):
        with pytest.raises(ValueError) as after:
            with connection.begin_nested():
                project(connection, bundle, synthetic_commit(), immediate=immediate)
        assert str(after.value) == str(before.value)


def test_a_failing_batch_rolls_back_the_whole_projection(connection, published):
    broken = {**published, 'relations': published['relations'] + [published['relations'][0]]}  # duplicate relation ID
    commit = synthetic_commit()
    release = uuid.uuid5(uuid.NAMESPACE_URL, commit + ':' + SCHEMA + ':' + digest(broken))
    before = projection_tables(connection, release)
    for immediate in (False, True):
        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                project(connection, broken, commit, immediate=immediate)
        after = projection_tables(connection, release)
        assert after == before  # shared tables unchanged, and not one row of this release
        assert all(value['rows'] == 0 for table, value in after.items() if table not in SHARED)
        assert connection.execute(text('SELECT count(*) FROM research.research_releases WHERE release_id=:id'), {'id': release}).scalar_one() == 0


@pytest.mark.slow
def test_scaled_research_projects_identically(connection, scaled_tree):
    files = {path.relative_to(scaled_tree).as_posix(): path.read_bytes() for path in scaled_tree.rglob('*') if path.is_file()}
    bundle = compile_archive(make_archive(files))
    seed_legacy(connection)
    result = both_ways(connection, bundle)
    assert result['tables']['relations']['rows'] >= 3000 and result['tables']['legacy_history']['rows'] > 0
