"""Register user request model with password validation."""

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_MIN_LENGTH = 8


class RegisterUserRequest(BaseModel):
    """Request model for email/password user registration."""

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com", "john.doe@gmail.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password (min 8 chars, 1 uppercase, 1 lowercase, 1 number)",
        examples=["SecurePass123"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements.

        Requirements:
        - Minimum 8 characters (handled by Field min_length)
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError("Password must be at least 8 characters long")
        return v

    model_config = ConfigDict(
        extra="ignore",
        strict=False,
        json_schema_extra={
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "password": "SecurePass123",
                }
            ]
        },
    )
