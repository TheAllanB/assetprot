import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_serializer


class AssetCreate(BaseModel):
    title: str
    content_type: str  # video | image | audio
    territories: list[str] = []
    rights_metadata: dict[str, Any] | None = None


class AssetResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    title: str
    content_type: str
    status: str
    territories: list[str]
    rights_metadata: dict[str, Any] | None = None
    blockchain_tx_hash: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id", "org_id")
    def serialize_uuid(self, v: uuid.UUID) -> str:
        return str(v)
