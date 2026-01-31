"""User repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from models.user_model import UserModel

logger = get_logger(__name__)


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_model: UserModel) -> UserModel:
        """Create a new user in the database.

        Args:
            user_model: The user model to create.

        Returns:
            The created user model with ID populated.
        """
        self.db.add(user_model)
        await self.db.flush()
        await self.db.refresh(user_model)
        return user_model

    async def get_user_by_stytch_id(self, stytch_user_id: str) -> UserModel | None:
        """Get a user by their Stytch user ID.

        Args:
            stytch_user_id: The Stytch user ID.

        Returns:
            The user model if found, None otherwise.
        """
        query = select(UserModel).where(
            UserModel.stytch_user_id == stytch_user_id, UserModel.is_obsolete.is_(False)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Get a user by their email address.

        Args:
            email: The user's email address.

        Returns:
            The user model if found, None otherwise.
        """
        query = select(UserModel).where(UserModel.email == email, UserModel.is_obsolete.is_(False))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        """Get a user by their user ID.

        Args:
            user_id: The user's ID.

        Returns:
            The user model if found, None otherwise.
        """
        query = select(UserModel).where(
            UserModel.user_id == user_id, UserModel.is_obsolete.is_(False)
        )
        result = await self.db.execute(query)
        return result.scalars().first()
