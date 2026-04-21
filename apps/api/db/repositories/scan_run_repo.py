import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset
from models.scan_run import ScanRun


async def list_by_org(
    db: AsyncSession, org_id: uuid.UUID, offset: int = 0, limit: int = 20
) -> tuple[list[ScanRun], int]:
    base = select(ScanRun).join(Asset, ScanRun.asset_id == Asset.id).where(Asset.org_id == org_id)
    count_q = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_q.scalar_one()
    q = await db.execute(base.offset(offset).limit(limit))
    return list(q.scalars().all()), total
