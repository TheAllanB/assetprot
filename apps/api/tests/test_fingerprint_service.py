import uuid
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from models.organization import Organization
from models.asset import Asset
from models.asset_fingerprint import AssetFingerprint


def _make_test_image() -> Image.Image:
    return Image.new("RGB", (256, 256), color=(100, 150, 200))


@pytest.mark.asyncio
async def test_process_image_asset_creates_fingerprint(db_session):
    from services.fingerprint_service import FingerprintService

    org = Organization(name="FP Org", plan="pro")
    db_session.add(org)
    await db_session.flush()
    asset = Asset(org_id=org.id, title="Test Image", content_type="image", territories=[])
    db_session.add(asset)
    await db_session.flush()
    fp = AssetFingerprint(asset_id=asset.id)
    db_session.add(fp)
    await db_session.commit()

    mock_qdrant = MagicMock()
    mock_qdrant.upsert = MagicMock()
    mock_qdrant.get_collections.return_value = MagicMock(collections=[])

    with (
        patch("services.fingerprint_service.compute_phash", return_value="abcd1234abcd1234"),
        patch("services.fingerprint_service.compute_whash", return_value="1234abcd1234abcd"),
        patch("services.fingerprint_service.compute_clip_embedding", return_value=[0.1] * 512),
        patch("services.fingerprint_service.embed_watermark", return_value=_make_test_image()),
        patch("services.fingerprint_service.upsert_embedding", return_value=str(uuid.uuid4())),
    ):
        service = FingerprintService(db=db_session, qdrant=mock_qdrant, clip_model=MagicMock(), clip_processor=MagicMock())
        await service.process(str(asset.id), _make_test_image())

    await db_session.refresh(asset)
    await db_session.refresh(fp)
    assert asset.status == "protected"
    assert fp.phash == "abcd1234abcd1234"
    assert fp.whash == "1234abcd1234abcd"
    assert fp.fingerprinted_at is not None
    assert fp.embedding_vector_hash is not None


@pytest.mark.asyncio
async def test_process_audio_asset_sets_chromaprint(db_session):
    from services.fingerprint_service import FingerprintService

    org = Organization(name="FP Org Audio", plan="pro")
    db_session.add(org)
    await db_session.flush()
    asset = Asset(org_id=org.id, title="Test Audio", content_type="audio", territories=[])
    db_session.add(asset)
    await db_session.flush()
    fp = AssetFingerprint(asset_id=asset.id)
    db_session.add(fp)
    await db_session.commit()

    with patch("services.fingerprint_service.compute_chromaprint", return_value=b"AQAAC0mk"):
        service = FingerprintService(db=db_session, qdrant=MagicMock(), clip_model=MagicMock(), clip_processor=MagicMock())
        await service.process_audio(str(asset.id), "/tmp/fake.mp3")

    await db_session.refresh(asset)
    await db_session.refresh(fp)
    assert fp.chromaprint == b"AQAAC0mk"
    assert asset.status == "protected"


@pytest.mark.asyncio
async def test_process_marks_asset_failed_on_error(db_session):
    from services.fingerprint_service import FingerprintService

    org = Organization(name="FP Org Fail", plan="pro")
    db_session.add(org)
    await db_session.flush()
    asset = Asset(org_id=org.id, title="Bad Image", content_type="image", territories=[])
    db_session.add(asset)
    await db_session.flush()
    fp = AssetFingerprint(asset_id=asset.id)
    db_session.add(fp)
    await db_session.commit()

    with patch("services.fingerprint_service.compute_phash", side_effect=RuntimeError("GPU out of memory")):
        service = FingerprintService(db=db_session, qdrant=MagicMock(), clip_model=MagicMock(), clip_processor=MagicMock())
        await service.process(str(asset.id), _make_test_image())

    await db_session.refresh(asset)
    assert asset.status == "failed"
