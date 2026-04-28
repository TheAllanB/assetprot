"""
Violation service (SRP + DIP).

SRP: Orchestrates violation business logic only.
DIP: Depends on ViolationRepository protocol, not concrete repo.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.violation_repo import SqlAlchemyViolationRepository
from models.violation import Violation


class ViolationService:
    """
    Violation business logic service.

    DIP: Accepts a ViolationRepository protocol; defaults to SqlAlchemy impl.
    SRP: Only handles violation retrieval/listing logic.
    """

    def __init__(self, db: AsyncSession, repo: SqlAlchemyViolationRepository | None = None) -> None:
        self._repo = repo or SqlAlchemyViolationRepository(db)

    async def list_violations(
        self, org_id: uuid.UUID, offset: int, limit: int, asset_id: uuid.UUID | None = None
    ) -> tuple[list[Violation], int]:
        return await self._repo.list_by_org(org_id, offset, limit, asset_id)

    async def get_violation(
        self, violation_id: uuid.UUID, org_id: uuid.UUID
    ) -> Violation | None:
        return await self._repo.get_by_id(violation_id, org_id)

    async def create_violation(
        self,
        org_id: uuid.UUID,
        asset_id: uuid.UUID,
        discovered_url: str,
        platform: str,
        confidence: float,
        **kwargs,
    ) -> Violation:
        return await self._repo.create(
            org_id=org_id,
            asset_id=asset_id,
            discovered_url=discovered_url,
            platform=platform,
            confidence=confidence,
            **kwargs,
        )


# ── Legacy free-function API (backward compat for existing routers) ──────────

async def list_violations(
    db: AsyncSession, org_id: uuid.UUID, offset: int, limit: int,
    asset_id: uuid.UUID | None = None,
):
    return await ViolationService(db).list_violations(org_id, offset, limit, asset_id)


async def get_violation(db: AsyncSession, violation_id: uuid.UUID, org_id: uuid.UUID):
    return await ViolationService(db).get_violation(violation_id, org_id)
