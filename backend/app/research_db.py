"""Independent query pool. Never fall back to the writer for a reader request."""
from functools import lru_cache
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from .research_http import ResearchError


@lru_cache(maxsize=1)
def reader_engine():
    url = os.environ.get('RESEARCH_READ_DATABASE_URL')
    if not url:
        raise ResearchError(503, 'research-unavailable', '新版研究尚未完成初始化。', True)
    engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5, hide_parameters=True)
    if engine.url.username != 'research_reader_login' or engine.dialect.name != 'postgresql':
        engine.dispose()
        raise ResearchError(503, 'research-unavailable', '新版研究讀取設定尚未完成。', True)
    return engine


def get_research_session():
    with reader_engine().connect().execution_options(isolation_level='REPEATABLE READ') as connection:
        with Session(bind=connection, expire_on_commit=False) as session:
            session.execute(text('SET TRANSACTION READ ONLY'))
            yield session


@lru_cache(maxsize=1)
def writer_engine():
    """Only explicit research credentials may execute admin commands."""
    url = os.environ.get('RESEARCH_WRITE_DATABASE_URL')
    if not url:
        raise ResearchError(503, 'admin-unavailable', '管理服務尚未完成設定。', True)
    engine = create_engine(url, pool_pre_ping=True, pool_size=3, max_overflow=2, hide_parameters=True)
    if (engine.url.username != 'research_writer_login' or engine.dialect.name != 'postgresql'
            or engine.url.database not in ('industry_research', 'industry_research_test')):
        engine.dispose()
        raise ResearchError(503, 'admin-unavailable', '管理資料庫設定不正確。', True)
    return engine


def get_admin_connection():
    with writer_engine().begin() as connection:
        yield connection
