from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.models.health import HealthResponse


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check API health",
)
def get_health() -> HealthResponse:
    """Return the current health status of the API."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
    )