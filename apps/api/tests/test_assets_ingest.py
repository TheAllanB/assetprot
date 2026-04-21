import io
import pytest
from unittest.mock import patch


REGISTER_PAYLOAD = {
    "org_name": "Ingest Org",
    "email": "ingest@sportsnet.com",
    "password": "securepass123",
}


@pytest.mark.asyncio
async def test_ingest_image_returns_task_id(client):
    reg = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    token = reg.json()["data"]["access_token"]

    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    fake_image.name = "test.png"

    with patch("routers.assets.fingerprint_task.delay") as mock_task:
        mock_task.return_value.id = "celery-task-uuid-123"
        resp = await client.post(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.png", fake_image, "image/png")},
            data={"title": "Championship Clip", "content_type": "image", "territories": '["US","GB"]'},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "asset_id" in body["data"]
    assert body["data"]["task_id"] == "celery-task-uuid-123"
    assert body["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_ingest_requires_auth(client):
    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    resp = await client.post(
        "/api/v1/assets",
        files={"file": ("test.png", fake_image, "image/png")},
        data={"title": "Clip", "content_type": "image", "territories": '[]'},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ingest_creates_asset_record(client):
    reg = await client.post(
        "/auth/register",
        json={"org_name": "Record Org", "email": "record@sportsnet.com", "password": "securepass123"},
    )
    token = reg.json()["data"]["access_token"]

    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    with patch("routers.assets.fingerprint_task.delay") as mock_task:
        mock_task.return_value.id = "task-abc"
        resp = await client.post(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("clip.png", fake_image, "image/png")},
            data={"title": "My Clip", "content_type": "image", "territories": '["US"]'},
        )
    asset_id = resp.json()["data"]["asset_id"]

    list_resp = await client.get("/api/v1/assets", headers={"Authorization": f"Bearer {token}"})
    asset_ids = [a["id"] for a in list_resp.json()["data"]]
    assert asset_id in asset_ids
