"""User domain entity."""


class User:
    """Domain entity representing a user."""

    def __init__(
        self,
        user_id: int,
        stytch_user_id: str,
        email: str,
    ):
        """Initialize user entity."""
        self._user_id = user_id
        self._email = email
        self._stytch_user_id = stytch_user_id

    @property
    def user_id(self) -> int:
        """Get the user ID."""
        return self._user_id

    @property
    def email(self) -> str:
        """Get the user email."""
        return self._email

    @property
    def stytch_user_id(self) -> str:
        """Get the Stytch user ID."""
        return self._stytch_user_id

    def __repr__(self) -> str:
        """Return string representation of user."""
        return f"<User(user_id={self.user_id}, email={self.email})>"
