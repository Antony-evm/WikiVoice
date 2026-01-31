from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from app.config import get_settings
from app.exception_handlers import (
    domain_exception_handler,
    global_exception_handler,
    validation_exception_handler,
)
from app.http_client import create_http_client
from app.logging_config import configure_logging, get_logger
from app.middleware import include_middleware
from app.routers import include_routers
from app.stytch_client import cleanup_stytch_client
from custom_exceptions import DomainError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application lifespan events.

    Handles startup and shutdown tasks like closing async sessions.
    """
    # Startup
    logger = get_logger(__name__)
    logger.info("application_startup_started")

    # Initialize HTTP client and store in app state
    app.state.http_client = create_http_client()  # type: ignore[attr-defined]
    logger.info("http_client_initialized")
    logger.info("application_startup_complete")

    yield

    # Shutdown
    logger.info("application_shutdown_started")
    await app.state.http_client.aclose()  # type: ignore[attr-defined]
    logger.info("http_client_closed")
    await cleanup_stytch_client()
    logger.info("application_shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    # Initialize structured logging
    # Use JSON logs in production, colorful console logs in development
    settings = get_settings()
    configure_logging(json_logs=settings.json_logs, log_level=settings.log_level)

    logger = get_logger(__name__)
    logger.info(
        "application_starting",
        json_logs=settings.json_logs,
        log_level=settings.log_level,
        environment=settings.environment,
    )

    app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
    include_middleware(app)
    include_routers(app)
    app.add_exception_handler(DomainError, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    return app
