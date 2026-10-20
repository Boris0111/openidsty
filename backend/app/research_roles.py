"""Provision the two application logins from environment, without logging secrets."""
import os
import re
import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url
from .config import DATABASE_URL


def provision():
    admin = make_url(DATABASE_URL)
    if admin.username != 'industry' or admin.database not in ('industry_research', 'industry_research_test'):
        raise RuntimeError('Role provisioning requires the isolated research bootstrap connection')
    with psycopg.connect(admin.set(drivername='postgresql').render_as_string(hide_password=False)) as connection:
        for key, expected in [('RESEARCH_READ_DATABASE_URL', 'research_reader_login'),
                              ('RESEARCH_WRITE_DATABASE_URL', 'research_writer_login')]:
            url = make_url(os.environ[key])
            if url.username != expected or url.host != admin.host or not re.fullmatch('[0-9a-f]{64}', url.password or ''):
                raise RuntimeError('Invalid isolated application credential configuration')
            connection.execute(sql.SQL('ALTER ROLE {} LOGIN PASSWORD {}').format(
                sql.Identifier(expected), sql.Literal(url.password)))


if __name__ == '__main__':
    provision()
    print('Research reader/writer logins provisioned; no credentials displayed')
