"""FastAPI application factory for ForgeLedger Test.

Creates and configures the FastAPI application instance with CORS middleware,
router registration, startup/shutdown lifecycle events for the database
connection pool, and static file serving for the frontend build output.

This is the entry point referenced by uvicorn::

    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import close_pool, init_pool

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    On startup:
        - Load and validate application settings.
        - Configure logging level from settings.
        - Initialise the asyncpg database connection pool with retry logic.

    On shutdown:
        - Gracefully close the database connection pool.
    """
    settings = get_settings()

    # Configure root logger based on settings
    logging.basicConfig(
        level=settings.LOG_LEVEL.value,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )

    logger.info(
        "Starting ForgeLedger Test (environment=%s, log_level=%s)",
        settings.ENVIRONMENT.value,
        settings.LOG_LEVEL.value,
    )

    # Initialise database connection pool
    try:
        await init_pool(settings)
        logger.info("Database connection pool initialised.")
    except Exception:
        logger.exception("Failed to initialise database connection pool.")
        raise

    yield

    # Shutdown
    logger.info("Shutting down ForgeLedger Test …")
    await close_pool()
    logger.info("Shutdown complete.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create, configure, and return the FastAPI application instance.

    Returns:
        A fully configured ``FastAPI`` application ready to be served by
        uvicorn.
    """
    settings = get_settings()

    application = FastAPI(
        title="ForgeLedger Test",
        description="Lightweight financial ledger for tracking income and expenses.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------
    # CORS middleware
    # ------------------------------------------------------------------
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Request logging middleware
    # ------------------------------------------------------------------
    @application.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        """Log every incoming HTTP request with method, path, status, and duration."""
        start = time.monotonic()
        response: Response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000.0
        logger.info(
            "%s %s — %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    # ------------------------------------------------------------------
    # Global exception handler
    # ------------------------------------------------------------------
    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch any unhandled exceptions and return a generic 500 response.

        The full traceback is logged at ERROR level but never exposed to the
        client.
        """
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )

    # ------------------------------------------------------------------
    # Router registration
    # ------------------------------------------------------------------
    from app.routers.health import router as health_router

    # Health routes are registered without the API prefix so that
    # deployment health probes can hit /health directly.
    application.include_router(health_router)

    # ------------------------------------------------------------------
    # Static file serving (frontend build output)
    # ------------------------------------------------------------------
    # In production the Vite build output lives at web/dist/ relative to
    # the project root.  We serve it at "/" so that the SPA handles all
    # non-API routes.  This mount is added last so that API routes take
    # precedence.
    frontend_dist = Path(__file__).resolve().parent.parent.parent / "web" / "dist"
    if frontend_dist.is_dir():
        application.mount(
            "/",
            StaticFiles(directory=str(frontend_dist), html=True),
            name="frontend",
        )
        logger.info("Serving frontend static files from %s", frontend_dist)

    return application


# ---------------------------------------------------------------------------
# Module-level app instance used by uvicorn
# ---------------------------------------------------------------------------

app: FastAPI = create_app()
