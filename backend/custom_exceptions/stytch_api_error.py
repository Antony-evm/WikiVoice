from fastapi import status

from custom_exceptions.base import DomainError


class StytchAPIError(DomainError):
    """Exception raised for Stytch API errors."""

    status_code = status.HTTP_502_BAD_GATEWAY
    message = "Unable to verify authentication. Please try again later."

    def __init__(
        self,
        error_type: str = "authentication",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ) -> None:
        self.error_type = error_type
        self.status_code = status_code  # type: ignore[assignment]
        super().__init__(error=f"Authentication service error: {error_type}")

    def __repr__(self) -> str:
        """Return string representation of StytchAPIError."""
        return f"<StytchAPIError(error_type={self.error_type})>"
