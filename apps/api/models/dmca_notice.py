import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Uuid, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class DMCANotice(Base):
    __tablename__ = "dmca_notices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    violation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("violations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notice_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    # draft | sent | acknowledged | rejected
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    violation: Mapped["Violation"] = relationship("Violation", back_populates="dmca_notices")
