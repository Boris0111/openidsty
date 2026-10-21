"""Real PostgreSQL owner/session contracts; all credentials and records are synthetic."""
from datetime import timedelta
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from app.main import app
from app import research_auth as auth
from app.research_db import get_admin_connection
from app.research_http import ResearchError
from app.research_owner import set_owner

ORIGIN = 'http://localhost:3010'
PASSWORD = 'synthetic owner password only'


@pytest.fixture
def owner(monkeypatch):
    url = os.getenv('RESEARCH_PG_WRITER_URL')
    if not url:
        pytest.skip('owner contracts require disposable research PostgreSQL')
    engine = create_engine(url, hide_parameters=True)
    if engine.url.database != 'industry_research_test':
        raise RuntimeError('Refusing owner tests outside the disposable research DB')
    monkeypatch.setenv('RESEARCH_ADMIN_MODE', 'loopback-http')
    monkeypatch.setenv('RESEARCH_ADMIN_ORIGINS', ORIGIN)
    monkeypatch.setenv('RESEARCH_ADMIN_HOSTS', 'localhost:3010')
    monkeypatch.setenv('RESEARCH_SESSION_SECRET', 'a' * 64)
    monkeypatch.setattr(auth, 'writer_engine', lambda: engine)
    def connection():
        with engine.begin() as conn:
            yield conn
    app.dependency_overrides[get_admin_connection] = connection
    with engine.begin() as conn:
        for table in ('admin_sessions', 'login_attempts', 'admin_owner'):
            conn.execute(text('DELETE FROM research.' + table))
        set_owner(conn, PASSWORD)
    with TestClient(app, base_url=ORIGIN, client=('127.0.0.1', 4567)) as client:
        yield client, engine
    app.dependency_overrides.pop(get_admin_connection, None)
    with engine.begin() as conn:
        for table in ('admin_sessions', 'login_attempts', 'admin_owner'):
            conn.execute(text('DELETE FROM research.' + table))
    engine.dispose()


def login(client, password=PASSWORD, **headers):
    challenge = client.get('/api/admin/session')
    assert challenge.status_code == 200
    return client.post('/api/admin/session', json={'password': password},
        headers={'Origin': ORIGIN, 'X-CSRF-Token': challenge.json()['csrf_token'], **headers})


def test_password_setup_reset_and_database_only_hashes(owner):
    client, engine = owner
    result = login(client)
    assert result.status_code == 200
    token = client.cookies.get(auth.SESSION_COOKIE)
    assert len(token) == 43 and PASSWORD not in result.text and token not in result.text
    cookies = result.headers.get_list('set-cookie')
    assert any('HttpOnly' in value and 'SameSite=strict' in value and 'Path=/api/admin' in value for value in cookies)
    assert not any('; Secure' in value for value in cookies)
    with engine.begin() as conn:
        saved = conn.execute(text('SELECT * FROM research.admin_owner')).mappings().one()
        assert saved['password_hash'].startswith('$argon2id$') and PASSWORD not in saved['password_hash']
        session = conn.execute(text('SELECT * FROM research.admin_sessions')).mappings().one()
        assert session['token_hash'] == auth.digest(token) and session['csrf_hash'] == auth.digest(result.json()['csrf_token'])
        assert session['absolute_expires_at'] - session['created_at'] == timedelta(hours=8)
        with pytest.raises(ValueError):
            set_owner(conn, 'another synthetic password')
        set_owner(conn, 'new synthetic owner password', reset=True)
    assert client.get('/api/admin/session').json()['authenticated'] is False
    assert login(client).status_code == 401
    assert login(client, 'new synthetic owner password').status_code == 200


