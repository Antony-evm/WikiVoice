from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from custom_exceptions.database_connection_error import DatabaseConnectionError

health_router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str


@health_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="""Check the API server health status.

    This endpoint provides a simple health check to verify that the API
    server is running and responsive. Used by monitoring systems, load
    balancers, and container orchestration platforms.

    **No Authentication Required**

    **Returns:**
    - Status object indicating server health

    **Use Cases:**
    - Kubernetes liveness/readiness probes
    - Load balancer health checks
    - Monitoring and alerting systems
    - Service status dashboards
    """,
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Health check endpoint that verifies database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return HealthResponse(status="healthy")
    except Exception as e:
        raise DatabaseConnectionError(str(e)) from e
