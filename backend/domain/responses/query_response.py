"""Query response model."""

from datetime import datetime

from pydantic import BaseModel


class WikipediaSourceResponse(BaseModel):
    """A Wikipedia source used for the response."""

    title: str
    url: str


class QueryResponse(BaseModel):
    """Response model for a query/response pair."""

    query_id: int
    query_text: str
    response_text: str
    input_mode: str
    sources: list[WikipediaSourceResponse] = []
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Response containing session with its queries."""

    session_id: int
    title: str
    queries: list[QueryResponse]
