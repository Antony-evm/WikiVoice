"""Session service for managing conversation sessions."""

from domain.responses.session_response import SessionResponse
from infrastructure.query_repository import QueryRepository
from infrastructure.session_repository import SessionRepository


class SessionService:
    """Service for session management operations."""

    def __init__(
        self,
        session_repository: SessionRepository,
        query_repository: QueryRepository,
    ):
        self.session_repository = session_repository
        self.query_repository = query_repository

    async def create_session(
        self, user_id: int, title: str = "New Conversation"
    ) -> SessionResponse:
        """Create a new session for a user.

        Args:
            user_id: The user's ID.
            title: Optional title for the session.

        Returns:
            Session response with session details.
        """
        session = await self.session_repository.create_session(user_id, title)
        return SessionResponse(
            session_id=session.session_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    async def get_session(self, session_id: int, user_id: int) -> SessionResponse | None:
        """Get a session by ID if it belongs to the user.

        Args:
            session_id: The session's ID.
            user_id: The user's ID for ownership verification.

        Returns:
            Session response if found and owned by user.
        """
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
        """Get paginated sessions for a user.

        Args:
            user_id: The user's ID.
            limit: Maximum number of sessions.
            offset: Number of sessions to skip.

        Returns:
            List of session responses.
        """
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
        """Update a session's title if owned by user.

        Args:
            session_id: The session's ID.
            user_id: The user's ID for ownership verification.
            title: The new title.

        Returns:
            Updated session response or None.
        """
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
        """Delete a session if owned by user.

        Args:
            session_id: The session's ID.
            user_id: The user's ID for ownership verification.

        Returns:
            True if deleted, False otherwise.
        """
        session = await self.session_repository.get_session_by_id(session_id)
        if session and session.user_id == user_id:
            return await self.session_repository.delete_session(session_id)
        return False
