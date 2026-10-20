"""One PostgreSQL gate for every SEC request in the active ingestion runtime."""
from contextlib import contextmanager
import os,re
from urllib.parse import urlsplit
from sqlalchemy import text

SEC_LOCK=38109077


def is_sec(url):
    host=(urlsplit(url).hostname or '').lower()
    return host=='sec.gov' or host.endswith('.sec.gov')


def validate_sec_url(url):
    parsed=urlsplit(url)
    if (parsed.scheme!='https' or parsed.hostname not in ('sec.gov','www.sec.gov','data.sec.gov') or
        parsed.port not in (None,443) or parsed.username or parsed.password or any(ord(c)<33 for c in url)):
        raise ValueError('SEC 請求只允許已核對的官方 HTTPS 主機。')


def user_agent():
    value=os.getenv('SEC_USER_AGENT','').strip()
    if (not re.fullmatch(r'[\x20-\x7e]{8,250}',value) or
        not re.search(r'\S+\s+.*[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}',value)):
        raise ValueError('需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email')
    return value


@contextmanager
def request_gate(engine=None):
    if engine is None:
        if os.getenv('RESEARCH_WRITE_DATABASE_URL'):
            from .research_db import writer_engine
            engine=writer_engine()
        else:
            from .db import engine
    if engine.dialect.name!='postgresql':raise ValueError('SEC 總限流需要 PostgreSQL，不允許程序內替代。')
    # The session lock stays held through the actual network operation. Waiting
    # 0.5 s on *every* acquisition also bounds crash/restart and delayed senders.
    # No table writes, reservation race, floating timestamps or extra service.
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
        locked=False
        try:
            connection.execute(text('SELECT pg_advisory_lock(:key)'),{'key':SEC_LOCK})
            locked=True
            connection.execute(text('SELECT pg_sleep(0.5)'))
            yield
        finally:
            try:
                if locked:connection.execute(text('SELECT pg_advisory_unlock(:key)'),{'key':SEC_LOCK})
                else:connection.invalidate()
            except Exception:
                connection.invalidate()
