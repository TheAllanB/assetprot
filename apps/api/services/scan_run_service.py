"""
Scan run service (SRP + DIP).

SRP: Orchestrates scan run business logic only.
DIP: Depends on ScanRunRepository protocol, not concrete repo.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.scan_run_repo import SqlAlchemyScanRunRepository
from models.scan_run import ScanRun


class ScanRunService:
    """
    Scan run business logic service.

    DIP: Accepts a ScanRunRepository protocol; defaults to SqlAlchemy impl.
    SRP: Only handles scan run retrieval/listing logic.
    """

    def __init__(self, db: AsyncSession, repo: SqlAlchemyScanRunRepository | None = None) -> None:
        self._repo = repo or SqlAlchemyScanRunRepository(db)

    async def list_scan_runs(
        self, org_id: uuid.UUID, offset: int, limit: int
    ) -> tuple[list[ScanRun], int]:
        return await self._repo.list_by_org(org_id, offset, limit)

    async def get_scan_run(
        self, scan_run_id: uuid.UUID, org_id: uuid.UUID
    ) -> ScanRun | None:
        return await self._repo.get_by_id(scan_run_id, org_id)


# ── Legacy free-function API (backward compat for existing routers) ──────────

async def list_scan_runs(db: AsyncSession, org_id: uuid.UUID, offset: int, limit: int):
    return await ScanRunService(db).list_scan_runs(org_id, offset, limit)


async def get_scan_run(db: AsyncSession, scan_run_id: uuid.UUID, org_id: uuid.UUID):
    return await ScanRunService(db).get_scan_run(scan_run_id, org_id)
