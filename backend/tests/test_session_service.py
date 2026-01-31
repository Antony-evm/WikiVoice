"""Tests for session service behavior - isolated unit tests."""

from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest


# Minimal dataclasses to represent domain objects
@dataclass
class SessionModel:
    """Mock session model for testing."""

    session_id: int = 0
    user_id: int = 0
    title: str = "New Conversation"
    created_at: datetime = None
    updated_at: datetime = None
    is_obsolete: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)


@dataclass
class SessionResponse:
    """Response model for session data."""

    session_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class SessionService:
    """Service for session management operations (test version)."""

    def __init__(self, session_repository, query_repository):
        self.session_repository = session_repository
        self.query_repository = query_repository

    async def create_session(
        self, user_id: int, title: str = "New Conversation"
    ) -> SessionResponse:
        """Create a new session for a user."""
        session = await self.session_repository.create_session(user_id, title)
        return SessionResponse(
            session_id=session.session_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    async def get_session(self, session_id: int, user_id: int) -> SessionResponse | None:
        """Get a session by ID if it belongs to the user."""
        session = await self.session_repository.get_session_by_id(session_id)
        if session and session.user_id == user_id:
            return SessionResponse(
                session_id=session.session_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
        return None

    async def get_user_sessions(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> list[SessionResponse]:
        """Get paginated sessions for a user."""
        sessions = await self.session_repository.get_sessions_by_user_id(user_id, limit, offset)
        return [
            SessionResponse(
                session_id=s.session_id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]

    async def update_session_title(
        self,
        session_id: int,
        user_id: int,
        title: str,
    ) -> SessionResponse | None:
        """Update a session's title if owned by user."""
        session = await self.session_repository.get_session_by_id(session_id)
        if session and session.user_id == user_id:
            updated = await self.session_repository.update_session_title(session_id, title)
            if updated:
                return SessionResponse(
                    session_id=updated.session_id,
                    title=updated.title,
                    created_at=updated.created_at,
                    updated_at=updated.updated_at,
                )
        return None

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        """Delete a session if owned by user."""
        session = await self.session_repository.get_session_by_id(session_id)
        if session and session.user_id == user_id:
            return await self.session_repository.delete_session(session_id)
        return False


class TestSessionServiceCreation:
    """Test session creation behavior."""

    @pytest.fixture
    def mock_session_repository(self):
        """Create a mock session repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        """Create a mock query repository."""
        return AsyncMock()

    @pytest.fixture
    def session_service(self, mock_session_repository, mock_query_repository):
        """Create a SessionService with mocked dependencies."""
        return SessionService(mock_session_repository, mock_query_repository)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_id,title,expected_title",
        [
            (1, "Research on AI", "Research on AI"),
            (2, "History Questions", "History Questions"),
            (1, "New Conversation", "New Conversation"),
            (99, "", ""),  # Empty title allowed
            (5, "Very Long Title " * 10, "Very Long Title " * 10),
        ],
    )
    async def test_create_session_returns_session_response(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
        user_id: int,
        title: str,
        expected_title: str,
    ):
        """When creating a session, system should return a proper session response."""
        # Arrange
        mock_session = SessionModel(
            session_id=42,
            user_id=user_id,
            title=expected_title,
        )
        mock_session_repository.create_session.return_value = mock_session

        # Act
        result = await session_service.create_session(user_id, title)

        # Assert
        assert result.session_id == 42
        assert result.title == expected_title
        assert result.created_at is not None
        mock_session_repository.create_session.assert_called_once_with(user_id, title)


class TestSessionServiceRetrieval:
    """Test session retrieval behavior."""

    @pytest.fixture
    def mock_session_repository(self):
        """Create a mock session repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        """Create a mock query repository."""
        return AsyncMock()

    @pytest.fixture
    def session_service(self, mock_session_repository, mock_query_repository):
        """Create a SessionService with mocked dependencies."""
        return SessionService(mock_session_repository, mock_query_repository)

    @pytest.fixture
    def sample_session(self):
        """Create a sample session model."""
        return SessionModel(session_id=1, user_id=1, title="Test Conversation")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "session_user_id,requesting_user_id,should_return_session",
        [
            (1, 1, True),  # User owns the session
            (1, 2, False),  # User doesn't own the session
            (5, 5, True),  # Another user owns their session
            (10, 1, False),  # Different user trying to access
        ],
    )
    async def test_get_session_respects_ownership(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
        sample_session: SessionModel,
        session_user_id: int,
        requesting_user_id: int,
        should_return_session: bool,
    ):
        """When getting a session, system should only return if user owns it."""
        # Arrange
        sample_session.user_id = session_user_id
        mock_session_repository.get_session_by_id.return_value = sample_session

        # Act
        result = await session_service.get_session(
            session_id=sample_session.session_id,
            user_id=requesting_user_id,
        )

        # Assert
        if should_return_session:
            assert result is not None
            assert result.session_id == sample_session.session_id
        else:
            assert result is None

    @pytest.mark.asyncio
    async def test_get_session_returns_none_for_nonexistent(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
    ):
        """When session doesn't exist, system should return None."""
        # Arrange
        mock_session_repository.get_session_by_id.return_value = None

        # Act
        result = await session_service.get_session(session_id=999, user_id=1)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "limit,offset,num_sessions",
        [
            (5, 0, 5),
            (10, 0, 3),
            (5, 5, 0),
            (1, 0, 1),
            (100, 0, 50),
        ],
    )
    async def test_get_user_sessions_with_pagination(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
        limit: int,
        offset: int,
        num_sessions: int,
    ):
        """When listing sessions, system should respect pagination parameters."""
        # Arrange
        mock_sessions = [
            SessionModel(session_id=i + 1, user_id=1, title=f"Session {i + 1}")
            for i in range(num_sessions)
        ]
        mock_session_repository.get_sessions_by_user_id.return_value = mock_sessions

        # Act
        result = await session_service.get_user_sessions(
            user_id=1,
            limit=limit,
            offset=offset,
        )

        # Assert
        assert len(result) == num_sessions
        mock_session_repository.get_sessions_by_user_id.assert_called_once_with(1, limit, offset)


class TestSessionServiceUpdate:
    """Test session update behavior."""

    @pytest.fixture
    def mock_session_repository(self):
        """Create a mock session repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        """Create a mock query repository."""
        return AsyncMock()

    @pytest.fixture
    def session_service(self, mock_session_repository, mock_query_repository):
        """Create a SessionService with mocked dependencies."""
        return SessionService(mock_session_repository, mock_query_repository)

    @pytest.fixture
    def sample_session(self):
        """Create a sample session model."""
        return SessionModel(session_id=1, user_id=1, title="Test Conversation")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "session_user_id,requesting_user_id,new_title,should_update",
        [
            (1, 1, "New Title", True),
            (1, 2, "Unauthorized Update", False),
            (5, 5, "My New Title", True),
            (10, 1, "Should Fail", False),
        ],
    )
    async def test_update_session_title_respects_ownership(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
        sample_session: SessionModel,
        session_user_id: int,
        requesting_user_id: int,
        new_title: str,
        should_update: bool,
    ):
        """When updating session title, system should only allow owner to update."""
        # Arrange
        sample_session.user_id = session_user_id
        mock_session_repository.get_session_by_id.return_value = sample_session

        updated_session = SessionModel(
            session_id=sample_session.session_id,
            user_id=session_user_id,
            title=new_title,
        )
        mock_session_repository.update_session_title.return_value = updated_session

        # Act
        result = await session_service.update_session_title(
            session_id=sample_session.session_id,
            user_id=requesting_user_id,
            title=new_title,
        )

        # Assert
        if should_update:
            assert result is not None
            assert result.title == new_title
            mock_session_repository.update_session_title.assert_called_once()
        else:
            assert result is None


class TestSessionServiceDeletion:
    """Test session deletion behavior."""

    @pytest.fixture
    def mock_session_repository(self):
        """Create a mock session repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_query_repository(self):
        """Create a mock query repository."""
        return AsyncMock()

    @pytest.fixture
    def session_service(self, mock_session_repository, mock_query_repository):
        """Create a SessionService with mocked dependencies."""
        return SessionService(mock_session_repository, mock_query_repository)

    @pytest.fixture
    def sample_session(self):
        """Create a sample session model."""
        return SessionModel(session_id=1, user_id=1, title="Test Conversation")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "session_user_id,requesting_user_id,should_delete",
        [
            (1, 1, True),
            (1, 2, False),
            (5, 5, True),
            (10, 1, False),
        ],
    )
    async def test_delete_session_respects_ownership(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
        sample_session: SessionModel,
        session_user_id: int,
        requesting_user_id: int,
        should_delete: bool,
    ):
        """When deleting session, system should only allow owner to delete."""
        # Arrange
        sample_session.user_id = session_user_id
        mock_session_repository.get_session_by_id.return_value = sample_session
        mock_session_repository.delete_session.return_value = True

        # Act
        result = await session_service.delete_session(
            session_id=sample_session.session_id,
            user_id=requesting_user_id,
        )

        # Assert
        assert result == should_delete
        if should_delete:
            mock_session_repository.delete_session.assert_called_once()
        else:
            mock_session_repository.delete_session.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session_returns_false(
        self,
        session_service: SessionService,
        mock_session_repository: AsyncMock,
    ):
        """When deleting nonexistent session, system should return False."""
        # Arrange
        mock_session_repository.get_session_by_id.return_value = None

        # Act
        result = await session_service.delete_session(session_id=999, user_id=1)

        # Assert
        assert result is False
        mock_session_repository.delete_session.assert_not_called()
