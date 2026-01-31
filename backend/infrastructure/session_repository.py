"""Session repository for database operations related to sessions."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from models.session_model import SessionModel

logger = get_logger(__name__)


class SessionRepository:
    """Repository for session-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: int, title: str = "New Conversation") -> SessionModel:
        """Create a new session for a user.

        Args:
            user_id: The user's ID.
            title: Optional title for the session.

        Returns:
            The created session model.
        """
        logger.info(f"[SessionRepo] Creating session - user_id={user_id}, title={title}")
        session = SessionModel(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        logger.info(f"[SessionRepo] Session created and flushed - session_id={session.session_id}")
        return session

    async def get_session_by_id(self, session_id: int) -> SessionModel | None:
        """Get a session by its ID.

        Args:
            session_id: The session's ID.

        Returns:
            The session model if found, None otherwise.
        """
        query = select(SessionModel).where(
            SessionModel.session_id == session_id,
            SessionModel.is_obsolete.is_(False),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_sessions_by_user_id(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[SessionModel]:
        """Get paginated sessions for a user.

        Args:
            user_id: The user's ID.
            limit: Maximum number of sessions to return.
            offset: Number of sessions to skip.

        Returns:
            Sequence of session models.
        """
        query = (
            select(SessionModel)
            .where(
                SessionModel.user_id == user_id,
                SessionModel.is_obsolete.is_(False),
            )
            .order_by(SessionModel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_sessions_by_user_id(self, user_id: int) -> int:
        """Count total sessions for a user.

        Args:
            user_id: The user's ID.

        Returns:
            Total number of sessions.
        """
        query = select(func.count(SessionModel.session_id)).where(
            SessionModel.user_id == user_id,
            SessionModel.is_obsolete.is_(False),
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update_session_title(self, session_id: int, title: str) -> SessionModel | None:
        """Update a session's title.

        Args:
            session_id: The session's ID.
            title: The new title.

        Returns:
            The updated session model if found.
        """
        session = await self.get_session_by_id(session_id)
        if session:
            session.title = title
            await self.db.flush()
            await self.db.refresh(session)
        return session

    async def delete_session(self, session_id: int) -> bool:
        """Soft-delete a session.

        Args:
            session_id: The session's ID.

        Returns:
            True if deleted, False if not found.
        """
        session = await self.get_session_by_id(session_id)
        if session:
            session.is_obsolete = True
            await self.db.flush()
            return True
        return False
