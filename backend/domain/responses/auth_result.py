"""Auth result response model."""

from pydantic import BaseModel

from .session_data import SessionData
from .user_response import UserResponse


class AuthResult(BaseModel):
    """Result from authentication operations (login/register)."""

    user: UserResponse
    session: SessionData
