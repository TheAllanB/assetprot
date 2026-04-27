import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_org_id, get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.base import APIResponse, PaginatedResponse
from schemas.scan_run import ScanRunResponse
from services.scan_run_service import list_scan_runs
from tasks.detection_task import detection_task

router = APIRouter(prefix="/api/v1/scan-runs", tags=["scan-runs"])


@router.get("", response_model=PaginatedResponse[ScanRunResponse])
async def list_scan_runs_route(
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    runs, total = await list_scan_runs(db, org_id, offset, limit)
    return PaginatedResponse(
        success=True,
        data=[ScanRunResponse.model_validate(r) for r in runs],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.post("", response_model=APIResponse[dict])
async def trigger_scan(
    asset_id: str,
    current_user: User = Depends(get_current_user),
):
    task = detection_task.delay(asset_id, str(current_user.org_id))

    return APIResponse(
        success=True,
        data={"scan_run_id": task.id, "status": "triggered"},
    )
