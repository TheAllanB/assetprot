"""
Concrete asset repository (DIP — implements AssetRepository protocol).

SRP: This module is solely responsible for Asset persistence operations.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset


class SqlAlchemyAssetRepository:
    """Concrete AsyncSession-backed asset repo (DIP — implements AssetRepository protocol)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_org(
        self, org_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Asset], int]:
        count_q = await self._db.execute(
            select(func.count()).select_from(Asset).where(Asset.org_id == org_id)
        )
        total = count_q.scalar_one()
        q = await self._db.execute(
            select(Asset).where(Asset.org_id == org_id).offset(offset).limit(limit)
        )
        return list(q.scalars().all()), total

    async def get_by_id(
        self, asset_id: uuid.UUID, org_id: uuid.UUID
    ) -> Asset | None:
        result = await self._db.execute(
            select(Asset).where(Asset.id == asset_id, Asset.org_id == org_id)
        )
        return result.scalar_one_or_none()


# ── Legacy free-function API (backward compat) ──────────────────────────────

async def list_by_org(
    db: AsyncSession, org_id: uuid.UUID, offset: int = 0, limit: int = 20
) -> tuple[list[Asset], int]:
    return await SqlAlchemyAssetRepository(db).list_by_org(org_id, offset, limit)


async def get_by_id(db: AsyncSession, asset_id: uuid.UUID, org_id: uuid.UUID) -> Asset | None:
    return await SqlAlchemyAssetRepository(db).get_by_id(asset_id, org_id)
