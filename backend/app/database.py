"""Database connection management for ForgeLedger Test.

Provides asyncpg connection pool lifecycle management, a dependency
for obtaining connections in request handlers, and a health check
function to verify database connectivity.

This module is the single source of truth for database connectivity.
All repository-layer code obtains connections through the ``get_connection``
async generator exposed here.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import asyncpg

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level pool reference
# ---------------------------------------------------------------------------
_pool: Optional[asyncpg.Pool] = None

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds, doubled each retry (exponential backoff)


async def init_pool(settings: Optional[Settings] = None) -> asyncpg.Pool:
    """Create and store the asyncpg connection pool.

    Implements retry logic with exponential backoff (3 attempts) as
    required by the blueprint's reliability section.

    Args:
        settings: Application settings. If ``None``, settings are loaded
            from the environment.

    Returns:
        The initialised ``asyncpg.Pool`` instance.

    Raises:
        asyncpg.PostgresError: If the database is unreachable after all
            retry attempts.
        Exception: Any unexpected error during pool creation.
    """
    global _pool

    if _pool is not None:
        return _pool

    if settings is None:
        settings = get_settings()

    dsn = settings.DATABASE_URL

    last_exc: Optional[BaseException] = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            logger.info(
                "Creating asyncpg connection pool (attempt %d/%d, min=%d, max=%d)",
                attempt,
                _MAX_RETRIES,
                settings.DB_POOL_MIN_SIZE,
                settings.DB_POOL_MAX_SIZE,
            )
            _pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=60,
                server_settings={"application_name": "forgeledger"},
            )
            logger.info("Database connection pool created successfully.")
            return _pool
        except (asyncpg.PostgresError, OSError, asyncio.TimeoutError) as exc:
            last_exc = exc
            if attempt < _MAX_RETRIES:
                delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Database connection attempt %d failed: %s. Retrying in %.1fs …",
                    attempt,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "Database connection failed after %d attempts: %s",
                    _MAX_RETRIES,
                    exc,
                )

    # All retries exhausted – re-raise the last exception.
    raise last_exc  # type: ignore[misc]


async def close_pool() -> None:
    """Gracefully close the connection pool.

    Safe to call even if the pool was never created or has already been
    closed.
    """
    global _pool

    if _pool is not None:
        logger.info("Closing database connection pool …")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")


def get_pool() -> asyncpg.Pool:
    """Return the current connection pool.

    Raises:
        RuntimeError: If the pool has not been initialised yet.
    """
    if _pool is None:
        raise RuntimeError(
            "Database connection pool is not initialised. "
            "Call 'init_pool()' during application startup."
        )
    return _pool


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency that yields a connection from the pool.

    Usage in a route::

        @router.get("/items")
        async def list_items(conn: asyncpg.Connection = Depends(get_connection)):
            ...

    The connection is automatically released back to the pool when the
    request finishes (even on error).
    """
    pool = get_pool()
    async with pool.acquire() as connection:
        yield connection


@asynccontextmanager
async def get_connection_ctx() -> AsyncGenerator[asyncpg.Connection, None]:
    """Context-manager variant for use outside of FastAPI dependency injection.

    Useful in service-layer code, scripts, or tests::

        async with get_connection_ctx() as conn:
            rows = await conn.fetch("SELECT 1")
    """
    pool = get_pool()
    async with pool.acquire() as connection:
        yield connection


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


async def check_database_health() -> dict[str, str]:
    """Verify that the database is reachable and responding.

    Executes a lightweight ``SELECT 1`` query against the pool.

    Returns:
        A dict with keys ``status`` (``"connected"`` or ``"disconnected"``)
        and optionally ``error`` with a human-readable message on failure.
    """
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                return {"status": "connected"}
            return {"status": "disconnected", "error": "Unexpected query result"}
    except RuntimeError as exc:
        # Pool not initialised
        return {"status": "disconnected", "error": str(exc)}
    except (asyncpg.PostgresError, OSError, asyncio.TimeoutError) as exc:
        logger.error("Database health check failed: %s", exc)
        return {"status": "disconnected", "error": str(exc)}
    except Exception as exc:
        logger.error("Unexpected error during database health check: %s", exc)
        return {"status": "disconnected", "error": "Internal error"}
