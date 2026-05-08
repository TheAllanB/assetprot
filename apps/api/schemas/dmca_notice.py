import uuid
from datetime import datetime

from pydantic import BaseModel, FieldSerializer


class DMCANoticeResponse(BaseModel):
    id: uuid.UUID
    violation_id: uuid.UUID
    notice_text: str
    status: str
    sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @FieldSerializer("id", "violation_id")
    def serialize_uuid(self, v: uuid.UUID) -> str:
        return str(v)