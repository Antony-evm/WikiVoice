"""Session response model."""

from datetime import datetime

from pydantic import BaseModel


class SessionResponse(BaseModel):
    """Response model for session data."""

    session_id: int
    title: str
    created_at: datetime
    updated_at: datetime
