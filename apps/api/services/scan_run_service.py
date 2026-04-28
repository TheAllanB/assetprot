import uuid

from sqlalchemy.ext.asyncio import AsyncSession

import db.repositories.scan_run_repo as scan_run_repo


async def list_scan_runs(db: AsyncSession, org_id: uuid.UUID, offset: int, limit: int):
    return await scan_run_repo.list_by_org(db, org_id, offset, limit)


async def get_scan_run(db: AsyncSession, scan_run_id: uuid.UUID, org_id: uuid.UUID):
    return await scan_run_repo.get_by_id(db, scan_run_id, org_id)
