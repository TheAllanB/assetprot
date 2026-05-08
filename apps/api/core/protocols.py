"""
Abstract protocols for ML infrastructure (DIP + ISP).

VectorStore protocol decouples services from Qdrant specifics.
NotificationService protocol decouples violation alerting from WebSocket.
DMCAGenerator protocol decouples DMCA notice generation from template.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VectorStore(Protocol):
    """Protocol for vector similarity search operations (ISP — only the methods callers need)."""

    def upsert(
        self, collection: str, asset_id: str, org_id: str, vector: list[float]
    ) -> str: ...

    def search(
        self, collection: str, vector: list[float], score_threshold: float, limit: int = 10
    ) -> list[dict]: ...


@runtime_checkable
class NotificationService(Protocol):
    """Protocol for real-time alert delivery (ISP — single responsibility)."""

    async def notify_violation(self, org_id: str, payload: dict) -> None: ...


@runtime_checkable
class DMCAGenerator(Protocol):
    """Protocol for DMCA notice generation (OCP — extend via new implementations, not modification)."""

    def generate(self, violation: Any) -> str: ...


@runtime_checkable
class FingerprintStrategy(Protocol):
    """
    Protocol for content fingerprinting strategies (OCP + LSP).

    New modalities (e.g., text fingerprinting) can be added by implementing
    this protocol without modifying existing code.
    """

    def supports(self, content_type: str) -> bool:
        """Return True if this strategy handles the given content type."""
        ...

    async def fingerprint(self, asset_id: str, file_path: str, **kwargs: Any) -> dict:
        """
        Execute fingerprinting and return result dict.

        Returns:
            dict with keys like 'phash', 'embedding', 'watermark_payload', etc.
        """
        ...