def test_login_csrf_origin_host_and_error_redaction(owner):
    client, _ = owner
    challenge = client.get('/api/admin/session').json()['csrf_token']
    for headers in ({}, {'Origin': 'https://evil.example', 'X-CSRF-Token': challenge},
                    {'Origin': ORIGIN}, {'Origin': ORIGIN, 'X-CSRF-Token': 'wrong'},
                    {'Origin': ORIGIN, 'Host': 'evil.example', 'X-CSRF-Token': challenge},
                    {'Origin': ORIGIN, 'Sec-Fetch-Site': 'cross-site', 'X-CSRF-Token': challenge}):
        result = client.post('/api/admin/session', json={'password': PASSWORD}, headers=headers)
        assert result.status_code == 403
        assert PASSWORD not in result.text and result.json()['request_id'] == result.headers['x-request-id']
        assert result.headers['cache-control'] == 'no-store'
    other = TestClient(app, base_url=ORIGIN)
    assert other.post('/api/admin/session', json={'password': PASSWORD}, headers={'Origin': ORIGIN, 'X-CSRF-Token': challenge}).status_code == 403
    invalid = client.post('/api/admin/session', json={'password': PASSWORD, 'extra': PASSWORD}, headers={'Origin': ORIGIN})
    assert invalid.status_code == 422 and PASSWORD not in invalid.text
    assert client.post('/api/admin/session', content=b'x' * 8193, headers={'Origin': ORIGIN}).status_code == 413


@pytest.mark.parametrize('expired', ['idle', 'absolute', 'revoked', 'credential'])
def test_expired_and_revoked_sessions_reject_owner_commands(owner, expired):
    client, engine = owner
    result = login(client)
    csrf = result.json()['csrf_token']
    with engine.begin() as conn:
        if expired == 'idle':
            conn.execute(text("UPDATE research.admin_sessions SET last_seen_at=now()-interval '31 minutes'"))
        elif expired == 'absolute':
            conn.execute(text("UPDATE research.admin_sessions SET absolute_expires_at=now()-interval '1 second'"))
        elif expired == 'revoked':
            conn.execute(text('UPDATE research.admin_sessions SET revoked_at=now()'))
        else:
            conn.execute(text('UPDATE research.admin_owner SET credential_version=credential_version+1'))
    denied = client.delete('/api/admin/session', headers={'Origin': ORIGIN, 'X-CSRF-Token': csrf})
    assert denied.status_code == 401
    assert not client.get('/api/admin/session').json()['authenticated']


def test_logout_revokes_replayed_cookie_and_relogin_rotates_token(owner):
    client, _ = owner
    initial = login(client)
    old = client.cookies.get(auth.SESSION_COOKIE)
    renewed = login(client)
    assert renewed.status_code == 200 and old != client.cookies.get(auth.SESSION_COOKIE)
    replay = TestClient(app, base_url=ORIGIN)
    replay.cookies.set(auth.SESSION_COOKIE, old, path=auth.COOKIE_PATH)
    assert not replay.get('/api/admin/session').json()['authenticated']
    assert client.delete('/api/admin/session', headers={'Origin': ORIGIN, 'X-CSRF-Token': initial.json()['csrf_token']}).status_code == 403
    current = client.cookies.get(auth.SESSION_COOKIE)
    assert client.delete('/api/admin/session', headers={'Origin': ORIGIN, 'X-CSRF-Token': renewed.json()['csrf_token']}).status_code == 200
    replay.cookies.set(auth.SESSION_COOKIE, current, path=auth.COOKIE_PATH)
    assert not replay.get('/api/admin/session').json()['authenticated']
    assert client.delete('/api/admin/session', headers={'Origin': ORIGIN}).status_code == 401


def test_persistent_rate_limit_ignores_forwarded_ip_and_recovers(owner, monkeypatch):
    client, engine = owner
    now = auth.utc_now()
    monkeypatch.setattr(auth, 'utc_now', lambda: now)
    for index in range(5):
        assert login(client, 'wrong password', **{'X-Forwarded-For': '192.0.2.' + str(index)}).status_code == 401
    blocked = login(client)
    assert blocked.status_code == 429 and blocked.headers['retry-after'] == '900'
    with engine.begin() as conn:
        assert conn.execute(text('SELECT count(*) FROM research.login_attempts')).scalar_one() == 1
    # New client/connection has the same durable bucket.
    another = TestClient(app, base_url=ORIGIN, client=('127.0.0.1', 9999))
    assert login(another).status_code == 429
    monkeypatch.setattr(auth, 'utc_now', lambda: now + timedelta(minutes=16))
    assert login(client).status_code == 200


