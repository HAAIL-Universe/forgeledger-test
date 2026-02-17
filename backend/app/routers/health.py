"""Health check router for ForgeLedger Test.

Provides endpoints for application health verification and version
information. The /health endpoint verifies database connectivity,
while /health/version returns build metadata.

This module belongs to the presentation (router) layer and MUST NOT
contain business logic, SQL queries, or direct database access. It
delegates database health checks to the database module.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.database import check_database_health
from app.models.health import HealthResponse, VersionResponse

logger = logging.getLogger(__name__)

# Application version — single source of truth for the /health/version endpoint.
_APP_VERSION = "0.1.0"
_BUILD_DATE = "2024-01-01T00:00:00Z"

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description=(
        "Returns the overall application status and database connectivity. "
        "Useful for deployment health probes and uptime monitoring."
    ),
    responses={
        200: {"description": "Application is healthy and database is connected"},
        503: {"description": "Application is running but database is unreachable"},
    },
)
async def health_check() -> JSONResponse:
    """Check application and database health.

    Executes a lightweight query against the database connection pool
    and returns the connectivity status. Returns HTTP 200 when the
    database is reachable, or HTTP 503 when it is not.

    Returns:
        JSONResponse with status and database connectivity information.
    """
    db_health = await check_database_health()
    db_status = db_health.get("status", "disconnected")

    if db_status == "connected":
        logger.debug("Health check passed: database connected.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "database": "connected"},
        )

    error_detail = db_health.get("error", "Unknown error")
    logger.warning("Health check degraded: database disconnected — %s", error_detail)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "degraded", "database": "disconnected"},
    )


@router.get(
    "/health/version",
    response_model=VersionResponse,
    summary="Return application version and build information",
    description="Provides the current semantic version and build date of the running application.",
)
async def version() -> VersionResponse:
    """Return application version metadata.

    Returns:
        VersionResponse containing the semantic version string and
        ISO 8601 build date.
    """
    return VersionResponse(version=_APP_VERSION, build_date=_BUILD_DATE)
