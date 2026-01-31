"""User mapper for converting between models and entities."""

from domain.entities.user import User
from models import UserModel


class UserMapper:
    """Mapper for converting user models, requests, and entities."""

    @staticmethod
    def from_request(
        email: str,
        stytch_user_id: str,
    ) -> UserModel:
        """Convert user creation request to database model.

        Args:
            email: User's email address.
            stytch_user_id: The Stytch user ID from the verified JWT token.

        Returns:
            UserModel ready for database insertion.
        """
        return UserModel(
            email=email,
            stytch_user_id=stytch_user_id,
        )

    @staticmethod
    def to_entity(user_model: UserModel) -> User:
        """Map a UserModel to a User entity."""
        return User(
            user_id=user_model.user_id,
            stytch_user_id=user_model.stytch_user_id,
            email=user_model.email,
        )
