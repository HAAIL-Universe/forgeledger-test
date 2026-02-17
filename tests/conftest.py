"""Pytest fixtures for ForgeLedger Test backend test suite.

Provides:
- Async test database connection pool (isolated from production)
- HTTPX async client wired to the FastAPI test application
- Database cleanup between tests for isolation
- Test application instance with overridden settings

All fixtures use function scope by default to ensure test isolation.
Session-scoped fixtures are used for expensive resources like connection pools.
"""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, Generator

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Ensure test environment variables are set before any app imports
# ---------------------------------------------------------------------------
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DATABASE_URL", os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://localhost:5432/forgeledger_test",
))
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("DB_POOL_MIN_SIZE", "1")
os.environ.setdefault("DB_POOL_MAX_SIZE", "5")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("RELOAD", "false")


# ---------------------------------------------------------------------------
# Event loop fixture — session-scoped for asyncpg pool reuse
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a single event loop for the entire test session.

    This avoids re-creating the loop per test which can cause issues with
    session-scoped async fixtures like the database pool.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Database connection pool — session-scoped
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    """Create a session-scoped asyncpg connection pool for tests.

    The pool connects to the database specified by ``DATABASE_URL`` (or
    ``TEST_DATABASE_URL`` if set). It is created once for the entire test
    session and closed at teardown.

    Yields:
        An ``asyncpg.Pool`` instance ready for query execution.
    """
    database_url = os.environ.get(
        "TEST_DATABASE_URL",
        os.environ["DATABASE_URL"],
    )

    pool: asyncpg.Pool = await asyncpg.create_pool(
        dsn=database_url,
        min_size=1,
        max_size=5,
        command_timeout=30,
    )

    yield pool

    await pool.close()


# ---------------------------------------------------------------------------
# Database schema setup — session-scoped
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_test_schema(db_pool: asyncpg.Pool) -> AsyncGenerator[None, None]:
    """Ensure test database schema exists before running tests.

    Creates the ``categories`` and ``transactions`` tables if they do not
    already exist. This fixture runs once per session and is idempotent.
    """
    async with db_pool.acquire() as conn:
        # Create categories table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name        VARCHAR(100) NOT NULL UNIQUE,
                type        VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)

        # Create transactions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                amount      DECIMAL(10,2) NOT NULL CHECK (amount > 0),
                type        VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                category_id UUID REFERENCES categories(id) ON DELETE RESTRICT,
                date        DATE NOT NULL,
                description TEXT,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)

        # Create indexes (IF NOT EXISTS for idempotency)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_category_id
                ON transactions(category_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_type
                ON transactions(type);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_date
                ON transactions(date DESC);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_type_date
                ON transactions(type, date DESC);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_categories_type
                ON categories(type);
        """)

    yield


# ---------------------------------------------------------------------------
# Database cleanup — function-scoped
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(db_pool: asyncpg.Pool) -> AsyncGenerator[None, None]:
    """Clean all test data before and after each test for isolation.

    Truncates both ``transactions`` and ``categories`` tables using CASCADE
    to handle foreign key relationships.
    """
    async with db_pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE transactions CASCADE;")
        await conn.execute("TRUNCATE TABLE categories CASCADE;")

    yield

    async with db_pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE transactions CASCADE;")
        await conn.execute("TRUNCATE TABLE categories CASCADE;")


# ---------------------------------------------------------------------------
# Database connection — function-scoped
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_conn(db_pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """Provide a single database connection for a test function.

    Yields:
        An ``asyncpg.Connection`` acquired from the session pool.
    """
    async with db_pool.acquire() as conn:
        yield conn


# ---------------------------------------------------------------------------
# FastAPI test application
# ---------------------------------------------------------------------------


@pytest.fixture
def test_app():
    """Create a fresh FastAPI application instance for testing.

    Returns a new app from the factory. The app's lifespan events
    (database pool init/close) are managed separately via the ``db_pool``
    fixture. For integration tests that need the full app lifecycle,
    the ``async_client`` fixture should be used instead.
    """
    from app.main import create_app

    return create_app()


# ---------------------------------------------------------------------------
# HTTPX async client — function-scoped
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def async_client(test_app, db_pool: asyncpg.Pool) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX ``AsyncClient`` wired to the test FastAPI application.

    This client sends requests directly to the ASGI app without starting
    a real HTTP server. The database pool is initialised via the ``db_pool``
    fixture rather than the app lifespan to ensure test isolation.

    Yields:
        An ``httpx.AsyncClient`` configured with the test application
        as its transport.
    """
    # Inject the test database pool into the app's database module
    # so that repository code uses the test pool.
    import app.database as database_module

    original_pool = getattr(database_module, "_pool", None)
    database_module._pool = db_pool

    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        timeout=30.0,
    ) as client:
        yield client

    # Restore original pool reference
    database_module._pool = original_pool


# ---------------------------------------------------------------------------
# Helper fixtures for common test data
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def sample_category(db_pool: asyncpg.Pool) -> dict:
    """Create and return a sample expense category for use in tests.

    Returns:
        A dict with keys ``id``, ``name``, ``type``, and ``created_at``.
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO categories (name, type)
            VALUES ('Test Groceries', 'expense')
            RETURNING id, name, type, created_at;
        """)

    return {
        "id": str(row["id"]),
        "name": row["name"],
        "type": row["type"],
        "created_at": row["created_at"].isoformat(),
    }


@pytest_asyncio.fixture
async def sample_income_category(db_pool: asyncpg.Pool) -> dict:
    """Create and return a sample income category for use in tests.

    Returns:
        A dict with keys ``id``, ``name``, ``type``, and ``created_at``.
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO categories (name, type)
            VALUES ('Test Salary', 'income')
            RETURNING id, name, type, created_at;
        """)

    return {
        "id": str(row["id"]),
        "name": row["name"],
        "type": row["type"],
        "created_at": row["created_at"].isoformat(),
    }


@pytest_asyncio.fixture
async def sample_transaction(
    db_pool: asyncpg.Pool,
    sample_category: dict,
) -> dict:
    """Create and return a sample expense transaction for use in tests.

    Depends on ``sample_category`` to satisfy the foreign key constraint.

    Returns:
        A dict with keys ``id``, ``amount``, ``type``, ``category_id``,
        ``date``, ``description``, ``created_at``, and ``updated_at``.
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO transactions (amount, type, category_id, date, description)
            VALUES ($1, $2, $3::uuid, $4, $5)
            RETURNING id, amount, type, category_id, date, description,
                      created_at, updated_at;
            """,
            50.00,
            "expense",
            sample_category["id"],
            "2024-01-15",
            "Test grocery purchase",
        )

    return {
        "id": str(row["id"]),
        "amount": str(row["amount"]),
        "type": row["type"],
        "category_id": str(row["category_id"]),
        "date": row["date"].isoformat(),
        "description": row["description"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }
