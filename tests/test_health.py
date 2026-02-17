"""Integration tests for the /health endpoint.

Verifies:
- HTTP 200 status when database is connected
- Response schema matches ``{"status": "ok", "database": "connected"}``
- HTTP 503 when database is unreachable (simulated)
- /health/version returns version metadata
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200_when_db_connected(async_client: AsyncClient) -> None:
    """GET /health should return 200 with status ok and database connected."""
    response = await async_client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


@pytest.mark.asyncio
async def test_health_endpoint_response_schema(async_client: AsyncClient) -> None:
    """GET /health response must contain exactly the expected keys."""
    response = await async_client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert set(body.keys()) == {"status", "database"}
    assert isinstance(body["status"], str)
    assert isinstance(body["database"], str)


@pytest.mark.asyncio
async def test_health_endpoint_returns_json_content_type(async_client: AsyncClient) -> None:
    """GET /health should return application/json content type."""
    response = await async_client.get("/health")

    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_health_endpoint_returns_503_when_db_disconnected(async_client: AsyncClient) -> None:
    """GET /health should return 503 when database health check fails."""
    mock_health = AsyncMock(return_value={"status": "disconnected", "error": "Connection refused"})

    with patch("app.routers.health.check_database_health", mock_health):
        response = await async_client.get("/health")

    assert response.status_code == 503

    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "disconnected"


@pytest.mark.asyncio
async def test_health_endpoint_returns_503_when_db_status_unknown(async_client: AsyncClient) -> None:
    """GET /health should return 503 when database returns unexpected status."""
    mock_health = AsyncMock(return_value={"status": "unknown"})

    with patch("app.routers.health.check_database_health", mock_health):
        response = await async_client.get("/health")

    assert response.status_code == 503

    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "disconnected"


@pytest.mark.asyncio
async def test_health_endpoint_returns_503_when_db_returns_empty(async_client: AsyncClient) -> None:
    """GET /health should return 503 when database health check returns empty dict."""
    mock_health = AsyncMock(return_value={})

    with patch("app.routers.health.check_database_health", mock_health):
        response = await async_client.get("/health")

    assert response.status_code == 503

    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "disconnected"


@pytest.mark.asyncio
async def test_health_version_endpoint(async_client: AsyncClient) -> None:
    """GET /health/version should return version and build_date."""
    response = await async_client.get("/health/version")

    assert response.status_code == 200

    body = response.json()
    assert "version" in body
    assert "build_date" in body
    assert isinstance(body["version"], str)
    assert isinstance(body["build_date"], str)


@pytest.mark.asyncio
async def test_health_version_returns_semver_format(async_client: AsyncClient) -> None:
    """GET /health/version should return a version string in semver-like format."""
    response = await async_client.get("/health/version")

    assert response.status_code == 200

    body = response.json()
    version_parts = body["version"].split(".")
    assert len(version_parts) == 3, f"Expected semver format x.y.z, got {body['version']}"
    for part in version_parts:
        assert part.isdigit(), f"Version part '{part}' is not numeric"


@pytest.mark.asyncio
async def test_health_database_connectivity_verified(
    async_client: AsyncClient,
    db_pool,
) -> None:
    """GET /health should confirm actual database connectivity via the test pool.

    This test validates that the health endpoint performs a real database
    check and the test database pool is properly wired into the application.
    """
    # First verify the pool is actually connected
    async with db_pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        assert result == 1

    # Then verify the health endpoint reflects this
    response = await async_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["database"] == "connected"


@pytest.mark.asyncio
async def test_health_endpoint_is_idempotent(async_client: AsyncClient) -> None:
    """Multiple GET /health calls should return consistent results."""
    responses = []
    for _ in range(3):
        response = await async_client.get("/health")
        responses.append(response)

    for resp in responses:
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["database"] == "connected"
