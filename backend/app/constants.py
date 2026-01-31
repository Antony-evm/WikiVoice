"""Application-wide constants.

Centralizes magic numbers and constants to avoid scattered definitions
and improve maintainability.
"""


class AuthConstants:
    """Authentication and authorization related constants."""

    JWT_MAX_AGE_SECONDS = 86400 * 30  # 30 DAYS
    JWT_TOKEN_PARTS = 2


class PaginationConstants:
    """Pagination related constants."""

    DEFAULT_PAGE_SIZE = 10


PUBLIC_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/",
    "/api/v1/auth/register",
    "/api/v1/auth/check-user",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
]


AUTH_EXCLUDED_PATHS = PUBLIC_PATHS
