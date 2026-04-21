import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset


async def list_by_org(
    db: AsyncSession, org_id: uuid.UUID, offset: int = 0, limit: int = 20
) -> tuple[list[Asset], int]:
    count_q = await db.execute(select(func.count()).select_from(Asset).where(Asset.org_id == org_id))
    total = count_q.scalar_one()
    q = await db.execute(select(Asset).where(Asset.org_id == org_id).offset(offset).limit(limit))
    return list(q.scalars().all()), total


async def get_by_id(db: AsyncSession, asset_id: uuid.UUID, org_id: uuid.UUID) -> Asset | None:
    result = await db.execute(select(Asset).where(Asset.id == asset_id, Asset.org_id == org_id))
    return result.scalar_one_or_none()
