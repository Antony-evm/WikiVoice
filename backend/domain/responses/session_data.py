"""Session data response model for Stytch authentication."""

from fastapi import Response
from pydantic import BaseModel

from app.config import get_settings


class SessionData(BaseModel):
    """Data returned from Stytch authentication operations."""

    session_jwt: str
    session_token: str
    stytch_user_id: str

    def to_headers(self) -> dict[str, str]:
        """Convert session data to response headers (deprecated, use set_cookies)."""
        return {
            "X-Session-JWT": self.session_jwt,
            "X-Session-Token": self.session_token,
            "X-Stytch-User-ID": self.stytch_user_id,
        }

    def set_cookies(self, response: Response) -> None:
        """Set HTTP-only cookies for auth tokens."""
        settings = get_settings()
        is_production = settings.environment == "production"

        # For cross-origin requests (different CloudFront distributions),
        # we need samesite="none" with secure=True
        samesite_value = "none" if is_production else "lax"

        # Session JWT cookie - used for API authentication
        response.set_cookie(
            key="session_jwt",
            value=self.session_jwt,
            httponly=True,
            secure=is_production,
            samesite=samesite_value,
            max_age=60 * 60 * 24 * 7,  # 7 days
            path="/",
        )

        # Session token cookie - used for session refresh
        response.set_cookie(
            key="session_token",
            value=self.session_token,
            httponly=True,
            secure=is_production,
            samesite=samesite_value,
            max_age=60 * 60 * 24 * 7,  # 7 days
            path="/",
        )

        # Stytch user ID - not sensitive but useful for frontend
        response.set_cookie(
            key="stytch_user_id",
            value=self.stytch_user_id,
            httponly=False,  # Frontend needs to read this
            secure=is_production,
            samesite=samesite_value,
            max_age=60 * 60 * 24 * 7,  # 7 days
            path="/",
        )
