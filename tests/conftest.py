"""
Pytest configuration and shared fixtures for ForgeLedger Test.

Provides database connection fixtures, test client setup, and common
test data factories for repository, service, and API integration tests.
"""

import asyncio
import os
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Event loop fixture for async tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure tests run with test environment settings."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    # Use a dummy DATABASE_URL so config doesn't fail if the var is missing
    if not os.environ.get("DATABASE_URL"):
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql://test:test@localhost:5432/forgeledger_test",
        )


# ---------------------------------------------------------------------------
# Sample data factories
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_category_income() -> dict:
    """Return a sample income category dict."""
    return {
        "id": str(uuid.uuid4()),
        "name": "Salary",
        "type": "income",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_category_expense() -> dict:
    """Return a sample expense category dict."""
    return {
        "id": str(uuid.uuid4()),
        "name": "Groceries",
        "type": "expense",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_transaction_income(sample_category_income: dict) -> dict:
    """Return a sample income transaction dict."""
    return {
        "id": str(uuid.uuid4()),
        "amount": "1500.00",
        "type": "income",
        "category_id": sample_category_income["id"],
        "date": date.today().isoformat(),
        "description": "Monthly salary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_transaction_expense(sample_category_expense: dict) -> dict:
    """Return a sample expense transaction dict."""
    return {
        "id": str(uuid.uuid4()),
        "amount": "52.30",
        "type": "expense",
        "category_id": sample_category_expense["id"],
        "date": date.today().isoformat(),
        "description": "Weekly groceries",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Mock repository fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_transaction_repository() -> MagicMock:
    """Provide a mock transaction repository for service-layer tests."""
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_category_repository() -> MagicMock:
    """Provide a mock category repository for service-layer tests."""
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.has_transactions = AsyncMock(return_value=False)
    return repo


# ---------------------------------------------------------------------------
# Mock database pool fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db_pool() -> MagicMock:
    """Provide a mock asyncpg connection pool."""
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire = MagicMock(return_value=conn)
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchrow = AsyncMock(return_value=None)
    conn.execute = AsyncMock(return_value="OK")
    return pool
