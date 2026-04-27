import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_org_id, get_db
from models.asset import Asset
from models.violation import Violation
from schemas.base import APIResponse
from services.dmca_service import generate_dmca_notice

router = APIRouter(prefix="/api/v1/violations", tags=["dmca"])


@router.post("/{violation_id}/dmca", response_model=APIResponse[dict])
async def generate_dmca(
    violation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    result = await db.execute(
        select(Violation).where(
            Violation.id == violation_id,
            Violation.asset_id.in_(
                select(Asset.id).where(Asset.org_id == org_id)
            ),
        )
    )
    violation = result.scalar_one_or_none()

    if violation is None:
        raise HTTPException(
            detail="Violation not found",
            status_code=404,
        )

    notice = generate_dmca_notice(violation)

    from models.dmca_notice import DMCANotice
    dmca = DMCANotice(
        violation_id=violation_id,
        notice_text=notice,
        status="draft",
    )
    db.add(dmca)
    await db.commit()
    await db.refresh(dmca)

    return APIResponse(
        success=True,
        data={
            "notice_id": str(dmca.id),
            "notice_text": notice,
            "status": dmca.status,
        },
    )