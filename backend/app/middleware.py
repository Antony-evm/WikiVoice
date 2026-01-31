from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.auth_middleware import StytchAuthMiddleware
from app.config import get_settings
from app.logging_middleware import LoggingMiddleware
from app.request_timeout_middleware import RequestTimeoutMiddleware
from app.response_headers_middleware import ResponseHeadersMiddleware


def include_middleware(app: FastAPI) -> None:
    """Include middleware in the FastAPI application.

    Note: Middleware is executed in reverse order of addition.
    Last added middleware runs first (outermost).
    """
    settings = get_settings()

    # Parse frontend URLs - support comma-separated list for multiple origins
    allowed_origins = [
        origin.strip() for origin in settings.frontend_url.split(",") if origin.strip()
    ]
    # Always allow localhost for development
    if "http://localhost:5173" not in allowed_origins:
        allowed_origins.append("http://localhost:5173")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Session-JWT", "X-Session-Token", "X-Stytch-User-ID"],
    )

    app.add_middleware(ResponseHeadersMiddleware)
    app.add_middleware(StytchAuthMiddleware)
    app.add_middleware(RequestTimeoutMiddleware)
    app.add_middleware(LoggingMiddleware)
