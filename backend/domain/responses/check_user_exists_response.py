"""Check user exists response model."""

from pydantic import BaseModel, EmailStr


class CheckUserExistsResponse(BaseModel):
    """Response for checking if a user exists."""

    exists: bool
    email: EmailStr
