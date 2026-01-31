from fastapi import status

from custom_exceptions.base import DomainError


class InvalidSessionTokenError(DomainError):
    """Exception raised when the session token is invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error = "Invalid session token."
    message = "The session has expired, please log in again."

    def __repr__(self) -> str:
        """Return string representation of exception."""
        return "<InvalidSessionToken()>"
