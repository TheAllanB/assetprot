import uuid
from datetime import datetime, timezone

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ml.fingerprinting.audio_fingerprint import compute_chromaprint
from ml.fingerprinting.clip_embed import compute_clip_embedding
from ml.fingerprinting.perceptual_hash import compute_phash, compute_whash
from ml.fingerprinting.watermark import embed_watermark
from ml.qdrant_store import upsert_embedding
from models.asset import Asset
from models.asset_fingerprint import AssetFingerprint


class FingerprintService:
    def __init__(self, db: AsyncSession, qdrant, clip_model, clip_processor) -> None:
        self._db = db
        self._qdrant = qdrant
        self._clip_model = clip_model
        self._clip_processor = clip_processor

    async def _get_or_create_fingerprint(self, asset_id: str) -> tuple[Asset, AssetFingerprint]:
        asset = await self._db.get(Asset, uuid.UUID(asset_id))
        fp = await self._db.scalar(
            select(AssetFingerprint).where(AssetFingerprint.asset_id == uuid.UUID(asset_id))
        )
        if fp is None:
            fp = AssetFingerprint(asset_id=uuid.UUID(asset_id))
            self._db.add(fp)
            await self._db.flush()
        return asset, fp

    async def process(self, asset_id: str, image: Image.Image) -> None:
        asset, fp = await self._get_or_create_fingerprint(asset_id)
        asset.status = "fingerprinting"
        await self._db.commit()

        try:
            fp.phash = compute_phash(image)
            fp.whash = compute_whash(image)
            embedding = compute_clip_embedding(image, self._clip_model, self._clip_processor)
            point_id = upsert_embedding(
                self._qdrant,
                "asset_embeddings",
                asset_id=asset_id,
                org_id=str(asset.org_id),
                vector=embedding,
            )
            fp.embedding_vector_hash = point_id
            embed_watermark(image, asset_id)
            fp.watermark_payload = asset_id.replace("-", "")[:8]
            fp.fingerprinted_at = datetime.now(timezone.utc)
            asset.status = "protected"
        except Exception:
            asset.status = "failed"

        await self._db.commit()

    async def process_audio(self, asset_id: str, file_path: str) -> None:
        asset, fp = await self._get_or_create_fingerprint(asset_id)
        asset.status = "fingerprinting"
        await self._db.commit()

        try:
            fp.chromaprint = compute_chromaprint(file_path)
            fp.fingerprinted_at = datetime.now(timezone.utc)
            asset.status = "protected"
        except Exception:
            asset.status = "failed"

        await self._db.commit()
