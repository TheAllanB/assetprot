"""
Abstract repository protocols (DIP — Dependency Inversion Principle).

All repositories implement these protocols so services depend on
abstractions, not concrete implementations. This enables easy
testing with mocks and swapping persistence backends.
"""

import uuid
from typing import Protocol, runtime_checkable

from models.asset import Asset
from models.violation import Violation
from models.scan_run import ScanRun


@runtime_checkable
class AssetRepository(Protocol):
    """Protocol for asset persistence operations."""

    async def list_by_org(
        self, org_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Asset], int]: ...

    async def get_by_id(
        self, asset_id: uuid.UUID, org_id: uuid.UUID
    ) -> Asset | None: ...


@runtime_checkable
class ViolationRepository(Protocol):
    """Protocol for violation persistence operations."""

    async def list_by_org(
        self, org_id: uuid.UUID, offset: int, limit: int, asset_id: uuid.UUID | None = None
    ) -> tuple[list[Violation], int]: ...

    async def get_by_id(
        self, violation_id: uuid.UUID, org_id: uuid.UUID
    ) -> Violation | None: ...

    async def create(
        self,
        org_id: uuid.UUID,
        asset_id: uuid.UUID,
        discovered_url: str,
        platform: str,
        confidence: float,
        status: str = "suspected",
        infringement_type: str | None = None,
        estimated_reach: int | None = None,
        rights_territory_violation: bool = False,
    ) -> Violation: ...


@runtime_checkable
class ScanRunRepository(Protocol):
    """Protocol for scan run persistence operations."""

    async def list_by_org(
        self, org_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[ScanRun], int]: ...

    async def get_by_id(
        self, scan_run_id: uuid.UUID, org_id: uuid.UUID
    ) -> ScanRun | None: ...
