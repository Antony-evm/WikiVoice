"""Authentication service for handling user registration and login."""

from __future__ import annotations

from api_requests import CheckUserExistsRequest, LoginRequest, RegisterUserRequest
from app import stytch_client
from app.logging_config import get_logger
from application.user_service import UserService
from domain.responses import AuthResult, CheckUserExistsResponse, UserResponse

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations.

    Handles user registration and login via Stytch.
    """

    def __init__(self, user_service: UserService):
        """Initialize auth service with dependencies.

        Args:
            user_service: Service for user operations.
        """
        self.user_service = user_service

    async def register_user(
        self,
        request: RegisterUserRequest,
    ) -> AuthResult:
        """Register a new user with email and password.

        This method:
        1. Creates user in Stytch with password
        2. Creates user in our database
        3. Returns user data and session info

        Args:
            request: The registration request with email and password.

        Returns:
            AuthResult with user data and session info.
        """
        session_data = stytch_client.create_password_user(request.email, request.password)
        user_model = await self.user_service.create_user(
            email=request.email,
            stytch_user_id=session_data.stytch_user_id,
        )

        logger.info(
            "user_registered",
            user_id=user_model.user_id,
            stytch_user_id=session_data.stytch_user_id,
        )

        return AuthResult(
            user=UserResponse.model_validate(user_model),
            session=session_data,
        )

    async def check_user_exists(
        self,
        request: CheckUserExistsRequest,
    ) -> CheckUserExistsResponse:
        """Check if a user exists with the given email.

        Args:
            request: Request containing email to check.

        Returns:
            CheckUserExistsResponse indicating if user exists.
        """
        existing_user = await self.user_service.get_user_by_email(request.email)
        if existing_user:
            return CheckUserExistsResponse(
                exists=True,
                email=request.email,
            )

        return CheckUserExistsResponse(exists=False, email=request.email)

    async def login_user(
        self,
        request: LoginRequest,
    ) -> AuthResult:
        """Authenticate a user with email and password.

        This method:
        1. Authenticates with Stytch
        2. Looks up user in our database
        3. Returns user data and session info

        Args:
            request: The login request with email and password.

        Returns:
            AuthResult with user data and session info.
        """
        session_data = stytch_client.authenticate_password(request.email, request.password)
        user = await self.user_service.get_user_by_stytch_user_id(session_data.stytch_user_id)
        return AuthResult(user=UserResponse.model_validate(user), session=session_data)
