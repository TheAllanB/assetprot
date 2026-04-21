from datetime import datetime, timezone
from uuid import uuid4

from schemas.base import APIResponse, PaginatedResponse
from schemas.auth import TokenResponse
from schemas.asset import AssetResponse
from schemas.violation import ViolationResponse


def test_api_response_success():
    r = APIResponse[dict](success=True, data={"foo": "bar"})
    assert r.success is True
    assert r.data == {"foo": "bar"}
    assert r.meta == {}


def test_api_response_error():
    r = APIResponse[None](success=False, data=None, error={"code": "NOT_FOUND", "message": "x"})
    assert r.success is False
    assert r.error["code"] == "NOT_FOUND"


def test_paginated_response():
    r = PaginatedResponse[dict](
        success=True,
        data=[{"id": "1"}],
        meta={"total": 1, "page": 1, "page_size": 20},
    )
    assert r.meta["total"] == 1


def test_token_response():
    t = TokenResponse(access_token="abc.def.ghi", refresh_token="xyz.abc.def")
    assert t.token_type == "bearer"


def test_asset_response_id_is_str():
    r = AssetResponse(
        id=uuid4(),
        org_id=uuid4(),
        title="Match Clip",
        content_type="video",
        status="pending",
        territories=["US"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert isinstance(r.model_dump()["id"], str)


def test_violation_response_serializes_uuids():
    r = ViolationResponse(
        id=uuid4(),
        asset_id=uuid4(),
        discovered_url="https://pirate.example/clip",
        platform="youtube",
        status="suspected",
        confidence=0.95,
        transformation_types=[],
        detected_at=datetime.now(timezone.utc),
    )
    dumped = r.model_dump()
    assert isinstance(dumped["id"], str)
    assert isinstance(dumped["asset_id"], str)
