from fastapi import status

from custom_exceptions.base import DomainError


class DatabaseError(DomainError):
    """Exception raised for database operation failures."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error = "Database operation failed"

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        self.original_error = original_error
        super().__init__(message=message)

    def __repr__(self) -> str:
        """Return string representation of exception."""
        original_name = type(self.original_error).__name__ if self.original_error else "None"
        return f"<DatabaseError(message={self.message}, original={original_name})>"
