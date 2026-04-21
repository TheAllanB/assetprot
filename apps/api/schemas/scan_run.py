import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_serializer


class ScanRunResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    status: str
    violations_found: int
    errors: dict[str, Any] | None = None
    run_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id", "asset_id")
    def serialize_uuid(self, v: uuid.UUID) -> str:
        return str(v)
