from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from .base import Base


class SessionModel(Base):
    """SQLAlchemy model for conversation sessions."""

    __table_args__ = {"schema": "auth_service"}
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("auth_service.users.user_id"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), default="New Conversation", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_obsolete = Column(Boolean, default=False, nullable=False)
