"""Application configuration loaded from environment variables.

Uses Pydantic Settings to validate and provide typed access to all
configuration values required by the ForgeLedger Test backend.
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(str, Enum):
    """Valid deployment environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Valid logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Required variables:
        DATABASE_URL: PostgreSQL connection string (Neon). Must start with ``postgresql://``.
        ENVIRONMENT: Deployment environment (``development`` or ``production``).

    Optional variables have sensible defaults for local development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Required
    # ------------------------------------------------------------------
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string for Neon serverless database.",
    )
    ENVIRONMENT: EnvironmentType = Field(
        default=EnvironmentType.DEVELOPMENT,
        description="Deployment environment: development or production.",
    )

    # ------------------------------------------------------------------
    # Optional – Server / API
    # ------------------------------------------------------------------
    API_PORT: int = Field(
        default=8000,
        description="Port for the backend API server (uvicorn).",
    )
    API_PREFIX: str = Field(
        default="/api",
        description="Prefix for all API routes.",
    )

    # ------------------------------------------------------------------
    # Optional – CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins.",
    )

    # ------------------------------------------------------------------
    # Optional – Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="Application logging level.",
    )

    # ------------------------------------------------------------------
    # Optional – Database pool
    # ------------------------------------------------------------------
    DB_POOL_MIN_SIZE: int = Field(
        default=2,
        ge=1,
        description="Minimum number of connections in the asyncpg pool.",
    )
    DB_POOL_MAX_SIZE: int = Field(
        default=10,
        ge=1,
        description="Maximum number of connections in the asyncpg pool.",
    )

    # ------------------------------------------------------------------
    # Development only
    # ------------------------------------------------------------------
    RELOAD: bool = Field(
        default=True,
        description="Enable uvicorn auto-reload on file changes.",
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode with verbose error output.",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure the DATABASE_URL starts with a valid PostgreSQL scheme."""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must start with 'postgresql://' or 'postgres://'")
        return v

    @field_validator("API_PREFIX")
    @classmethod
    def validate_api_prefix(cls, v: str) -> str:
        """Ensure the API prefix starts with a forward slash and has no trailing slash."""
        if not v.startswith("/"):
            v = f"/{v}"
        return v.rstrip("/")

    # ------------------------------------------------------------------
    # Computed helpers
    # ------------------------------------------------------------------
    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list of strings."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Return ``True`` when running in development mode."""
        return self.ENVIRONMENT == EnvironmentType.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Return ``True`` when running in production mode."""
        return self.ENVIRONMENT == EnvironmentType.PRODUCTION


def get_settings() -> Settings:
    """Create and return a validated ``Settings`` instance.

    This function is intended to be used as a FastAPI dependency or called
    once at application startup. It reads from environment variables and
    an optional ``.env`` file in the working directory.

    Returns:
        A fully validated ``Settings`` object.

    Raises:
        pydantic.ValidationError: If required variables are missing or invalid.
    """
    return Settings()  # type: ignore[call-arg]
