"""Query router for RAG query endpoints."""

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user_id, get_db
from api.error_responses import (
    INTERNAL_SERVER_ERROR_500,
    NOT_FOUND_404,
    UNAUTHORIZED_401,
    VALIDATION_ERROR_422,
)
from api.success_response import SuccessResponse
from api_requests.query_request import QueryRequest
from domain.responses.query_response import ConversationHistoryResponse, QueryResponse
from infrastructure.query_repository import QueryRepository
from infrastructure.rag_service import RAGService
from infrastructure.session_repository import SessionRepository
from infrastructure.wikipedia_client import WikipediaClient

router = APIRouter(prefix="/query")


def get_rag_service(db: AsyncSession = Depends(get_db)) -> RAGService:
    """Dependency to get RAG service."""
    session_repo = SessionRepository(db)
    query_repo = QueryRepository(db)
    http_client = httpx.AsyncClient(timeout=60.0)
    wikipedia_client = WikipediaClient(http_client)
    return RAGService(session_repo, query_repo, wikipedia_client, http_client)


@router.post(
    "",
    response_model=SuccessResponse[QueryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a query and get an AI response",
    description="""
    Submit a question to WikiVoice and receive an AI-generated response
    using Wikipedia as the knowledge source.

    **Input Modes:**
    - `text`: User typed the query
    - `voice`: User spoke the query (transcribed)

    **Query Validation:**
    - Minimum 1 character, maximum 2000 characters
    - Prompt injection attempts are blocked

    **Returns:**
    - AI-generated response based on Wikipedia content
    - List of Wikipedia sources used
    """,
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        422: VALIDATION_ERROR_422,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def submit_query(
    request: QueryRequest,
    user_id: int = Depends(get_current_user_id),
    rag_service: RAGService = Depends(get_rag_service),
) -> SuccessResponse[QueryResponse]:
    """Submit a query and get an AI response using Wikipedia RAG."""
    result = await rag_service.process_query(
        session_id=request.session_id,
        user_id=user_id,
        query_text=request.query_text,
        input_mode=request.input_mode,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    return SuccessResponse(data=result, message="Query processed successfully")


@router.get(
    "/history/{session_id}",
    response_model=SuccessResponse[ConversationHistoryResponse],
    summary="Get conversation history for a session",
    description="""
    Retrieve all queries and responses for a specific conversation session.

    **Returns:**
    - Session metadata (ID, title)
    - List of all query/response pairs in chronological order
    """,
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def get_conversation_history(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    rag_service: RAGService = Depends(get_rag_service),
) -> SuccessResponse[ConversationHistoryResponse]:
    """Get the conversation history for a session."""
    queries = await rag_service.get_conversation_history(session_id, user_id)
    if queries is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    return SuccessResponse(
        data=ConversationHistoryResponse(session_id=session_id, title="", queries=queries),
        message="History retrieved successfully",
    )
