"""Classify an actual failed attempt, without changing last successful data."""
import httpx


def failure_details(exc):
    if isinstance(exc, ValueError) and '需設定 SEC_USER_AGENT' in str(exc):
        return {'last_error_kind': 'configuration', 'last_http_status': None}
    current, visited = exc, set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if isinstance(current, httpx.HTTPStatusError):
            return {'last_error_kind': 'http', 'last_http_status': current.response.status_code}
        if isinstance(current, httpx.TimeoutException):
            return {'last_error_kind': 'timeout', 'last_http_status': None}
        if isinstance(current, httpx.HTTPError):
            return {'last_error_kind': 'network', 'last_http_status': None}
        current = current.__cause__ or current.__context__
    return {'last_error_kind': 'parse' if isinstance(exc, (ValueError, SyntaxError)) else 'internal', 'last_http_status': None}
