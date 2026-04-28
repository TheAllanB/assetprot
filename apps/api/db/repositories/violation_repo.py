"""
Concrete violation repository (DIP — implements ViolationRepository protocol).

SRP: This module is solely responsible for Violation persistence operations.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset
from models.violation import Violation


class SqlAlchemyViolationRepository:
    """Concrete AsyncSession-backed violation repo (DIP — implements ViolationRepository protocol)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_org(
        self, org_id: uuid.UUID, offset: int = 0, limit: int = 20, asset_id: uuid.UUID | None = None
    ) -> tuple[list[Violation], int]:
        base = (
            select(Violation)
            .join(Asset, Violation.asset_id == Asset.id)
            .where(Asset.org_id == org_id)
        )
        if asset_id:
            base = base.where(Violation.asset_id == asset_id)
        count_q = await self._db.execute(select(func.count()).select_from(base.subquery()))
        total = count_q.scalar_one()
        q = await self._db.execute(base.offset(offset).limit(limit))
        return list(q.scalars().all()), total

    async def get_by_id(
        self, violation_id: uuid.UUID, org_id: uuid.UUID
    ) -> Violation | None:
        result = await self._db.execute(
            select(Violation)
            .join(Asset, Violation.asset_id == Asset.id)
            .where(Violation.id == violation_id, Asset.org_id == org_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        org_id: uuid.UUID,
        asset_id: uuid.UUID,
        discovered_url: str,
        platform: str,
        confidence: float,
        status: str = "suspected",
        infringement_type: str | None = None,
        estimated_reach: int | None = None,
        rights_territory_violation: bool = False,
    ) -> Violation:
        violation = Violation(
            org_id=org_id,
            asset_id=asset_id,
            discovered_url=discovered_url,
            platform=platform,
            confidence=confidence,
            status=status,
            infringement_type=infringement_type,
            estimated_reach=estimated_reach,
            rights_territory_violation=rights_territory_violation,
        )
        self._db.add(violation)
        await self._db.commit()
        await self._db.refresh(violation)
        return violation


# ── Legacy free-function API (backward compat) ──────────────────────────────

async def list_by_org(
    db: AsyncSession, org_id: uuid.UUID, offset: int = 0, limit: int = 20,
    asset_id: uuid.UUID | None = None,
) -> tuple[list[Violation], int]:
    return await SqlAlchemyViolationRepository(db).list_by_org(org_id, offset, limit, asset_id)


async def get_by_id(
    db: AsyncSession, violation_id: uuid.UUID, org_id: uuid.UUID
) -> Violation | None:
    return await SqlAlchemyViolationRepository(db).get_by_id(violation_id, org_id)


async def create(
    db: AsyncSession, org_id: uuid.UUID, asset_id: uuid.UUID,
    discovered_url: str, platform: str, confidence: float,
    status: str = "suspected", infringement_type: str | None = None,
    estimated_reach: int | None = None, rights_territory_violation: bool = False,
) -> Violation:
    return await SqlAlchemyViolationRepository(db).create(
        org_id, asset_id, discovered_url, platform, confidence,
        status, infringement_type, estimated_reach, rights_territory_violation,
    )