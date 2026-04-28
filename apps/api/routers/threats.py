import random
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_org_id, get_db
from models.asset import Asset
from models.violation import Violation
from schemas.base import APIResponse

router = APIRouter(prefix="/api/v1/threats", tags=["threats"])

# Geo-coordinates for demo platforms (realistic IP geo-locations)
PLATFORM_COORDS = {
    "YouTube": {"lat": 37.42, "lon": -122.08},
    "Custom": {"lat": 52.52, "lon": 13.40},
    "twitter": {"lat": 37.77, "lon": -122.41},
    "reddit": {"lat": 37.39, "lon": -122.08},
    "instagram": {"lat": 37.48, "lon": -122.15},
    "tiktok": {"lat": 34.05, "lon": -118.24},
    "unknown": {"lat": 40.71, "lon": -74.01},
}


@router.get("", response_model=APIResponse[list])
async def list_threats(
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
):
    """
    Get GeoJSON-ready threat data for the ThreatMap visualization.
    Aggregates violations with geographic coordinates based on detected platform.
    """
    result = await db.execute(
        select(Violation, Asset.title)
        .join(Asset, Violation.asset_id == Asset.id)
        .where(Asset.org_id == org_id)
        .order_by(Violation.detected_at.desc())
        .limit(50)
    )
    rows = result.all()

    threats = []
    for violation, asset_title in rows:
        platform = violation.platform or "unknown"
        coords = PLATFORM_COORDS.get(platform, PLATFORM_COORDS["unknown"])

        # Add slight randomization to prevent point overlap
        jitter_lat = (random.random() - 0.5) * 4
        jitter_lon = (random.random() - 0.5) * 4

        severity = "critical" if violation.status == "confirmed" else (
            "warning" if violation.confidence > 0.8 else "info"
        )

        threats.append({
            "id": str(violation.id),
            "asset_id": str(violation.asset_id),
            "asset_title": asset_title,
            "platform": platform,
            "confidence": violation.confidence,
            "status": violation.status,
            "severity": severity,
            "discovered_url": violation.discovered_url,
            "estimated_reach": violation.estimated_reach,
            "detected_at": violation.detected_at.isoformat() if violation.detected_at else None,
            # Origin = rights holder location (London HQ as default)
            "origin_lat": 51.51,
            "origin_lon": -0.13,
            # Detected = platform geo-location with jitter
            "detected_lat": coords["lat"] + jitter_lat,
            "detected_lon": coords["lon"] + jitter_lon,
        })

    return APIResponse(success=True, data=threats)
