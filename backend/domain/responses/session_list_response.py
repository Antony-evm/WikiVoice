"""Session list response model."""

from pydantic import BaseModel

from .session_response import SessionResponse


class SessionListResponse(BaseModel):
    """Response containing list of sessions."""

    sessions: list[SessionResponse]
