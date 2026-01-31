from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from .base import Base


class UserModel(Base):
    """SQLAlchemy model for user accounts."""

    __table_args__ = {"schema": "auth_service"}
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stytch_user_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_obsolete = Column(Boolean, default=False, nullable=False)
