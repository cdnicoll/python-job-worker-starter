"""Health check routes."""
from fastapi import APIRouter, Response

from src.config.database import check_transaction_pooler_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """API liveness check."""
    return {"status": "ok"}


@router.get("/health/db")
async def health_db(response: Response) -> dict:
    """Database connectivity check. Returns 503 when DB unreachable."""
    ok = await check_transaction_pooler_health()
    if not ok:
        response.status_code = 503
        return {"status": "error", "message": "Database unreachable"}
    return {"status": "ok"}
