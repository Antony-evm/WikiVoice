"""Base exception class for all domain exceptions."""

from typing import Any

from fastapi import status


class DomainError(Exception):
    """Base exception for all domain errors.

    Carries HTTP metadata for API layer, but is NOT an HTTPException.
    Can be used in CLI tools, workers, tests, etc.

    Subclasses should set class attributes:
        - status_code: HTTP status code (default: 500)
        - error: Short error description for API response
        - message: User-friendly message for API response
        - headers: Optional headers to include in response
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error: str = "Internal error"
    message: str = "An unexpected error occurred."
    headers: dict[str, str] | None = None

    def __init__(
        self,
        *,
        error: str | None = None,
        message: str | None = None,
        headers: dict[str, str] | None = None,
        **context: Any,
    ) -> None:
        """Initialize domain exception.

        Args:
            error: Override class-level error string
            message: Override class-level message string
            headers: Override class-level headers
            **context: Additional context to include in response
        """
        if error is not None:
            self.error = error
        if message is not None:
            self.message = message
        if headers is not None:
            self.headers = headers
        self.context = context
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to response payload."""
        result = {"error": self.error, "message": self.message}
        if self.context:
            result.update(self.context)
        return result
