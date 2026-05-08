import json
from datetime import datetime, timezone
from typing import Any, Dict


class AgentTrace:
    """Records a structured execution trace for an agent pipeline run."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.started_at = datetime.now(timezone.utc)
        self.steps: list[Dict[str, Any]] = []

    def log_step(
        self,
        node_name: str,
        input_summary: Any,
        output_summary: Any,
        duration_ms: float,
    ):
        """Log a single node execution step."""
        self.steps.append({
            "node": node_name,
            "input_summary": self._safe_serialize(input_summary),
            "output_summary": self._safe_serialize(output_summary),
            "duration_ms": round(duration_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to a dict suitable for JSONB storage."""
        return {
            "task_id": self.task_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "total_duration_ms": round(
                (datetime.now(timezone.utc) - self.started_at).total_seconds() * 1000, 2
            ),
            "steps": self.steps,
            "step_count": len(self.steps),
        }

    @staticmethod
    def _safe_serialize(obj: Any) -> Any:
        """Safely serialize objects for JSON storage."""
        if isinstance(obj, (dict, list, str, int, float, bool, type(None))):
            return obj
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        return str(obj)
