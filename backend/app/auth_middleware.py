from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.constants import AUTH_EXCLUDED_PATHS, AuthConstants
from app.logging_config import get_logger, user_id_var
from app.stytch_client import authenticate_jwt
from custom_exceptions import InvalidSessionTokenError

logger = get_logger(__name__)


class StytchAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to authenticate requests using Stytch JWT tokens."""

    def __init__(self, app, excluded_paths: list | None = None):  # noqa: ANN001
        super().__init__(app)
        self.excluded_paths = AUTH_EXCLUDED_PATHS + (excluded_paths or [])

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        """Process request through authentication middleware."""
        if self._should_skip_auth(request):
            return await call_next(request)

        # Try to get token from cookie first, then fall back to header
        token = self._extract_token_from_cookie(request) or self._extract_bearer_token(request)
        if not token:
            exc = InvalidSessionTokenError(
                error="Authorization missing",
                message="Authorization cookie or header missing",
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict(),
                headers=exc.headers,
            )

        try:
            auth_response = authenticate_jwt(token)
        except InvalidSessionTokenError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict(),
                headers=exc.headers,
            )

        request.state.user_id = auth_response.stytch_user_id
        request.state.session_jwt = auth_response.session_jwt
        user_id_var.set(request.state.user_id)

        return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """Check if authentication should be skipped for this request."""
        return request.url.path in self.excluded_paths or request.method == "OPTIONS"

    def _extract_token_from_cookie(self, request: Request) -> str | None:
        """Extract JWT token from HTTP-only cookie."""
        return request.cookies.get("session_jwt")

    def _extract_bearer_token(self, request: Request) -> str | None:
        """Extract JWT token from Authorization header (legacy support)."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        parts = authorization.split(" ", 1)
        if len(parts) != AuthConstants.JWT_TOKEN_PARTS or parts[0].lower() != "bearer":
            return None

        return parts[1]
