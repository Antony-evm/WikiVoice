"""Tests for auth service behavior - isolated unit tests."""

from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest


# Minimal dataclasses to represent domain objects
@dataclass
class UserModel:
    """Mock user model for testing."""

    user_id: int = 0
    email: str = ""
    stytch_user_id: str = ""
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)


@dataclass
class SessionData:
    """Data returned from Stytch authentication operations."""

    session_jwt: str
    session_token: str
    stytch_user_id: str


@dataclass
class UserResponse:
    """Response model for user data."""

    user_id: int
    email: str


@dataclass
class CheckUserExistsResponse:
    """Response model for check user exists."""

    exists: bool
    email: str


@dataclass
class AuthResult:
    """Result from authentication operations."""

    user: UserResponse
    session: SessionData


@dataclass
class RegisterUserRequest:
    """Request to register a user."""

    email: str
    password: str


@dataclass
class LoginRequest:
    """Request to login a user."""

    email: str
    password: str


@dataclass
class CheckUserExistsRequest:
    """Request to check if user exists."""

    email: str


class InvalidCredentialsError(Exception):
    """Raised when credentials are invalid."""


class UserService:
    """Service for user-related operations (test version)."""

    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def create_user(self, email: str, stytch_user_id: str) -> UserModel:
        """Create a new user in the database."""
        user_model = UserModel(email=email, stytch_user_id=stytch_user_id)
        return await self.user_repository.create_user(user_model)

    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Get a user by their email address."""
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_stytch_user_id(self, stytch_user_id: str) -> UserModel:
        """Get a user by their Stytch user ID."""
        return await self.user_repository.get_user_by_stytch_id(stytch_user_id)


class AuthService:
    """Service for authentication operations (test version)."""

    def __init__(self, user_service: UserService, stytch_client=None):
        self.user_service = user_service
        self.stytch_client = stytch_client

    async def register_user(self, request: RegisterUserRequest) -> AuthResult:
        """Register a new user with email and password."""
        session_data = self.stytch_client.create_password_user(request.email, request.password)
        user_model = await self.user_service.create_user(
            email=request.email,
            stytch_user_id=session_data.stytch_user_id,
        )
        return AuthResult(
            user=UserResponse(user_id=user_model.user_id, email=user_model.email),
            session=session_data,
        )

    async def check_user_exists(self, request: CheckUserExistsRequest) -> CheckUserExistsResponse:
        """Check if a user exists with the given email."""
        existing_user = await self.user_service.get_user_by_email(request.email)
        return CheckUserExistsResponse(
            exists=existing_user is not None,
            email=request.email,
        )

    async def login_user(self, request: LoginRequest) -> AuthResult:
        """Authenticate a user with email and password."""
        session_data = self.stytch_client.authenticate_password(request.email, request.password)
        user = await self.user_service.get_user_by_stytch_user_id(session_data.stytch_user_id)
        return AuthResult(
            user=UserResponse(user_id=user.user_id, email=user.email),
            session=session_data,
        )


class TestAuthServiceRegistration:
    """Test user registration behavior."""

    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_stytch_client(self):
        from unittest.mock import MagicMock

        return MagicMock()

    @pytest.fixture
    def auth_service(self, mock_user_repository, mock_stytch_client):
        user_service = UserService(mock_user_repository)
        return AuthService(user_service, mock_stytch_client)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,password",
        [
            ("user@example.com", "Password123"),
            ("admin@company.org", "SecurePass1"),
            ("test.user@domain.co.uk", "MyPassword1"),
            ("user+tag@gmail.com", "TestPass99"),
        ],
    )
    async def test_register_user_creates_user_and_returns_auth_result(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_stytch_client,
        email: str,
        password: str,
    ):
        """When registering, system should create user in Stytch and local DB, then return auth result."""
        # Arrange
        mock_session_data = SessionData(
            session_jwt="jwt-token",
            session_token="session-token",
            stytch_user_id="stytch-123",
        )

        mock_user = UserModel(
            user_id=1,
            email=email,
            stytch_user_id="stytch-123",
        )

        mock_stytch_client.create_password_user.return_value = mock_session_data
        mock_user_repository.create_user.return_value = mock_user

        request = RegisterUserRequest(email=email, password=password)

        # Act
        result = await auth_service.register_user(request)

        # Assert
        assert result.user.email == email
        assert result.user.user_id == 1
        assert result.session.session_jwt == "jwt-token"
        assert result.session.stytch_user_id == "stytch-123"
        mock_stytch_client.create_password_user.assert_called_once_with(email, password)
        mock_user_repository.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_propagates_stytch_errors(
        self,
        auth_service: AuthService,
        mock_stytch_client,
    ):
        """When Stytch fails to create user, system should propagate the error."""
        # Arrange
        mock_stytch_client.create_password_user.side_effect = Exception("Stytch API error")

        request = RegisterUserRequest(email="test@example.com", password="Password123")

        # Act & Assert
        with pytest.raises(Exception, match="Stytch API error"):
            await auth_service.register_user(request)


class TestAuthServiceLogin:
    """Test user login behavior."""

    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_stytch_client(self):
        from unittest.mock import MagicMock

        return MagicMock()

    @pytest.fixture
    def auth_service(self, mock_user_repository, mock_stytch_client):
        user_service = UserService(mock_user_repository)
        return AuthService(user_service, mock_stytch_client)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,password,stytch_user_id",
        [
            ("user@example.com", "Password123", "stytch-user-1"),
            ("admin@company.org", "SecurePass1", "stytch-user-2"),
            ("manager@test.com", "Manager99", "stytch-user-3"),
        ],
    )
    async def test_login_authenticates_and_returns_user(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_stytch_client,
        email: str,
        password: str,
        stytch_user_id: str,
    ):
        """When logging in with valid credentials, system should authenticate and return user data."""
        # Arrange
        mock_session_data = SessionData(
            session_jwt="jwt-token",
            session_token="session-token",
            stytch_user_id=stytch_user_id,
        )

        mock_user = UserModel(
            user_id=42,
            email=email,
            stytch_user_id=stytch_user_id,
        )

        mock_stytch_client.authenticate_password.return_value = mock_session_data
        mock_user_repository.get_user_by_stytch_id.return_value = mock_user

        request = LoginRequest(email=email, password=password)

        # Act
        result = await auth_service.login_user(request)

        # Assert
        assert result.user.email == email
        assert result.user.user_id == 42
        assert result.session.session_jwt == "jwt-token"
        mock_stytch_client.authenticate_password.assert_called_once_with(email, password)
        mock_user_repository.get_user_by_stytch_id.assert_called_once_with(stytch_user_id)

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials_raises_error(
        self,
        auth_service: AuthService,
        mock_stytch_client,
    ):
        """When credentials are invalid, system should propagate authentication error."""
        # Arrange
        mock_stytch_client.authenticate_password.side_effect = InvalidCredentialsError(
            "Invalid credentials"
        )

        request = LoginRequest(email="test@example.com", password="wrongpassword")

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(request)


class TestAuthServiceCheckUserExists:
    """Test checking if user exists behavior."""

    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_stytch_client(self):
        from unittest.mock import MagicMock

        return MagicMock()

    @pytest.fixture
    def auth_service(self, mock_user_repository, mock_stytch_client):
        user_service = UserService(mock_user_repository)
        return AuthService(user_service, mock_stytch_client)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,user_exists",
        [
            ("existing@example.com", True),
            ("new@example.com", False),
            ("another.existing@test.com", True),
            ("brand.new@company.org", False),
        ],
    )
    async def test_check_user_exists_returns_correct_status(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        email: str,
        user_exists: bool,
    ):
        """When checking if user exists, system should return correct status."""
        # Arrange
        if user_exists:
            sample_user = UserModel(user_id=1, email=email, stytch_user_id="stytch-123")
            mock_user_repository.get_user_by_email.return_value = sample_user
        else:
            mock_user_repository.get_user_by_email.return_value = None

        request = CheckUserExistsRequest(email=email)

        # Act
        result = await auth_service.check_user_exists(request)

        # Assert
        assert result.exists == user_exists
        assert result.email == email
        mock_user_repository.get_user_by_email.assert_called_once_with(email)
