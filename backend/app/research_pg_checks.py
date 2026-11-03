"""Explicit isolated PostgreSQL checks; never creates fixtures in the app DB."""
import os
import argparse
from pathlib import Path
from alembic import command
from alembic.config import Config
import psycopg
from sqlalchemy.engine import make_url
from .config import DATABASE_URL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=['all', 'admin-read', 'publication-restart', 'publication-interfaces','source-updates','research-dynamic','reader-navigation'], default='all')
    args = parser.parse_args()
    bootstrap = make_url(DATABASE_URL)
    if bootstrap.username != 'industry' or bootstrap.database != 'industry_research' or bootstrap.host != 'db':
        raise RuntimeError('Run only via the verified research Compose initialize service')
    with psycopg.connect(bootstrap.set(drivername='postgresql').render_as_string(hide_password=False), autocommit=True) as connection:
        connection.execute('SELECT pg_advisory_lock(38109074)')
        exists = connection.execute("SELECT 1 FROM pg_database WHERE datname='industry_research_test'").fetchone()
        if not exists:
            connection.execute('CREATE DATABASE industry_research_test')
        test_url = bootstrap.set(database='industry_research_test').render_as_string(hide_password=False)
        cfg = Config(str(Path(__file__).parents[1] / 'alembic.ini'))
        cfg.attributes['database_url'] = test_url
        command.upgrade(cfg, 'head')
        os.environ['RESEARCH_PG_TEST_URL'] = test_url
        os.environ['RESEARCH_PG_READER_URL'] = make_url(os.environ['RESEARCH_READ_DATABASE_URL']).set(database='industry_research_test').render_as_string(hide_password=False)
        os.environ['RESEARCH_PG_WRITER_URL'] = make_url(os.environ['RESEARCH_WRITE_DATABASE_URL']).set(database='industry_research_test').render_as_string(hide_password=False)
        import pytest
        suites={
            'reader-navigation':['tests/test_research_v2.py','tests/test_research_graph_v2.py','tests/test_research_search.py','tests/test_reader_gateway.py'],
            'research-dynamic':['tests/test_research_dynamic.py','tests/test_research_compare.py','tests/test_research_cache.py','tests/test_research_updates.py'],
            'source-updates':['tests/test_source_updates.py'],
            'publication-interfaces':['tests/test_publication_interfaces.py'],
            'publication-restart':['tests/test_research_restart.py'],
            'admin-read':['tests/test_research_admin_reads.py','tests/test_research_coverage.py'],
        }
        cases = suites.get(args.suite,['tests/test_research_postgres.py',
            'tests/test_research_v2.py', 'tests/test_research_graph_v2.py', 'tests/test_research_search.py',
            'tests/test_research_auth.py', 'tests/test_research_documents.py', 'tests/test_research_drafts.py',
            'tests/test_research_publication.py', 'tests/test_projection_writer.py', 'tests/test_research_admin_reads.py', 'tests/test_research_coverage.py', 'tests/test_research_restart.py', 'tests/test_publication_interfaces.py',
            'tests/test_sec_http.py','tests/test_source_updates.py','tests/test_research_dynamic.py','tests/test_research_compare.py','tests/test_research_cache.py','tests/test_research_updates.py','tests/test_reader_gateway.py'])
        raise SystemExit(pytest.main(['-q', '-p', 'no:cacheprovider', *cases]))


if __name__ == '__main__':
    main()
