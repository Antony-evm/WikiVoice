from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from .base import Base


class QueryModel(Base):
    """SQLAlchemy model for query/response pairs within a session."""

    __table_args__ = {"schema": "auth_service"}
    __tablename__ = "queries"

    query_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(
        Integer,
        ForeignKey("auth_service.sessions.session_id"),
        nullable=False,
        index=True,
    )
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    input_mode = Column(String(10), default="text", nullable=False)  # 'text' or 'voice'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
