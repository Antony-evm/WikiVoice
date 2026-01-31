from http import HTTPStatus

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.logging_config import get_logger
from custom_exceptions import DomainError

logger = get_logger(__name__)


def domain_exception_handler(request: Request, exc: DomainError) -> Response:
    """Handler for all domain exceptions.

    Converts DomainError subclasses to appropriate JSON responses.
    """
    if exc.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.error(
            "domain_exception",
            exc_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            **exc.context,
        )
    elif exc.status_code >= HTTPStatus.BAD_REQUEST:
        logger.warning(
            "domain_exception",
            exc_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            **exc.context,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers=exc.headers,
    )


def global_exception_handler(request: Request, exc: Exception) -> Response:
    """Global handler for all unhandled exceptions.

    Prevents stack traces from leaking to clients.
    Logs exception details securely without exposing sensitive data.
    """
    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,  # Will be filtered by limit_exception_traceback processor
    )

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    """Custom handler for Pydantic validation errors.

    Returns a consistent JSON response with formatted error details.
    """
    errors = exc.errors()

    # Format validation errors into a readable message
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{field}: {msg}")

    logger.warning(
        "validation_error",
        path=request.url.path,
        method=request.method,
        errors=errors,
    )

    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "message": "; ".join(error_messages),
            "details": errors,
        },
    )
