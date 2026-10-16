"""Single local owner; opaque sessions, persistent throttling and CSRF checks."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import math
import os
import re
import secrets
from urllib.parse import urlsplit

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from .research_db import get_admin_connection, writer_engine
from .research_http import ResearchError

router = APIRouter(prefix='/api/admin', tags=['owner'])
SESSION_COOKIE = 'industryflow_owner'
CHALLENGE_COOKIE = 'industryflow_login_csrf'
COOKIE_PATH = '/api/admin'
TOKEN = re.compile(r'^[A-Za-z0-9_-]{43}$')
HASHER = PasswordHasher()  # Argon2id, RFC 9106 low-memory parameters (64 MiB).
IDLE = timedelta(minutes=30)
MAX_AGE = timedelta(hours=8)


def utc_now():
    return datetime.now(timezone.utc)


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class AdminConfig:
    secure: bool
    origins: frozenset[str]
    hosts: frozenset[str]
    secret: bytes


def admin_config():
    mode = os.getenv('RESEARCH_ADMIN_MODE', 'disabled')
    origins = frozenset(filter(None, os.getenv('RESEARCH_ADMIN_ORIGINS', '').split(',')))
    hosts = frozenset(filter(None, os.getenv('RESEARCH_ADMIN_HOSTS', '').split(',')))
    secret = os.getenv('RESEARCH_SESSION_SECRET', '')
    valid = mode in ('loopback-http', 'https') and origins and hosts and re.fullmatch('[0-9a-f]{64}', secret)
    for origin in origins:
        try:
            parsed = urlsplit(origin)
            parsed.port
        except ValueError:
            valid = False
            continue
        valid = valid and (parsed.scheme in ('http', 'https') and parsed.netloc and not parsed.username
            and not parsed.password and not parsed.path and not parsed.query and not parsed.fragment)
        if mode == 'loopback-http':
            valid = valid and parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost', '::1')
        else:
            valid = valid and parsed.scheme == 'https'
    if not valid:
        raise ResearchError(503, 'admin-unavailable', '管理入口尚未完成安全設定。')
    return AdminConfig(mode == 'https', origins, hosts, bytes.fromhex(secret))


def check_boundary(request, *, write=False):
    config = admin_config()
    host_values = request.headers.getlist('host')
    origin_values = request.headers.getlist('origin')
    if len(host_values) != 1 or host_values[0] not in config.hosts:
        raise ResearchError(403, 'admin-origin-denied', '此來源無法使用管理入口。')
    if (len(origin_values) > 1 or (origin_values and origin_values[0] not in config.origins)
            or (write and not origin_values)
            or request.headers.get('sec-fetch-site') == 'cross-site'):
        raise ResearchError(403, 'admin-origin-denied', '此來源無法使用管理入口。')
    return config


def csrf_for(token, config):
    return hmac.new(config.secret, ('session-csrf:' + token).encode(), hashlib.sha256).hexdigest()


def cookie(response, name, value, config, seconds):
    response.set_cookie(name, value, max_age=seconds, path=COOKIE_PATH,
                        secure=config.secure, httponly=True, samesite='strict')


def expire_cookie(response, name, config):
    response.delete_cookie(name, path=COOKIE_PATH, secure=config.secure, httponly=True, samesite='strict')


def load_session(connection, token, *, touch=True):
    if not token or not TOKEN.fullmatch(token):
        return None
    # Consistent lock order with login and CLI reset: owner first, then session.
    owner = connection.execute(text('SELECT credential_version FROM research.admin_owner WHERE singleton FOR SHARE')).scalar_one_or_none()
    if owner is None:
        return None
    now = utc_now()
    row = connection.execute(text('''SELECT * FROM research.admin_sessions WHERE token_hash=:hash
        AND credential_version=:version AND revoked_at IS NULL AND absolute_expires_at>:now
        AND last_seen_at>:idle FOR UPDATE'''),
        {'hash': digest(token), 'version': owner, 'now': now, 'idle': now - IDLE}).mappings().first()
    if row and touch:
        connection.execute(text('UPDATE research.admin_sessions SET last_seen_at=:now WHERE token_hash=:hash'),
                           {'now': now, 'hash': digest(token)})
    return dict(row) if row else None


def require_owner(request: Request, connection=Depends(get_admin_connection)):
    check_boundary(request)
    token = request.cookies.get(SESSION_COOKIE)
    session = load_session(connection, token)
    if session is None:
        raise ResearchError(401, 'owner-required', '請先登入管理入口。')
    return session


def require_owner_write(request: Request, connection=Depends(get_admin_connection)):
    check_boundary(request, write=True)
    session = require_owner(request, connection)
    supplied = request.headers.get('x-csrf-token', '')
    if not supplied or not hmac.compare_digest(digest(supplied), session['csrf_hash']):
        raise ResearchError(403, 'csrf-denied', '驗證已失效，請重新開啟管理入口。')
    return session


def signed_challenge(config):
    nonce = secrets.token_urlsafe(32)
    value = nonce + '.' + str(int(utc_now().timestamp()))
    signature = hmac.new(config.secret, ('login:' + value).encode(), hashlib.sha256).hexdigest()
    return nonce, value + '.' + signature


def check_login_csrf(request, config):
    """The pre-login challenge is signed, short-lived and bound to an HttpOnly cookie."""
    supplied = request.headers.get('x-csrf-token', '')
    value = request.cookies.get(CHALLENGE_COOKIE, '')
    parts = value.split('.')
    if (TOKEN.fullmatch(supplied) and len(parts) == 3 and TOKEN.fullmatch(parts[0])
            and parts[1].isascii() and parts[1].isdigit() and len(parts[1]) <= 12
            and re.fullmatch('[0-9a-f]{64}', parts[2])):
        age = utc_now().timestamp() - int(parts[1])
        expected = hmac.new(config.secret, ('login:' + '.'.join(parts[:2])).encode(), hashlib.sha256).hexdigest()
        if 0 <= age < 600 and hmac.compare_digest(expected, parts[2]) and hmac.compare_digest(supplied, parts[0]):
            return
    raise ResearchError(403, 'csrf-denied', '登入驗證已失效，請重新開啟管理入口。')


def login_attempt(request, config):
    # Transport peer only. X-Forwarded-For is deliberately never trusted here.
    peer = request.client.host if request.client else 'unknown'
    key = hmac.new(config.secret, ('login-ip:' + peer).encode(), hashlib.sha256).hexdigest()
    now = utc_now()
    retry = None
    # A separate committed transaction persists failed attempts and survives restarts.
    with writer_engine().begin() as connection:
        connection.execute(text('''INSERT INTO research.login_attempts VALUES (:key,0,:now,NULL)
            ON CONFLICT (bucket_hash) DO NOTHING'''), {'key': key, 'now': now})
        row = connection.execute(text('SELECT * FROM research.login_attempts WHERE bucket_hash=:key FOR UPDATE'), {'key': key}).mappings().one()
        if row['blocked_until'] and row['blocked_until'] > now:
            retry = max(1, math.ceil((row['blocked_until'] - now).total_seconds()))
        else:
            expired = now - row['window_start'] >= timedelta(minutes=1) or row['blocked_until'] is not None
            attempts = 0 if expired else row['attempts']
            blocked = now + timedelta(minutes=15) if attempts >= 5 else None
            connection.execute(text('''UPDATE research.login_attempts SET attempts=:attempts,
                window_start=:start,blocked_until=:blocked WHERE bucket_hash=:key'''),
                {'key': key, 'attempts': attempts + 1, 'start': now if expired else row['window_start'], 'blocked': blocked})
            if blocked:
                retry = 900
    if retry:
        raise ResearchError(429, 'login-limited', '登入嘗試過於頻繁，請稍後再試。', True, retry_after=retry)


@router.get('/session')
def session_state(request: Request, connection=Depends(get_admin_connection)):
    config = check_boundary(request)
    token = request.cookies.get(SESSION_COOKIE)
    session = load_session(connection, token)
    if session:
        return JSONResponse({'authenticated': True, 'csrf_token': csrf_for(token, config),
            'absolute_expires_at': session['absolute_expires_at'].isoformat()}, headers={'Cache-Control': 'no-store'})
    nonce, challenge = signed_challenge(config)
    configured = connection.execute(text('SELECT EXISTS(SELECT 1 FROM research.admin_owner)')).scalar_one()
    response = JSONResponse({'authenticated': False, 'owner_configured': configured, 'csrf_token': nonce},
                            headers={'Cache-Control': 'no-store'})
    cookie(response, CHALLENGE_COOKIE, challenge, config, 600)
    expire_cookie(response, SESSION_COOKIE, config)
    return response


def perform_login(request, password):
    config = check_boundary(request, write=True)
    with writer_engine().begin() as connection:
        previous = load_session(connection, request.cookies.get(SESSION_COOKIE), touch=False)
        if previous:
            supplied = request.headers.get('x-csrf-token', '')
            if not supplied or not hmac.compare_digest(digest(supplied), previous['csrf_hash']):
                raise ResearchError(403, 'csrf-denied', '驗證已失效，請重新開啟管理入口。')
        else:
            check_login_csrf(request, config)
    login_attempt(request, config)
    with writer_engine().begin() as connection:
        owner = connection.execute(text('SELECT * FROM research.admin_owner WHERE singleton FOR UPDATE')).mappings().first()
        if not owner:
            raise ResearchError(503, 'owner-not-configured', '請先由本機設定維護者密碼。')
        try:
            HASHER.verify(owner['password_hash'], password)
        except (VerificationError, InvalidHashError):
            raise ResearchError(401, 'login-failed', '密碼不正確。') from None
        if HASHER.check_needs_rehash(owner['password_hash']):
            connection.execute(text('UPDATE research.admin_owner SET password_hash=:hash WHERE singleton'),
                               {'hash': HASHER.hash(password)})
        if previous:
            connection.execute(text('UPDATE research.admin_sessions SET revoked_at=:now WHERE token_hash=:hash'),
                               {'now': utc_now(), 'hash': previous['token_hash']})
        token = secrets.token_urlsafe(32)
        csrf = csrf_for(token, config)
        now = utc_now()
        connection.execute(text('''INSERT INTO research.admin_sessions
            (token_hash,csrf_hash,credential_version,created_at,last_seen_at,absolute_expires_at)
            VALUES (:token,:csrf,:version,:now,:now,:expiry)'''),
            {'token': digest(token), 'csrf': digest(csrf), 'version': owner['credential_version'], 'now': now, 'expiry': now + MAX_AGE})
        connection.execute(text("INSERT INTO research.audit_log(actor,operation,detail) VALUES ('owner','login','{}')"))
    response = JSONResponse({'authenticated': True, 'csrf_token': csrf, 'absolute_expires_at': (now + MAX_AGE).isoformat()},
                            headers={'Cache-Control': 'no-store'})
    cookie(response, SESSION_COOKIE, token, config, int(MAX_AGE.total_seconds()))
    expire_cookie(response, CHALLENGE_COOKIE, config)
    return response


@router.post('/session')
async def login(request: Request):
    check_boundary(request, write=True)
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 8192:
            raise ResearchError(413, 'body-too-large', '登入資料超過大小限制。')
    try:
        data = json.loads(body)
        password = data['password']
        if not isinstance(data, dict) or set(data) != {'password'} or not isinstance(password, str) or not 1 <= len(password.encode()) <= 1024:
            raise ValueError()
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise ResearchError(422, 'invalid-request', '請提供有效密碼。') from None
    return await run_in_threadpool(perform_login, request, password)


@router.delete('/session')
def logout(request: Request, owner=Depends(require_owner_write), connection=Depends(get_admin_connection)):
    config = check_boundary(request, write=True)
    connection.execute(text('UPDATE research.admin_sessions SET revoked_at=:now WHERE token_hash=:hash'),
                       {'now': utc_now(), 'hash': owner['token_hash']})
    connection.execute(text("INSERT INTO research.audit_log(actor,operation,detail) VALUES ('owner','logout','{}')"))
    response = JSONResponse({'authenticated': False}, headers={'Cache-Control': 'no-store'})
    expire_cookie(response, SESSION_COOKIE, config)
    expire_cookie(response, CHALLENGE_COOKIE, config)
    return response
