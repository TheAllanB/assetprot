import pytest
from sqlalchemy import text

from models.organization import Organization
from models.asset import Asset
from models.asset_fingerprint import AssetFingerprint
from models.violation import Violation
from models.dmca_notice import DMCANotice

@pytest.mark.asyncio
async def test_db_session_connects(db_session):
    result = await db_session.execute(text("SELECT 1"))
    row = result.scalar()
    assert row == 1

@pytest.mark.asyncio
async def test_create_organization(db_session):
    org = Organization(name="Test Sports Network", plan="pro")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    assert org.id is not None
    assert org.name == "Test Sports Network"

@pytest.mark.asyncio
async def test_create_asset(db_session):
    org = Organization(name="Sports Co", plan="free")
    db_session.add(org)
    await db_session.flush()
    asset = Asset(
        org_id=org.id,
        title="Championship Highlights",
        content_type="video",
        territories=["US", "GB"],
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    assert asset.id is not None
    assert asset.status == "pending"

@pytest.mark.asyncio
async def test_create_asset_fingerprint(db_session):
    org = Organization(name="Org", plan="free")
    db_session.add(org)
    await db_session.flush()
    asset = Asset(org_id=org.id, title="Match", content_type="video", territories=[])
    db_session.add(asset)
    await db_session.flush()
    fp = AssetFingerprint(asset_id=asset.id, phash="a" * 64, whash="b" * 64)
    db_session.add(fp)
    await db_session.commit()
    await db_session.refresh(fp)
    assert fp.asset_id == asset.id

@pytest.mark.asyncio
async def test_create_violation(db_session):
    org = Organization(name="Org2", plan="free")
    db_session.add(org)
    await db_session.flush()
    asset = Asset(org_id=org.id, title="Game", content_type="video", territories=[])
    db_session.add(asset)
    await db_session.flush()
    v = Violation(
        asset_id=asset.id,
        discovered_url="https://example.com/stolen",
        platform="youtube",
        confidence=0.95,
        infringement_type="exact_copy",
    )
    db_session.add(v)
    await db_session.commit()
    await db_session.refresh(v)
    assert v.status == "suspected"
