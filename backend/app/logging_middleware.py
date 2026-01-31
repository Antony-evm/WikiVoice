"""Logging middleware to inject request context into all log entries.

This middleware:
- Generates a unique request_id for each request
- Extracts user_id from authenticated requests
- Makes both available via contextvars for automatic inclusion in logs
- Logs request start/end with timing information
"""

import time
import uuid

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import get_logger, request_id_var, user_id_var

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that injects request_id and user_id into log context.

    Should be added early in the middleware stack so that all subsequent
    middleware and handlers have access to the logging context.
    """

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        """Process request through logging middleware."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_token = request_id_var.set(request_id)
        user_id_token = None
        request.state.request_id = request_id

        start_time = time.perf_counter()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
        )

        try:
            response = await call_next(request)
            user_id = self._get_user_id(request)
            if user_id:
                user_id_token = user_id_var.set(user_id)

            duration_ms = (time.perf_counter() - start_time) * 1000
            if response.status_code < status.HTTP_400_BAD_REQUEST:
                log_method = logger.info
            else:
                log_method = logger.warning
            log_method(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            response.headers["X-Request-ID"] = request_id

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error_type=type(exc).__name__,
                exc_info=True,
            )
            raise
        else:
            return response
        finally:
            request_id_var.reset(request_id_token)
            if user_id_token:
                user_id_var.reset(user_id_token)

    def _get_user_id(self, request: Request) -> str | None:
        """Attempt to get the internal user_id from request state.

        Note: This gets the stytch_user_id from auth middleware.
        The actual internal user_id resolution happens later in the dependency.
        For logging purposes, we use whatever is available.
        """
        try:
            if hasattr(request.state, "user_id"):
                return request.state.user_id
        except AttributeError:
            pass
        return None
