import logging

import stytch
from aiohttp import ClientSession, ClientTimeout
from stytch.consumer.models.users import GetResponse
from stytch.core.response_base import StytchError

from app.config import get_settings
from app.constants import AuthConstants
from custom_exceptions import InvalidSessionTokenError
from custom_exceptions.invalid_credentials_error import InvalidCredentialsError
from domain.responses.session_data import SessionData

logger = logging.getLogger(__name__)


class StytchClientManager:
    """Manages the Stytch client lifecycle and ensures proper cleanup."""

    def __init__(self) -> None:
        self._client: stytch.Client | None = None
        self._session: ClientSession | None = None

    def get_client(self) -> stytch.Client:
        """Get or create the Stytch client instance."""
        if self._client is None:
            settings = get_settings()
            timeout = ClientTimeout(total=10.0, connect=5.0, sock_read=10.0)
            self._session = ClientSession(timeout=timeout)
            self._client = stytch.Client(
                project_id=settings.stytch_project_id,
                secret=settings.stytch_secret,
                async_session=self._session,
            )
        return self._client

    async def cleanup(self) -> None:
        """Close the aiohttp ClientSession."""
        if self._session is not None:
            await self._session.close()
            logger.info("Closed Stytch client session")
            self._session = None
            self._client = None


_manager = StytchClientManager()


def get_stytch_client() -> stytch.Client:
    """Get the Stytch client instance."""
    return _manager.get_client()


async def cleanup_stytch_client() -> None:
    """Cleanup the Stytch client resources."""
    await _manager.cleanup()


def authenticate_jwt(session_jwt: str) -> SessionData:
    """Authenticate JWT token."""
    try:
        result = get_stytch_client().sessions.authenticate_jwt(session_jwt=session_jwt)
        return SessionData(
            session_jwt=result.session_jwt,
            session_token=result.session.session_id,
            stytch_user_id=result.session.user_id,
        )
    except StytchError as e:
        raise InvalidSessionTokenError from e


def get_stytch_user(stytch_user_id: str) -> GetResponse:
    """Get user information from Stytch by user ID."""
    return get_stytch_client().users.get(user_id=stytch_user_id)


def create_password_user(email: str, password: str) -> SessionData:
    """Create a new user with email/password in Stytch."""
    result = get_stytch_client().passwords.create(
        email=email,
        password=password,
        session_duration_minutes=AuthConstants.JWT_MAX_AGE_SECONDS // 60,
    )
    return SessionData(
        session_jwt=result.session_jwt,
        session_token=result.session_token,
        stytch_user_id=result.user_id,
    )


def authenticate_password(email: str, password: str) -> SessionData:
    """Authenticate a user with email and password."""
    try:
        result = get_stytch_client().passwords.authenticate(
            email=email,
            password=password,
            session_duration_minutes=AuthConstants.JWT_MAX_AGE_SECONDS // 60,
        )
        return SessionData(
            session_jwt=result.session_jwt,
            stytch_user_id=result.user_id,
            session_token=result.session.session_id,
        )
    except StytchError as e:
        raise InvalidCredentialsError from e


def delete_stytch_user(stytch_user_id: str) -> None:
    """Delete a user from Stytch by their Stytch user ID."""
    get_stytch_client().users.delete(user_id=stytch_user_id)
