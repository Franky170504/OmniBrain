from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_qdrant_service
from backend.app.models.schemas import HealthResponse
from src.vectors.service import QdrantService

router = APIRouter(prefix="/health",tags=["Health Check"],)

@router.get("",response_model=HealthResponse,)
def health_check(qdrant_service: QdrantService = Depends(get_qdrant_service),) -> HealthResponse:
    qdrant_status = qdrant_service.health()
    return HealthResponse(status="healthy",qdrant=qdrant_status,)