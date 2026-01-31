"""Session request models."""

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""

    title: str = "New Conversation"


class UpdateSessionRequest(BaseModel):
    """Request to update a session."""

    title: str
