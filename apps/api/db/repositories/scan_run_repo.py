"""
Concrete scan run repository (DIP — implements ScanRunRepository protocol).

SRP: This module is solely responsible for ScanRun persistence operations.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.scan_run import ScanRun


class SqlAlchemyScanRunRepository:
    """Concrete AsyncSession-backed scan run repo (DIP — implements ScanRunRepository protocol)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_org(
        self, org_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[ScanRun], int]:
        base = select(ScanRun).where(ScanRun.org_id == org_id)
        count_q = await self._db.execute(select(func.count()).select_from(base.subquery()))
        total = count_q.scalar_one()
        q = await self._db.execute(base.offset(offset).limit(limit).order_by(ScanRun.run_at.desc()))
        return list(q.scalars().all()), total

    async def get_by_id(
        self, scan_run_id: uuid.UUID, org_id: uuid.UUID
    ) -> ScanRun | None:
        result = await self._db.execute(
            select(ScanRun).where(ScanRun.id == scan_run_id, ScanRun.org_id == org_id)
        )
        return result.scalar_one_or_none()


# ── Legacy free-function API (backward compat) ──────────────────────────────

async def list_by_org(
    db: AsyncSession, org_id: uuid.UUID, offset: int = 0, limit: int = 20
) -> tuple[list[ScanRun], int]:
    return await SqlAlchemyScanRunRepository(db).list_by_org(org_id, offset, limit)


async def get_by_id(
    db: AsyncSession, scan_run_id: uuid.UUID, org_id: uuid.UUID
) -> ScanRun | None:
    return await SqlAlchemyScanRunRepository(db).get_by_id(scan_run_id, org_id)
