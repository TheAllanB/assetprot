"""
Threats router (SRP — only handles HTTP request/response).

Business logic delegated to ThreatAnalysisService.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_org_id, get_db
from schemas.base import APIResponse
from services.threat_service import ThreatAnalysisService

router = APIRouter(prefix="/api/v1/threats", tags=["threats"])


@router.get("", response_model=APIResponse[list])
async def list_threats(
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    """Get GeoJSON-ready threat data for the ThreatMap visualization."""
    service = ThreatAnalysisService(db)
    threats = await service.get_threats(org_id)
    return APIResponse(success=True, data=threats)
