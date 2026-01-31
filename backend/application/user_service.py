"""User service for user-related operations."""

from app.logging_config import get_logger
from custom_exceptions import UserNotFoundError
from domain.mappers import UserMapper
from infrastructure.user_repository import UserRepository
from models import UserModel

logger = get_logger(__name__)


class UserService:
    """Service for user-related operations."""

    def __init__(self, user_repository: UserRepository):
        """Initialize user service with dependencies.

        Args:
            user_repository: Repository for user data access.
        """
        self.user_repository = user_repository

    async def create_user(
        self,
        email: str,
        stytch_user_id: str,
    ) -> UserModel:
        """Create a new user in the database.

        Args:
            email: User's email address.
            stytch_user_id: User's Stytch ID.

        Returns:
            The created UserModel.
        """
        user_model = UserMapper.from_request(
            email=email,
            stytch_user_id=stytch_user_id,
        )
        return await self.user_repository.create_user(user_model)

    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Get a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The UserModel if found, None otherwise.
        """
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_stytch_user_id(self, stytch_user_id: str) -> UserModel:
        """Get a user by their Stytch user ID.

        Args:
            stytch_user_id: The Stytch user ID to search for.

        Returns:
            The UserModel.

        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.user_repository.get_user_by_stytch_id(stytch_user_id)
        if not user:
            msg = f"User with stytch_user_id {stytch_user_id} not found"
            raise UserNotFoundError(msg)
        return user

    async def get_user_by_id(self, user_id: int) -> UserModel:
        """Get a user by their user ID.

        Args:
            user_id: The user ID to search for.

        Returns:
            The UserModel.

        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            msg = f"User with user_id {user_id} not found"
            raise UserNotFoundError(msg)
        return user
