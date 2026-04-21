import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_serializer


class ViolationVerdict(BaseModel):
    infringement_type: Literal["exact_copy", "re_encoded", "partial_clip", "audio_only", "false_positive"]
    confidence: float
    transformation_type: list[str]
    platform: str
    estimated_reach: int | None = None
    rights_territory_violation: bool
    reasoning: str


class ViolationResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    discovered_url: str
    platform: str
    status: str
    confidence: float
    infringement_type: str | None = None
    transformation_types: list[str]
    estimated_reach: int | None = None
    triage_verdict: dict[str, Any] | None = None
    detected_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}

    @field_serializer("id", "asset_id")
    def serialize_uuid(self, v: uuid.UUID) -> str:
        return str(v)
