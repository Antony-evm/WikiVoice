from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response wrapper for API responses."""

    data: T | None = Field(
        default=None,
        description=(
            "The data returned by the API call. This can be any type of data "
            "depending on the specific API endpoint."
        ),
    )
