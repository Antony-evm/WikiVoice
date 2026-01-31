"""Dependency injection for FastAPI endpoints."""

from dataclasses import dataclass

import httpx
from cachetools import TTLCache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.logging_config import get_logger
from application import AuthService, UserService
from custom_exceptions import UserNotFoundError
from infrastructure import UserRepository
from models.database import get_db

logger = get_logger(__name__)

_USER_CACHE_TTL = 900
_USER_CACHE_MAX_SIZE = 1000


@dataclass(frozen=True, slots=True)
class CachedUser:
    """Cached user data for auth lookups."""

    user_id: int


_user_cache: TTLCache[str, CachedUser] = TTLCache(maxsize=_USER_CACHE_MAX_SIZE, ttl=_USER_CACHE_TTL)


def invalidate_user_cache(stytch_user_id: str) -> None:
    """Remove a user from the cache (call on user deletion)."""
    _user_cache.pop(stytch_user_id, None)


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Get the shared HTTP client from app state."""
    return request.app.state.http_client  # type: ignore[attr-defined]


def init_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Initialize user repository with database session."""
    return UserRepository(db)


def init_user_service(
    user_repository: UserRepository = Depends(init_user_repository),
) -> UserService:
    """Initialize user service with user repository."""
    return UserService(user_repository)


def init_auth_service(
    user_service: UserService = Depends(init_user_service),
) -> AuthService:
    """Initialize authentication service with dependencies."""
    return AuthService(user_service)


async def get_current_user_id(
    request: Request, user_repository: UserRepository = Depends(init_user_repository)
) -> int:
    """Get the current authenticated user's internal database ID.

    Uses a TTL cache to avoid repeated database lookups.
    """
    stytch_user_id = request.state.user_id
    if cached := _user_cache.get(stytch_user_id):
        request.state.internal_user_id = cached.user_id
        return cached.user_id

    user_model = await user_repository.get_user_by_stytch_id(stytch_user_id)
    if not user_model:
        raise UserNotFoundError(stytch_user_id)
    assert user_model.user_id is not None
    request.state.internal_user_id = user_model.user_id
    _user_cache[stytch_user_id] = CachedUser(user_id=user_model.user_id)

    return user_model.user_id
