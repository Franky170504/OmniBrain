from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_qdrant_service
from app.services.qdrant_service import QdrantService

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(qdrant_service: QdrantService = Depends(get_qdrant_service)) -> dict:
    try:
        qdrant_status = qdrant_service.health()
        return {
            "status": "healthy",
            "qdrant": qdrant_status,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {type(exc).__name__}: {exc}",
        ) from exc