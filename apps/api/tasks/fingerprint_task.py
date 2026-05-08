"""
Celery fingerprint task (SRP + DIP).

SRP: This task only orchestrates the fingerprinting workflow.
DIP: Uses FingerprintService with injected strategies (OCP extension point).
"""

import asyncio
import os
from io import BytesIO

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from celery_app import celery_app
from core.config import settings


def _make_session() -> tuple:
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, factory


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def fingerprint_task(self, asset_id: str, file_path: str, content_type: str) -> dict:
    """
    Celery task for fingerprinting an asset.

    DIP: Creates FingerprintService with strategies injected —
    the service doesn't know about Celery, and the task doesn't
    know about fingerprinting algorithms.
    """
    async def _run():
        from qdrant_client import QdrantClient
        from transformers import CLIPModel, CLIPProcessor

        from services.fingerprint_service import (
            AudioFingerprintStrategy,
            FingerprintService,
            ImageFingerprintStrategy,
        )

        # Load models (SRP — model loading is separate from fingerprinting)
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip_model.eval()
        qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

        engine, factory = _make_session()
        try:
            async with factory() as session:
                # DIP: Inject strategies into the service
                image_strategy = ImageFingerprintStrategy(
                    qdrant=qdrant,
                    clip_model=clip_model,
                    clip_processor=clip_processor,
                    collection=settings.qdrant_collection,
                )
                audio_strategy = AudioFingerprintStrategy()

                service = FingerprintService(db=session, strategies=[image_strategy, audio_strategy])

                # Build kwargs based on content type
                kwargs = {}
                if content_type in ("image", "video"):
                    with open(file_path, "rb") as f:
                        kwargs["image"] = Image.open(BytesIO(f.read())).convert("RGB")

                await service.process(asset_id, content_type, file_path, **kwargs)
        finally:
            await engine.dispose()
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass

        return {"asset_id": asset_id, "status": "ok"}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc)
