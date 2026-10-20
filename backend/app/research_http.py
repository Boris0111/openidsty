"""V2-only error contracts; legacy responses retain their existing shapes."""
import uuid
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from sqlalchemy.exc import DBAPIError


class ResearchError(Exception):
    def __init__(self, status, code, message, retryable=False, **extra):
        self.status, self.code, self.message = status, code, message
        self.retryable, self.extra = retryable, extra


def error_response(request, error):
    response = JSONResponse(jsonable_encoder({'code': error.code, 'message': error.message,
        'request_id': getattr(request.state, 'request_id', uuid.uuid4().hex),
        'retryable': error.retryable, **error.extra}), status_code=error.status)
    response.headers['Cache-Control'] = 'no-store'
    if error.retryable:
        response.headers['Retry-After'] = str(error.extra.get('retry_after', 5))
    return response


def install(app):
    @app.middleware('http')
    async def request_identity(request, call_next):
        if request.url.path.startswith(('/api/v2/', '/api/admin/')):
            request.state.request_id = uuid.uuid4().hex
        response = await call_next(request)
        if hasattr(request.state, 'request_id'):
            response.headers['X-Request-ID'] = request.state.request_id
        return response

    @app.exception_handler(ResearchError)
    async def research_error(request, error):
        return error_response(request, error)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, error):
        if request.url.path.startswith(('/api/v2/', '/api/admin/')):
            return error_response(request, ResearchError(422, 'invalid-request', '查詢格式不正確，請確認條件。'))
        return await request_validation_exception_handler(request, error)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, error):
        if request.url.path.startswith(('/api/v2/', '/api/admin/')):
            return error_response(request, ResearchError(error.status_code, 'not-found' if error.status_code == 404 else 'invalid-request',
                '找不到這筆研究。' if error.status_code == 404 else '無法完成這個請求。'))
        return await http_exception_handler(request, error)

    @app.exception_handler(DBAPIError)
    async def database_error(request, error):
        if request.url.path.startswith(('/api/v2/', '/api/admin/')):
            return error_response(request, ResearchError(503, 'database-unavailable', '目前無法讀取研究，請稍後再試。', True))
        return JSONResponse({'detail': '服務暫時無法使用'}, status_code=503)
