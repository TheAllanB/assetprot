import uuid
import logging
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

# Context variables for request-scoped data
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
org_id_var: ContextVar[str] = ContextVar("org_id", default="")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign a unique request_id and extract user context from JWT for logging."""

    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())[:8]
        request_id_var.set(req_id)

        # Try to extract user context from auth header (non-blocking)
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            try:
                from core.security import decode_token

                payload = decode_token(auth.split(" ", 1)[1])
                user_id_var.set(payload.get("sub", ""))
                org_id_var.set(payload.get("org_id", ""))
            except Exception:
                pass

        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