def test_challenge_expiry_and_anonymous_cannot_logout(owner, monkeypatch):
    client, _ = owner
    now = auth.utc_now()
    token = client.get('/api/admin/session').json()['csrf_token']
    monkeypatch.setattr(auth, 'utc_now', lambda: now + timedelta(minutes=11))
    assert client.post('/api/admin/session', json={'password': PASSWORD}, headers={'Origin': ORIGIN, 'X-CSRF-Token': token}).status_code == 403
    assert client.delete('/api/admin/session', headers={'Origin': ORIGIN, 'X-CSRF-Token': token}).status_code == 401


def test_secure_cookie_and_no_private_http_exception(owner, monkeypatch):
    client, _ = owner
    monkeypatch.setenv('RESEARCH_ADMIN_MODE', 'https')
    monkeypatch.setenv('RESEARCH_ADMIN_ORIGINS', 'https://localhost:3010')
    https = TestClient(app, base_url='https://localhost:3010')
    challenge = https.get('/api/admin/session')
    assert all('; Secure' in value for value in challenge.headers.get_list('set-cookie'))
    result = https.post('/api/admin/session', json={'password': PASSWORD},
        headers={'Origin': 'https://localhost:3010', 'X-CSRF-Token': challenge.json()['csrf_token']})
    assert result.status_code == 200
    assert all('; Secure' in value for value in result.headers.get_list('set-cookie'))
    monkeypatch.setenv('RESEARCH_ADMIN_MODE', 'loopback-http')
    monkeypatch.setenv('RESEARCH_ADMIN_ORIGINS', 'http://192.168.1.2:3010')
    assert client.get('/api/admin/session').status_code == 503


def test_setup_password_policy_and_missing_writer_never_uses_reader(monkeypatch):
    from app.research_db import writer_engine
    for password in ('short', 'x' * 1025):
        with pytest.raises(ValueError):
            set_owner(None, password)
    monkeypatch.delenv('RESEARCH_WRITE_DATABASE_URL', raising=False)
    writer_engine.cache_clear()
    with pytest.raises(ResearchError) as caught:
        writer_engine()
    assert caught.value.status == 503
    monkeypatch.setenv('RESEARCH_WRITE_DATABASE_URL', 'postgresql+psycopg://research_reader_login@localhost/industry_research')
    with pytest.raises(ResearchError):
        writer_engine()
    writer_engine.cache_clear()


def test_malformed_origin_config_and_challenge_are_rejected(monkeypatch):
    from starlette.requests import Request
    monkeypatch.setenv('RESEARCH_ADMIN_MODE', 'https')
    monkeypatch.setenv('RESEARCH_ADMIN_ORIGINS', 'https://[bad')
    monkeypatch.setenv('RESEARCH_ADMIN_HOSTS', 'localhost:3010')
    monkeypatch.setenv('RESEARCH_SESSION_SECRET', 'a' * 64)
    with pytest.raises(ResearchError):
        auth.admin_config()
    config = auth.AdminConfig(False, frozenset({ORIGIN}), frozenset({'localhost:3010'}), b'a' * 32)
    nonce, challenge = auth.signed_challenge(config)
    for supplied, saved in [('bad', challenge), (nonce, challenge[:-1] + 'x'), ('é', challenge)]:
        request = Request({'type': 'http', 'headers': [(b'x-csrf-token', supplied.encode('latin-1')),
            (b'cookie', (auth.CHALLENGE_COOKIE + '=' + saved).encode())]})
        with pytest.raises(ResearchError) as caught:
            auth.check_login_csrf(request, config)
        assert caught.value.status == 403
