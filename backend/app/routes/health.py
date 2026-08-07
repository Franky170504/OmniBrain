from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_qdrant_service
from app.models.schemas import HealthResponse
from app.services.qdrant_service import QdrantService


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check(
    session: AsyncSession = Depends(get_db),
    qdrant_service: QdrantService = Depends(get_qdrant_service),
) -> HealthResponse:
    postgres_status = {"status": "healthy"}
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        postgres_status = {"status": "unhealthy", "error": str(exc)}

    qdrant_status = qdrant_service.health()
    overall = "healthy"
    if postgres_status["status"] != "healthy" or qdrant_status["status"] != "healthy":
        overall = "degraded"

    return HealthResponse(
        status=overall,
        postgres=postgres_status,
        qdrant=qdrant_status,
    )
