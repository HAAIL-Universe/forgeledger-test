"""Pydantic models for health check response schemas.

Defines the response models used by the /health and /health/version endpoints
to provide application status and version information.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for the /health endpoint.

    Indicates the overall application status and database connectivity.
    """

    status: str = Field(
        ...,
        description="Application status indicator",
        examples=["ok"],
    )
    database: str = Field(
        ...,
        description="Database connection status",
        examples=["connected"],
    )


class VersionResponse(BaseModel):
    """Response model for the /health/version endpoint.

    Returns application version and build metadata.
    """

    version: str = Field(
        ...,
        description="Application semantic version",
        examples=["0.1.0"],
    )
    build_date: str = Field(
        ...,
        description="ISO 8601 build date string",
        examples=["2024-01-01T00:00:00Z"],
    )
