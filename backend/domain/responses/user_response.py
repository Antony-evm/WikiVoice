from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    """Response model for user data."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
