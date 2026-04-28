import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_org_id, get_db
from dependencies.auth import get_current_user
from models.user import User
from models.violation import Violation
from schemas.base import APIResponse, PaginatedResponse
from schemas.violation import CreateViolationRequest, ViolationResponse
from services.violation_service import get_violation, list_violations

router = APIRouter(prefix="/api/v1/violations", tags=["violations"])


@router.get("", response_model=PaginatedResponse[ViolationResponse])
async def list_violations_route(
    offset: int = 0,
    limit: int = 20,
    asset_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    violations, total = await list_violations(db, org_id, offset, limit, asset_id)
    return PaginatedResponse(
        success=True,
        data=[ViolationResponse.model_validate(v) for v in violations],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.get("/{violation_id}", response_model=APIResponse[ViolationResponse])
async def get_violation_route(
    violation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    violation = await get_violation(db, violation_id, org_id)
    if violation is None:
        raise HTTPException(status_code=404, detail="Violation not found")
    return APIResponse(success=True, data=ViolationResponse.model_validate(violation))


@router.post("", response_model=APIResponse[ViolationResponse])
async def create_violation_route(
    req: CreateViolationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    violation = Violation(
        org_id=current_user.org_id,
        asset_id=req.asset_id,
        discovered_url=req.discovered_url,
        platform=req.platform,
        status="suspected",
        confidence=req.confidence,
        infringement_type=req.infringement_type,
        transformation_types=req.transformation_types,
        estimated_reach=req.estimated_reach,
    )
    db.add(violation)
    await db.commit()
    await db.refresh(violation)

    # Broadcast alert via WebSocket
    try:
        from routers.ws import manager

        await manager.broadcast_to_org(str(current_user.org_id), {
            "type": "violation_detected",
            "violation_id": str(violation.id),
            "asset_id": str(req.asset_id),
            "platform": req.platform,
            "confidence": req.confidence,
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception:
        pass  # WebSocket broadcast is best-effort

    return APIResponse(success=True, data=ViolationResponse.model_validate(violation))
