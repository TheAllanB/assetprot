"""
Notification service implementations (ISP + SRP + DIP).

ISP: NotificationService protocol has a single method — callers only depend on what they need.
SRP: This module only handles notification delivery.
DIP: Callers depend on the NotificationService protocol, not WebSocket specifics.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WebSocketNotificationService:
    """
    WebSocket-backed notification service (DIP — implements NotificationService protocol).

    ISP: Only exposes notify_violation() — callers don't need to know about
    WebSocket connection management.
    """

    def __init__(self, connection_manager: Any) -> None:
        self._manager = connection_manager

    async def notify_violation(self, org_id: str, payload: dict) -> None:
        """Send a violation alert to all connections for an organization."""
        try:
            await self._manager.broadcast_to_org(org_id, {
                "type": "violation_detected",
                **payload,
            })
        except Exception as e:
            logger.warning(f"WebSocket notification failed for org {org_id}: {e}")


class LogNotificationService:
    """
    Logging-only notification service for testing/development (LSP — substitutable).

    LSP: Can replace WebSocketNotificationService anywhere the protocol is expected.
    """

    async def notify_violation(self, org_id: str, payload: dict) -> None:
        logger.info(f"[NOTIFICATION] org={org_id} violation={payload}")
