"""Session router for session management endpoints."""

import logging

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
from api_requests.session_request import CreateSessionRequest, UpdateSessionRequest
from application.session_service import SessionService
from domain.responses.session_list_response import SessionListResponse
from domain.responses.session_response import SessionResponse
from infrastructure.query_repository import QueryRepository
from infrastructure.session_repository import SessionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions")


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Dependency to get session service."""
    session_repo = SessionRepository(db)
    query_repo = QueryRepository(db)
    return SessionService(session_repo, query_repo)


@router.post(
    "",
    response_model=SuccessResponse[SessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation session",
    description="""
    Create a new conversation session for the authenticated user.

    **Default Title:**
    - "New Conversation" if no title provided
    - Title can be updated later or auto-generated from first query

    **Returns:**
    - Session ID, title, and timestamps
    """,
    responses={
        401: UNAUTHORIZED_401,
        422: VALIDATION_ERROR_422,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def create_session(
    request: CreateSessionRequest,
    user_id: int = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
) -> SuccessResponse[SessionResponse]:
    """Create a new conversation session."""
    logger.info(f"[SessionRouter] create_session called - user_id={user_id}, title={request.title}")
    session = await session_service.create_session(user_id, request.title)
    logger.info(f"[SessionRouter] Session created - session_id={session.session_id}")
    return SuccessResponse(data=session, message="Session created successfully")


@router.get(
    "",
    response_model=SuccessResponse[SessionListResponse],
    summary="List user's conversation sessions",
    description="""
    Retrieve a paginated list of the user's conversation sessions.

    **Pagination:**
    - `limit`: Maximum sessions to return (default: 5)
    - `offset`: Number of sessions to skip (default: 0)

    **Returns:**
    - List of session summaries ordered by most recent
    """,
    responses={
        401: UNAUTHORIZED_401,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def list_sessions(
    limit: int = 5,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
) -> SuccessResponse[SessionListResponse]:
    """List user's conversation sessions."""
    sessions = await session_service.get_user_sessions(user_id, limit, offset)
    return SuccessResponse(
        data=SessionListResponse(sessions=sessions),
        message="Sessions retrieved successfully",
    )


@router.get(
    "/{session_id}",
    response_model=SuccessResponse[SessionResponse],
    summary="Get a specific session",
    description="""
    Retrieve details for a specific conversation session.

    **Returns:**
    - Session ID, title, and timestamps
    """,
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def get_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
) -> SuccessResponse[SessionResponse]:
    """Get a specific session."""
    logger.info(f"[SessionRouter] get_session called - session_id={session_id}, user_id={user_id}")
    session = await session_service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return SuccessResponse(data=session, message="Session retrieved successfully")


@router.patch(
    "/{session_id}",
    response_model=SuccessResponse[SessionResponse],
    summary="Update a session's title",
    description="""
    Update the title of an existing conversation session.

    **Returns:**
    - Updated session with new title
    """,
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        422: VALIDATION_ERROR_422,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def update_session(
    session_id: int,
    request: UpdateSessionRequest,
    user_id: int = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
) -> SuccessResponse[SessionResponse]:
    """Update a session's title."""
    session = await session_service.update_session_title(session_id, user_id, request.title)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return SuccessResponse(data=session, message="Session updated successfully")


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="""
    Delete a conversation session and all its queries.

    **Note:** This action is irreversible.
    """,
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def delete_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    """Delete a session."""
    deleted = await session_service.delete_session(session_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
