import httpx
import pytest
from sqlalchemy import select
from app.ingest import ingest_one, register_sources
from app.models import Company, Source


def wrapped_http_error():
    request = httpx.Request('GET', 'https://official.test/')
    response = httpx.Response(403, request=request)
    error = ValueError('HTTP 擷取失敗')
    error.__cause__ = httpx.HTTPStatusError('HTTP 403', request=request, response=response)
    return error


@pytest.mark.parametrize('error,kind,status,http_status', [
    (ValueError('需設定 SEC_USER_AGENT：專案名稱與維護者聯絡 email'), 'configuration', 'configuration_required', None),
    (wrapped_http_error(), 'http', 'failed', 403),
    (httpx.ReadTimeout('timeout'), 'timeout', 'failed', None),
    (ValueError('官方表格缺少必要欄位'), 'parse', 'failed', None),
])
def test_failed_attempt_is_classified_and_recovery_clears_diagnostic(db, error, kind, status, http_status):
    definitions = register_sources(db)
    definition = next(d for d in definitions if d['id'] == 'ir-tsmc')
    companies = list(db.scalars(select(Company)))
    def success(*args): return [], []
    ingest_one(db, definition, None, companies, success)
    last_success = db.get(Source, definition['id']).last_success
    def failure(*args): raise error
    assert ingest_one(db, definition, None, companies, failure)['status'] == status
    source = db.get(Source, definition['id'])
    assert source.data['last_error_kind'] == kind
    assert source.data['last_http_status'] == http_status
    assert source.last_success == last_success
    register_sources(db)
    assert source.data['last_error_kind'] == kind
    assert ingest_one(db, definition, None, companies, success)['status'] == 'success'
    assert source.data['last_error_kind'] is None
    assert source.data['last_http_status'] is None
