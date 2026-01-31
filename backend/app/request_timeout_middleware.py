"""Request timeout middleware for FastAPI application.

This middleware ensures all HTTP requests complete within a configured timeout,
preventing long-running requests from hanging indefinitely.
"""

import asyncio
from collections.abc import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces a timeout on all HTTP requests.

    If a request takes longer than the configured timeout, it will be cancelled
    and a 504 Gateway Timeout response will be returned.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process the request with a timeout.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            The HTTP response.
        """
        timeout = get_settings().request_timeout

        try:
            return await asyncio.wait_for(call_next(request), timeout=timeout)

        except TimeoutError:
            logger.warning(
                "request_timeout_exceeded",
                method=request.method,
                path=request.url.path,
                timeout=timeout,
            )
            return JSONResponse(
                content={
                    "error": "Request timeout",
                    "message": "The request took too long to process",
                },
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            )
