"""Authentication router for WikiVoice."""

from fastapi import APIRouter, Depends, Response, status

from api.dependencies import init_auth_service
from api.error_responses import (
    INTERNAL_SERVER_ERROR_500,
    UNAUTHORIZED_401,
    USER_EXISTS_409,
    VALIDATION_ERROR_422,
)
from api.success_response import SuccessResponse
from api_requests import CheckUserExistsRequest, LoginRequest, RegisterUserRequest
from app.logging_config import get_logger
from application import AuthService
from domain.responses import CheckUserExistsResponse, UserResponse

logger = get_logger(__name__)

auth_router = APIRouter()


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponse[UserResponse],
    summary="Register a new user with email and password",
    description="""
    Register a new user account with email and password authentication.

    **Password Requirements:**
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number

    **Returns:**
    - User profile with ID and email
    - Session data in HTTP-only cookies
    """,
    responses={
        409: USER_EXISTS_409,
        422: VALIDATION_ERROR_422,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def register_user(
    response: Response,
    register_request: RegisterUserRequest,
    auth_service: AuthService = Depends(init_auth_service),
) -> SuccessResponse[UserResponse]:
    """Register a new user with email and password."""
    result = await auth_service.register_user(register_request)

    # Set HTTP-only cookies for auth tokens
    result.session.set_cookies(response)

    return SuccessResponse(data=result.user)


@auth_router.post(
    "/check-user",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[CheckUserExistsResponse],
    summary="Check if a user exists by email",
    description="""
    Check if a user account exists with the given email address.
    Used to determine whether to show login or register form.

    **Returns:**
    - `exists`: Boolean indicating if the email is registered
    - `email`: The email address that was checked
    """,
    responses={
        422: VALIDATION_ERROR_422,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def check_user_exists(
    check_request: CheckUserExistsRequest,
    auth_service: AuthService = Depends(init_auth_service),
) -> SuccessResponse[CheckUserExistsResponse]:
    """Check if a user exists by email."""
    result = await auth_service.check_user_exists(check_request)
    return SuccessResponse(data=result)


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[UserResponse],
    summary="Login with email and password",
    description="""
    Authenticate a user with their email address and password.

    **Returns:**
    - User profile with ID and email
    - Session data in HTTP-only cookies
    """,
    responses={
        401: UNAUTHORIZED_401,
        422: VALIDATION_ERROR_422,
        500: INTERNAL_SERVER_ERROR_500,
    },
)
async def login(
    response: Response,
    login_request: LoginRequest,
    auth_service: AuthService = Depends(init_auth_service),
) -> SuccessResponse[UserResponse]:
    """Login with email and password."""
    result = await auth_service.login_user(login_request)

    # Set HTTP-only cookies for auth tokens
    result.session.set_cookies(response)

    return SuccessResponse(data=result.user)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout and clear session cookies",
    description="Clears all authentication cookies to log out the user.",
)
async def logout(response: Response) -> SuccessResponse[dict]:
    """Clear authentication cookies."""
    # Clear all auth cookies
    response.delete_cookie(key="session_jwt", path="/")
    response.delete_cookie(key="session_token", path="/")
    response.delete_cookie(key="stytch_user_id", path="/")

    return SuccessResponse(data={"message": "Logged out successfully"})
