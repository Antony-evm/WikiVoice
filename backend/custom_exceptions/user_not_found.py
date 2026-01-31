from fastapi import status

from custom_exceptions.base import DomainError


class UserNotFoundError(DomainError):
    """Exception raised when a user is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    error = "Resource not found or access denied"
    message = "User does not exist. Please create an account before logging in."

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__()

    def __repr__(self) -> str:
        """Return string representation of exception."""
        return f"<UserNotFound(user_id={self.user_id})>"
