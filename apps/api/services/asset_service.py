"""
Asset service (SRP + DIP).

SRP: Orchestrates asset business logic only.
DIP: Depends on AssetRepository protocol, not concrete repo.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.asset_repo import SqlAlchemyAssetRepository
from models.asset import Asset


class AssetService:
    """
    Asset business logic service.

    DIP: Accepts an AssetRepository protocol; defaults to SqlAlchemy impl.
    SRP: Only handles asset retrieval/listing logic.
    """

    def __init__(self, db: AsyncSession, repo: SqlAlchemyAssetRepository | None = None) -> None:
        self._repo = repo or SqlAlchemyAssetRepository(db)

    async def list_assets(
        self, org_id: uuid.UUID, offset: int, limit: int
    ) -> tuple[list[Asset], int]:
        return await self._repo.list_by_org(org_id, offset, limit)

    async def get_asset(
        self, asset_id: uuid.UUID, org_id: uuid.UUID
    ) -> Asset | None:
        return await self._repo.get_by_id(asset_id, org_id)


# ── Legacy free-function API (backward compat for existing routers) ──────────

async def list_assets(db: AsyncSession, org_id: uuid.UUID, offset: int, limit: int):
    return await AssetService(db).list_assets(org_id, offset, limit)


async def get_asset(db: AsyncSession, asset_id: uuid.UUID, org_id: uuid.UUID) -> Asset | None:
    return await AssetService(db).get_asset(asset_id, org_id)
