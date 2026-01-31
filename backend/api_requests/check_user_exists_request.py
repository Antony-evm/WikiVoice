"""Check user exists request model."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CheckUserExistsRequest(BaseModel):
    """Request model for checking if a user exists by email."""

    email: EmailStr = Field(
        description="Email address to check",
        examples=["user@example.com"],
    )

    model_config = ConfigDict(
        extra="ignore",
        strict=False,
        json_schema_extra={
            "examples": [
                {
                    "email": "john.doe@example.com",
                }
            ]
        },
    )
