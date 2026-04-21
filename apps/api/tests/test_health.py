import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_returns_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] in ("ok", "degraded")
    assert "db" in data["data"]
    assert "redis" in data["data"]


@pytest.mark.asyncio
async def test_api_v1_prefix_exists():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/assets")
    assert r.status_code in (401, 403)  # protected — not 404
