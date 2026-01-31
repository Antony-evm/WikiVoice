"""Invalid credentials error."""

from custom_exceptions.base import DomainError


class InvalidCredentialsError(DomainError):
    """Raised when email/password authentication fails."""

    def __init__(self) -> None:
        """Initialize invalid credentials error."""
        super().__init__(
            message="Invalid email or password",
            error_code="invalid_credentials",
        )
