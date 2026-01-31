"""Structured logging configuration using structlog.

This module configures structured logging with:
- JSON output for production environments
- Console-friendly output for development
- Automatic context binding (request_id, user_id)
- Sensitive data filtering to prevent secrets from leaking into logs
- Minimal traceback logging (type + message only in production)
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog
from structlog.types import EventDict, Processor

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "credential",
        "private_key",
        "access_token",
        "refresh_token",
        "database_url",
        "db_url",
        "connection_string",
        "stytch_secret",
        "pushy_secret_api_key",
        "admin_api_key",
        "scheduler_api_key",
        "revenuecat_webhook_auth_header",
    }
)


def _is_sensitive(key: str) -> bool:
    """Check if a key indicates sensitive data."""
    return key.lower().replace("-", "_") in SENSITIVE_KEYS


def _redact_value(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive values from log data."""
    if key and _is_sensitive(key):
        return "[REDACTED]"

    if isinstance(value, dict):
        return {k: _redact_value(v, k) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return type(value)(_redact_value(item) for item in value)
    return value


def redact_sensitive_data(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Processor to redact sensitive data from all log fields."""
    return {key: _redact_value(value, key) for key, value in event_dict.items()}


def add_request_context(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Add request_id and user_id to log events from context vars."""
    if request_id := request_id_var.get():
        event_dict["request_id"] = request_id
    if user_id := user_id_var.get():
        event_dict["user_id"] = user_id
    return event_dict


def format_exception_only(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Replace full traceback with just exception type and message.

    This prevents:
    - Huge logs from dependency injection chains
    - Local variables (with secrets) from appearing in logs
    - Log storage bloat
    """
    exc_info = event_dict.pop("exc_info", None)
    if not exc_info:
        return event_dict

    # Get actual exception info if exc_info=True
    if exc_info is True:
        exc_info = sys.exc_info()

    if exc_info and exc_info[0] is not None:
        exc_type, exc_value, _ = exc_info
        event_dict["error_type"] = exc_type.__name__
        event_dict["error_message"] = str(exc_value)

    return event_dict


def configure_logging(json_logs: bool = False, log_level: str = "INFO") -> None:
    """Configure structlog for the application.

    Args:
        json_logs: If True, output JSON logs (for production).
                   If False, output colorful console logs (for development).
        log_level: The minimum log level to output.
    """
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_request_context,
        format_exception_only,
        redact_sensitive_data,
    ]

    if json_logs:
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    for lib in ("uvicorn", "uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance bound to the given name."""
    return structlog.stdlib.get_logger(name)
