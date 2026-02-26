"""Metrics middleware - request timing."""
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.utils.logging import get_logger

logger = get_logger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Log request timing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(request.state, "request_id", None)
        extra = {"request_id": request_id} if request_id else {}
        logger.info(
            f"request completed path={request.url.path} method={request.method} status={response.status_code} duration_ms={duration_ms:.2f}",
            extra=extra,
        )
        return response
