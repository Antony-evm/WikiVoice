"""Tests for user service behavior - isolated unit tests."""

from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest


# Custom exception for testing
class UserNotFoundError(Exception):
    """Raised when a user is not found."""


# Minimal dataclass to represent user
@dataclass
class UserModel:
    """Mock user model for testing."""

    user_id: int = 0
    email: str = ""
    stytch_user_id: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    is_obsolete: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)


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
        user = await self.user_repository.get_user_by_stytch_id(stytch_user_id)
        if not user:
            raise UserNotFoundError(f"User with stytch_user_id {stytch_user_id} not found")
        return user

    async def get_user_by_id(self, user_id: int) -> UserModel:
        """Get a user by their user ID."""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with user_id {user_id} not found")
        return user


class TestUserServiceCreation:
    """Test user creation behavior."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repository):
        """Create a UserService with mocked dependencies."""
        return UserService(mock_user_repository)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,stytch_user_id",
        [
            ("user@example.com", "stytch-abc-123"),
            ("admin@company.org", "stytch-xyz-456"),
            ("test.user@domain.co.uk", "stytch-def-789"),
            ("user+tag@gmail.com", "stytch-ghi-012"),
            ("very.long.email.address@subdomain.example.com", "stytch-jkl-345"),
        ],
    )
    async def test_create_user_persists_and_returns_user(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        email: str,
        stytch_user_id: str,
    ):
        """When creating a user, system should persist and return the user model."""
        # Arrange
        mock_user = UserModel(
            user_id=1,
            email=email,
            stytch_user_id=stytch_user_id,
        )
        mock_user_repository.create_user.return_value = mock_user

        # Act
        result = await user_service.create_user(
            email=email,
            stytch_user_id=stytch_user_id,
        )

        # Assert
        assert result.email == email
        assert result.stytch_user_id == stytch_user_id
        mock_user_repository.create_user.assert_called_once()


class TestUserServiceRetrieval:
    """Test user retrieval behavior."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repository):
        """Create a UserService with mocked dependencies."""
        return UserService(mock_user_repository)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user model."""
        return UserModel(
            user_id=1,
            email="test@example.com",
            stytch_user_id="stytch-user-123",
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email,user_exists",
        [
            ("existing@example.com", True),
            ("nonexistent@example.com", False),
            ("user@company.org", True),
            ("unknown@domain.co", False),
        ],
    )
    async def test_get_user_by_email_handles_existing_and_missing(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        sample_user: UserModel,
        email: str,
        user_exists: bool,
    ):
        """When getting user by email, system should return user or None appropriately."""
        # Arrange
        if user_exists:
            sample_user.email = email
            mock_user_repository.get_user_by_email.return_value = sample_user
        else:
            mock_user_repository.get_user_by_email.return_value = None

        # Act
        result = await user_service.get_user_by_email(email)

        # Assert
        if user_exists:
            assert result is not None
            assert result.email == email
        else:
            assert result is None
        mock_user_repository.get_user_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "stytch_user_id",
        [
            "stytch-user-abc",
            "stytch-user-xyz",
            "stytch-user-123",
        ],
    )
    async def test_get_user_by_stytch_id_returns_user_when_found(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        sample_user: UserModel,
        stytch_user_id: str,
    ):
        """When getting user by Stytch ID, system should return user if found."""
        # Arrange
        sample_user.stytch_user_id = stytch_user_id
        mock_user_repository.get_user_by_stytch_id.return_value = sample_user

        # Act
        result = await user_service.get_user_by_stytch_user_id(stytch_user_id)

        # Assert
        assert result.stytch_user_id == stytch_user_id
        mock_user_repository.get_user_by_stytch_id.assert_called_once_with(stytch_user_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "stytch_user_id",
        [
            "nonexistent-stytch-1",
            "nonexistent-stytch-2",
            "invalid-id",
        ],
    )
    async def test_get_user_by_stytch_id_raises_when_not_found(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        stytch_user_id: str,
    ):
        """When getting user by Stytch ID that doesn't exist, system should raise error."""
        # Arrange
        mock_user_repository.get_user_by_stytch_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_by_stytch_user_id(stytch_user_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_id",
        [1, 2, 42, 100, 999],
    )
    async def test_get_user_by_id_returns_user_when_found(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        sample_user: UserModel,
        user_id: int,
    ):
        """When getting user by ID, system should return user if found."""
        # Arrange
        sample_user.user_id = user_id
        mock_user_repository.get_user_by_id.return_value = sample_user

        # Act
        result = await user_service.get_user_by_id(user_id)

        # Assert
        assert result.user_id == user_id
        mock_user_repository.get_user_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_id",
        [0, -1, 999999, 123456],
    )
    async def test_get_user_by_id_raises_when_not_found(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        user_id: int,
    ):
        """When getting user by ID that doesn't exist, system should raise error."""
        # Arrange
        mock_user_repository.get_user_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_by_id(user_id)
