"""Query repository for database operations."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from models.query_model import QueryModel

logger = get_logger(__name__)


class QueryRepository:
    """Repository for query-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_query(
        self,
        session_id: int,
        query_text: str,
        response_text: str,
        input_mode: str = "text",
    ) -> QueryModel:
        """Create a new query/response pair.

        Args:
            session_id: The session's ID.
            query_text: The user's query text.
            response_text: The AI's response text.
            input_mode: 'text' or 'voice'.

        Returns:
            The created query model.
        """
        query = QueryModel(
            session_id=session_id,
            query_text=query_text,
            response_text=response_text,
            input_mode=input_mode,
        )
        self.db.add(query)
        await self.db.flush()
        await self.db.refresh(query)
        return query

    async def get_queries_by_session_id(
        self,
        session_id: int,
        limit: int | None = None,
    ) -> Sequence[QueryModel]:
        """Get queries for a session, ordered by creation time.

        Args:
            session_id: The session's ID.
            limit: Optional limit on number of queries to return.

        Returns:
            Sequence of query models.
        """
        query = (
            select(QueryModel)
            .where(QueryModel.session_id == session_id)
            .order_by(QueryModel.created_at.asc())
        )
        if limit:
            query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recent_queries_by_session_id(
        self,
        session_id: int,
        limit: int = 5,
    ) -> Sequence[QueryModel]:
        """Get the most recent queries for context in RAG.

        Args:
            session_id: The session's ID.
            limit: Maximum number of recent queries.

        Returns:
            Sequence of query models, ordered oldest to newest.
        """
        # Get most recent, then reverse for chronological context
        query = (
            select(QueryModel)
            .where(QueryModel.session_id == session_id)
            .order_by(QueryModel.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        queries = list(result.scalars().all())
        return list(reversed(queries))
