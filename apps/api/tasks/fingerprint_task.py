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
    async def _run():
        from qdrant_client import QdrantClient
        from transformers import CLIPModel, CLIPProcessor

        from services.fingerprint_service import FingerprintService

        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip_model.eval()
        qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

        engine, factory = _make_session()
        try:
            async with factory() as session:
                service = FingerprintService(
                    db=session,
                    qdrant=qdrant,
                    clip_model=clip_model,
                    clip_processor=clip_processor,
                )
                if content_type == "audio":
                    await service.process_audio(asset_id, file_path)
                else:
                    with open(file_path, "rb") as f:
                        image = Image.open(BytesIO(f.read())).convert("RGB")
                    await service.process(asset_id, image)
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
