import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Uuid, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class AssetFingerprint(Base):
    __tablename__ = "asset_fingerprints"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True
    )
    phash: Mapped[str | None] = mapped_column(String(256), nullable=True)
    whash: Mapped[str | None] = mapped_column(String(256), nullable=True)
    chromaprint: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    watermark_payload: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embedding_vector_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fingerprinted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="fingerprint")
