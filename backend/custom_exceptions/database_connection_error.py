from fastapi import status

from custom_exceptions.base import DomainError


class DatabaseConnectionError(DomainError):
    """Exception raised when database connection fails."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error = "Service temporarily unavailable"
    message = "Database connection failed"

    def __init__(self, message: str = "Database connection failed") -> None:
        super().__init__(message=message)

    def __repr__(self) -> str:
        """Return string representation of exception."""
        return f"<DatabaseConnectionError(message={self.message})>"
