"""
Fingerprint service (SRP + OCP + DIP).

SRP: Orchestrates fingerprinting — delegates to strategy implementations.
OCP: New content types (e.g., text, 3D models) added by registering new
     strategies, NOT by modifying this class.
DIP: Depends on FingerprintStrategy protocol, not concrete implementations.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset
from models.asset_fingerprint import AssetFingerprint

logger = logging.getLogger(__name__)


class ImageFingerprintStrategy:
    """
    Fingerprinting strategy for image content (LSP — substitutable for any FingerprintStrategy).

    SRP: Only handles image-specific fingerprinting (pHash, wHash, CLIP, watermark).
    """

    def __init__(self, qdrant, clip_model, clip_processor, collection: str) -> None:
        self._qdrant = qdrant
        self._clip_model = clip_model
        self._clip_processor = clip_processor
        self._collection = collection

    def supports(self, content_type: str) -> bool:
        return content_type in ("image", "video")

    async def fingerprint(self, asset_id: str, file_path: str, **kwargs: Any) -> dict:
        from ml.fingerprinting.clip_embed import compute_clip_embedding
        from ml.fingerprinting.perceptual_hash import compute_phash, compute_whash
        from ml.fingerprinting.watermark import embed_watermark
        from ml.qdrant_store import upsert_embedding

        image: Image.Image = kwargs["image"]
        org_id: str = kwargs.get("org_id", "")

        result: dict[str, Any] = {}
        result["phash"] = compute_phash(image)
        result["whash"] = compute_whash(image)

        embedding = compute_clip_embedding(image, self._clip_model, self._clip_processor)
        point_id = upsert_embedding(self._qdrant, self._collection, asset_id, org_id, embedding)
        result["embedding_vector_hash"] = point_id

        embed_watermark(image, asset_id)
        result["watermark_payload"] = asset_id.replace("-", "")[:8]

        return result


class AudioFingerprintStrategy:
    """
    Fingerprinting strategy for audio content (LSP — substitutable for any FingerprintStrategy).

    SRP: Only handles audio-specific fingerprinting (Chromaprint).
    """

    def supports(self, content_type: str) -> bool:
        return content_type == "audio"

    async def fingerprint(self, asset_id: str, file_path: str, **kwargs: Any) -> dict:
        from ml.fingerprinting.audio_fingerprint import compute_chromaprint

        chromaprint = compute_chromaprint(file_path)
        return {"chromaprint": chromaprint}


class FingerprintService:
    """
    Orchestrator that delegates to registered strategies (OCP).

    To add a new content type:
    1. Implement a class with `supports()` and `fingerprint()` methods
    2. Register it via `register_strategy()`
    No modification of this class required (OCP).
    """

    def __init__(self, db: AsyncSession, strategies: list | None = None) -> None:
        self._db = db
        self._strategies: list = strategies or []

    def register_strategy(self, strategy: Any) -> None:
        """Register a new fingerprinting strategy (OCP extension point)."""
        self._strategies.append(strategy)

    def _find_strategy(self, content_type: str) -> Any:
        """Find the first strategy that supports this content type."""
        for strategy in self._strategies:
            if strategy.supports(content_type):
                return strategy
        raise ValueError(f"No fingerprinting strategy registered for content type: {content_type}")

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

    async def process(self, asset_id: str, content_type: str, file_path: str, **kwargs: Any) -> None:
        """
        Process an asset through the appropriate fingerprinting strategy.

        OCP: New modalities handled by registering strategies, not modifying this method.
        """
        asset, fp = await self._get_or_create_fingerprint(asset_id)
        asset.status = "fingerprinting"
        await self._db.commit()

        try:
            strategy = self._find_strategy(content_type)
            result = await strategy.fingerprint(
                asset_id, file_path, org_id=str(asset.org_id), **kwargs
            )

            # Apply results to fingerprint record
            for key, value in result.items():
                if hasattr(fp, key):
                    setattr(fp, key, value)

            fp.fingerprinted_at = datetime.now(timezone.utc)
            asset.status = "protected"
            logger.info(f"Asset {asset_id} fingerprinted via {strategy.__class__.__name__}")

        except Exception as e:
            logger.error(f"Fingerprinting failed for {asset_id}: {e}")
            asset.status = "failed"

        await self._db.commit()
