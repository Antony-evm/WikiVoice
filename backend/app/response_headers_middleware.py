from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ResponseHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add session headers to all API responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through response headers middleware."""
        response = await call_next(request)
        new_session_token = getattr(request.state, "session_token", None)
        new_session_jwt = getattr(request.state, "session_jwt", None)
        if new_session_token:
            response.headers["X-Session-Token"] = new_session_token
        else:
            session_token = request.headers.get("authorization", "").replace("Bearer ", "")
            if session_token:
                response.headers["X-Session-Token"] = session_token

        if new_session_jwt:
            response.headers["X-Session-JWT"] = new_session_jwt
        else:
            session_jwt = request.headers.get("session-jwt", "")
            if session_jwt:
                response.headers["X-Session-JWT"] = session_jwt

        return response
