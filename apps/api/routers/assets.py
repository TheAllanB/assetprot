import json
import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies import get_current_org_id, get_db
from dependencies.auth import get_current_user
from models.asset import Asset
from models.asset_fingerprint import AssetFingerprint
from models.user import User
from schemas.asset import AssetIngestResponse, AssetResponse
from schemas.base import APIResponse, PaginatedResponse
from services.asset_service import get_asset, list_assets
from tasks.fingerprint_task import fingerprint_task

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


@router.post("", response_model=APIResponse[AssetIngestResponse])
async def ingest_asset(
    file: UploadFile = File(...),
    title: str = Form(...),
    content_type: str = Form(...),
    territories: str = Form("[]"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if content_type not in ("image", "video", "audio"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="content_type must be image, video, or audio",
        )

    try:
        territories_list = json.loads(territories)
    except json.JSONDecodeError:
        territories_list = []

    asset = Asset(
        org_id=current_user.org_id,
        title=title,
        content_type=content_type,
        territories=territories_list,
        status="pending",
    )
    db.add(asset)
    await db.flush()

    fp = AssetFingerprint(asset_id=asset.id)
    db.add(fp)
    await db.commit()
    await db.refresh(asset)

    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = (file.filename or "file").rsplit(".", 1)[-1] if "." in (file.filename or "") else "bin"
    file_path = os.path.join(settings.upload_dir, f"{asset.id}.{ext}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    task = fingerprint_task.delay(str(asset.id), file_path, content_type)

    return APIResponse(
        success=True,
        data=AssetIngestResponse(asset_id=str(asset.id), task_id=task.id),
    )


@router.get("", response_model=PaginatedResponse[AssetResponse])
async def list_assets_route(
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    assets, total = await list_assets(db, org_id, offset, limit)
    return PaginatedResponse(
        success=True,
        data=[AssetResponse.model_validate(a) for a in assets],
        meta={"total": total, "offset": offset, "limit": limit},
    )


@router.get("/{asset_id}", response_model=APIResponse[AssetResponse])
async def get_asset_route(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    asset = await get_asset(db, asset_id, org_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return APIResponse(success=True, data=AssetResponse.model_validate(asset))
