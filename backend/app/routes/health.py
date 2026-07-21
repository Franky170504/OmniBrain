from fastapi import APIRouter, status
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health Check"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Backend Health Check",
    description="Check operational status and API responsiveness.",
    responses={
        200: {"description": "API is operational and healthy."}
    }
)
async def health_check() -> HealthResponse:
    """Return backend operational status."""
    return HealthResponse()
