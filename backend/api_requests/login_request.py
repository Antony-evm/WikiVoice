"""Login request model."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Request model for email/password login."""

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com", "john.doe@gmail.com"],
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        description="User's password",
        examples=["MySecurePassword123"],
    )

    model_config = ConfigDict(
        extra="ignore",
        strict=False,
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "MySecurePassword123",
                }
            ]
        },
    )
