"""Explicit isolated PostgreSQL checks; never creates fixtures in the app DB."""
import os
from pathlib import Path
from alembic import command
from alembic.config import Config
import psycopg
from sqlalchemy.engine import make_url
from .config import DATABASE_URL


def main():
    bootstrap = make_url(DATABASE_URL)
    if bootstrap.username != 'industry' or bootstrap.database != 'industry_research' or bootstrap.host != 'db':
        raise RuntimeError('Run only via the verified research Compose initialize service')
    with psycopg.connect(bootstrap.set(drivername='postgresql').render_as_string(hide_password=False), autocommit=True) as connection:
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
    raise SystemExit(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_research_postgres.py',
        'tests/test_research_v2.py', 'tests/test_research_graph_v2.py', 'tests/test_research_search.py']))


if __name__ == '__main__':
    main()
