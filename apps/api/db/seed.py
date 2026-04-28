import asyncio

from sqlalchemy import select

from core.config import settings
from core.security import hash_password
from db.base import Base
from db.session import engine, AsyncSessionLocal
from models.asset import Asset
from models.asset_fingerprint import AssetFingerprint
from models.organization import Organization
from models.user import User


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_demo_data():
    """Seed demo data for testing and development."""
    async with AsyncSessionLocal() as session:
        # Check if demo org already exists
        existing = await session.scalar(
            select(Organization).where(Organization.name == "Demo Sports League")
        )
        if existing:
            print("Demo data already exists, skipping seed")
            return

        # Create demo organization
        org = Organization(name="Demo Sports League", plan="pro")
        session.add(org)
        await session.flush()

        # Create demo user
        user = User(
            org_id=org.id,
            email="admin@demo.com",
            hashed_password=hash_password("demo123!"),
            is_active=True,
        )
        session.add(user)
        await session.flush()

        # Create demo assets with fingerprints
        demo_assets = [
            Asset(
                id="11111111-1111-1111-1111-111111111111",
                org_id=org.id,
                title="Champions League Final 2024 — Full Broadcast",
                content_type="video",
                territories=["US", "UK", "EU", "APAC"],
                status="protected",
                rights_metadata={"sport": "football", "teams": ["Real Madrid", "Dortmund"], "tags": ["champions league", "final"]},
            ),
            Asset(
                id="22222222-2222-2222-2222-222222222222",
                org_id=org.id,
                title="Top 10 Goals of the Season — Highlights Reel",
                content_type="video",
                territories=["US", "UK"],
                status="protected",
                rights_metadata={"sport": "football", "tags": ["goals", "highlights", "season"]},
            ),
            Asset(
                id="33333333-3333-3333-3333-333333333333",
                org_id=org.id,
                title="Press Conference — Post-Match Interview",
                content_type="video",
                territories=["US"],
                status="protected",
            ),
            Asset(
                id="44444444-4444-4444-4444-444444444444",
                org_id=org.id,
                title="Official Match Day Poster — Digital Art",
                content_type="image",
                territories=["US", "UK", "EU"],
                status="protected",
            ),
            Asset(
                id="55555555-5555-5555-5555-555555555555",
                org_id=org.id,
                title="Stadium Anthem — Official Audio",
                content_type="audio",
                territories=["US", "UK", "EU", "APAC"],
                status="protected",
            ),
        ]
        session.add_all(demo_assets)
        await session.flush()

        # Add fingerprints
        for asset in demo_assets:
            fp = AssetFingerprint(
                asset_id=asset.id,
                phash="abc123def456",
                whash="def456abc123",
                watermark_payload="DEMO0001",
            )
            session.add(fp)

        # Create demo violations
        from datetime import datetime, timezone, timedelta
        from models.violation import Violation

        now = datetime.now(timezone.utc)
        violations = [
            Violation(
                id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                org_id=org.id,
                asset_id=demo_assets[0].id,
                discovered_url="https://youtube.com/watch?v=pirated-cl-final",
                platform="YouTube",
                status="confirmed",
                confidence=0.96,
                infringement_type="exact_copy",
                transformation_types=["re_encoded"],
                estimated_reach=125000,
                detected_at=now - timedelta(hours=2),
            ),
            Violation(
                id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                org_id=org.id,
                asset_id=demo_assets[1].id,
                discovered_url="https://streamingsite.net/clips/top-goals-2024",
                platform="Custom",
                status="confirmed",
                confidence=0.89,
                infringement_type="re_encoded",
                transformation_types=["re_encoded", "watermark_removed"],
                estimated_reach=45000,
                detected_at=now - timedelta(hours=6),
            ),
            Violation(
                id="cccccccc-cccc-cccc-cccc-cccccccccccc",
                org_id=org.id,
                asset_id=demo_assets[0].id,
                discovered_url="https://reddit.com/r/soccer/comments/pirated_highlights",
                platform="reddit",
                status="suspected",
                confidence=0.78,
                infringement_type="partial_clip",
                transformation_types=["cropped", "re_encoded"],
                estimated_reach=18000,
                detected_at=now - timedelta(hours=12),
            ),
            Violation(
                id="dddddddd-dddd-dddd-dddd-dddddddddddd",
                org_id=org.id,
                asset_id=demo_assets[3].id,
                discovered_url="https://instagram.com/p/unauthorized_poster_repost",
                platform="instagram",
                status="suspected",
                confidence=0.72,
                infringement_type="exact_copy",
                transformation_types=[],
                estimated_reach=8500,
                detected_at=now - timedelta(days=1),
            ),
            Violation(
                id="eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
                org_id=org.id,
                asset_id=demo_assets[4].id,
                discovered_url="https://tiktok.com/@user/video/anthem_remix",
                platform="tiktok",
                status="suspected",
                confidence=0.65,
                infringement_type="audio_only",
                transformation_types=["remixed"],
                estimated_reach=32000,
                detected_at=now - timedelta(days=2),
            ),
        ]
        session.add_all(violations)
        await session.commit()
        print("Demo data seeded successfully (5 assets, 5 violations)")


async def main():
    await create_tables()
    if settings.app_env != "production":
        await seed_demo_data()


if __name__ == "__main__":
    asyncio.run(main())