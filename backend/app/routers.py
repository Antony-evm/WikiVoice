from fastapi import FastAPI

from api import auth_router, health_router, query_router, session_router


def include_routers(app: FastAPI) -> None:
    """Register all API routers with the FastAPI application."""
    app.include_router(health_router, tags=["health"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(session_router, prefix="/api/v1", tags=["sessions"])
    app.include_router(query_router, prefix="/api/v1", tags=["query"])
