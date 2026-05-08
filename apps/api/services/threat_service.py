"""
Threat analysis service (SRP + DIP).

SRP: Encapsulates threat data aggregation logic, extracted from the router.
DIP: Receives db session via dependency injection.

Previously this logic was inline in the threats router — violating SRP
(router should only handle HTTP concerns, not business logic).
"""

import random
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset
from models.violation import Violation


# Geo-coordinates for known platforms (SRP — configuration data, not logic)
PLATFORM_COORDS: dict[str, dict[str, float]] = {
    "YouTube": {"lat": 37.42, "lon": -122.08},
    "Custom": {"lat": 52.52, "lon": 13.40},
    "twitter": {"lat": 37.77, "lon": -122.41},
    "reddit": {"lat": 37.39, "lon": -122.08},
    "instagram": {"lat": 37.48, "lon": -122.15},
    "tiktok": {"lat": 34.05, "lon": -118.24},
    "unknown": {"lat": 40.71, "lon": -74.01},
}

# Default HQ origin
DEFAULT_ORIGIN = {"lat": 51.51, "lon": -0.13}


class ThreatAnalysisService:
    """
    Aggregates violation data into GeoJSON-ready threat payloads.

    SRP: Only handles threat data transformation.
    DIP: Accepts db session, doesn't create it.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_threats(self, org_id: uuid.UUID, limit: int = 50) -> list[dict]:
        """Get GeoJSON-ready threat data for an organization."""
        result = await self._db.execute(
            select(Violation, Asset.title)
            .join(Asset, Violation.asset_id == Asset.id)
            .where(Asset.org_id == org_id)
            .order_by(Violation.detected_at.desc())
            .limit(limit)
        )
        rows = result.all()

        return [self._map_threat(violation, asset_title) for violation, asset_title in rows]

    @staticmethod
    def _classify_severity(violation: Violation) -> str:
        """Classify threat severity based on status and confidence (SRP — single rule)."""
        if violation.status == "confirmed":
            return "critical"
        if violation.confidence > 0.8:
            return "warning"
        return "info"

    @staticmethod
    def _get_coords(platform: str) -> dict[str, float]:
        """Get geo-coordinates for a platform with jitter (SRP — single rule)."""
        coords = PLATFORM_COORDS.get(platform, PLATFORM_COORDS["unknown"])
        return {
            "lat": coords["lat"] + (random.random() - 0.5) * 4,
            "lon": coords["lon"] + (random.random() - 0.5) * 4,
        }

    def _map_threat(self, violation: Violation, asset_title: str) -> dict:
        """Map a violation to a threat payload (SRP — single transformation)."""
        platform = violation.platform or "unknown"
        coords = self._get_coords(platform)

        return {
            "id": str(violation.id),
            "asset_id": str(violation.asset_id),
            "asset_title": asset_title,
            "platform": platform,
            "confidence": violation.confidence,
            "status": violation.status,
            "severity": self._classify_severity(violation),
            "discovered_url": violation.discovered_url,
            "estimated_reach": violation.estimated_reach,
            "detected_at": violation.detected_at.isoformat() if violation.detected_at else None,
            "origin_lat": DEFAULT_ORIGIN["lat"],
            "origin_lon": DEFAULT_ORIGIN["lon"],
            "detected_lat": coords["lat"],
            "detected_lon": coords["lon"],
        }
