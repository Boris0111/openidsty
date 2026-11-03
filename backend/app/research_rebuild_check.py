"""Verify Git reconstruction and preserved legacy lineage in the test DB only."""
import argparse
import json
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from .config import DATABASE_URL
from .research_compile import compile_archive, digest, project, projection_tables


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    url = make_url(DATABASE_URL)
    if url.database != 'industry_research' or url.username != 'industry' or url.host != 'db':
        raise RuntimeError('Only the isolated research initializer may run this check')
    archive = sys.stdin.buffer.read(100 * 1024 * 1024 + 1)
    bundle = compile_archive(archive)
    assert bundle == compile_archive(archive)
    # The application DB is read-only here: copy lineage into the explicit test DB.
    source = create_engine(url, hide_parameters=True)
    target = create_engine(url.set(database='industry_research_test'), hide_parameters=True)
    from .research_compile import canonical
    history_tables = ('theme_assessment_versions', 'indicators', 'indicator_observations',
                      'theme_indicators', 'technical_documents', 'technical_observations', 'technical_reviews')
    with source.connect() as connection:
        lineage = {table: [dict(row) for row in connection.execute(text('SELECT * FROM public.' + table)).mappings()] for table in history_tables}
        sources = [dict(row) for row in connection.execute(text('SELECT * FROM public.sources')).mappings()]
    # Preserve public test DB data by using an uncommitted transaction, then rollback.
    # Its legacy tables must be empty; it is never a copy of the application DB.
    connection = target.connect()
    transaction = connection.begin()
    try:
        for table, rows in lineage.items():
            if connection.execute(text('SELECT count(*) FROM public.' + table)).scalar_one():
                raise RuntimeError('Expected empty legacy tables in research test DB')
        # The compiler's history mapping needs FK parents; import only into test DB.
        from sqlalchemy.orm import Session
        from .import_map import import_map
        session = Session(bind=connection, expire_on_commit=False, join_transaction_mode='create_savepoint')
        import_map(session)
        session.close()
        for row in sources:
            values = {key: canonical(value) if isinstance(value, (dict, list)) else value for key, value in row.items()}
            keys = list(values)
            expressions = ['CAST(:' + key + ' AS json)' if isinstance(row[key], (dict, list)) else ':' + key for key in keys]
            connection.execute(text('INSERT INTO public.sources (' + ','.join(keys) + ') VALUES (' + ','.join(expressions) + ') ON CONFLICT (id) DO NOTHING'), values)
        # Importer creates baselines; replace with exact source history in this rollback-only transaction.
        for table in ('technical_reviews', 'technical_observations', 'technical_documents',
                      'indicator_observations', 'theme_indicators', 'indicators', 'theme_assessment_versions'):
            connection.execute(text('DELETE FROM public.' + table))
        for table in history_tables:
            for row in lineage[table]:
                values = {key: canonical(value) if isinstance(value, (dict, list)) else value for key, value in row.items()}
                keys = list(values)
                expressions = ['CAST(:' + key + ' AS json)' if isinstance(row[key], (dict, list)) else ':' + key for key in keys]
                connection.execute(text('INSERT INTO public.' + table + ' (' + ','.join(keys) + ') VALUES (' + ','.join(expressions) + ')'), values)
        # Other pg-check suites may leave a head in the test DB; this check runs in a rolled-back transaction.
        connection.execute(text('DELETE FROM research.release_head'))
        # Writing row by row (as before batching) and batched must leave identical tables; both use the real
        # lineage copied above, so legacy_history is compared too.
        with connection.begin_nested() as rowwise:
            immediate = project(connection, bundle, args.commit, publish=True, immediate=True)
            immediate_tables = projection_tables(connection, immediate['release_id'])
            rowwise.rollback()
        first = project(connection, bundle, args.commit, publish=True)
        tables = projection_tables(connection, first['release_id'])
        assert (immediate['release_id'], immediate['content_hash']) == (first['release_id'], first['content_hash'])
        assert immediate_tables == tables, 'Batched projection differs from row-by-row projection'
        second = project(connection, bundle, args.commit, publish=True)
        assert first['release_id'] == second['release_id'] and second['reused']
        rows = connection.execute(text('SELECT entity_id,kind,name,summary,markdown,data,reviewed,semantic_hash FROM research.entity_snapshots WHERE release_id=CAST(:id AS uuid) ORDER BY entity_id'), {'id': first['release_id']}).mappings().all()
        assert len(rows) == len(bundle['snapshots'])
        for actual, expected in zip(rows, bundle['snapshots']):
            assert digest({k: v for k, v in actual.items() if k != 'semantic_hash'}) == expected['semantic_hash']
        counts = dict(connection.execute(text('SELECT history_kind,count(DISTINCT split_part(legacy_id,\':\',2)) FROM research.legacy_history WHERE release_id=CAST(:id AS uuid) GROUP BY history_kind'), {'id': first['release_id']}).all())
        expected_kinds = dict(zip(history_tables[:3] + history_tables[4:],
                                  ('assessment', 'indicator-definition', 'indicator-observation', 'technical-document', 'technical-observation', 'technical-review')))
        for table, kind in expected_kinds.items():
            assert counts.get(kind, 0) == len(lineage[table])
        from .research_search import search_query
        connection.execute(text('SET LOCAL ROLE research_reader'))
        search_plans = []
        for q in ('臺積電', '台積', 'AMD'):
            sql, params = search_query(q, first['release_id'], limit=51)
            plan = connection.execute(text('EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) ' + sql), params).scalar_one()
            search_plans.append({'query': q, 'sql': sql, 'plan': plan})
        print(json.dumps({'commit': args.commit, 'content_hash': first['content_hash'],
            'entities': len(rows), 'same_commit_rebuild': True, 'legacy_history': counts,
            'projection_tables': tables, 'writer_equivalent': True,
            'test_transaction_rolled_back': True, 'search_plans': search_plans}))
    finally:
        transaction.rollback()
        connection.close()
        source.dispose()
        target.dispose()


if __name__ == '__main__':
    main()
