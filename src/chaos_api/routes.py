"""Health and metrics endpoints for the chaos API."""

import time
from collections import deque
from typing import Any

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

# Simple in-memory metrics storage (use proper metrics in production)
_request_times: deque[float] = deque(maxlen=1000)
_request_counts: dict[int, int] = {}
_start_time = time.time()

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    uptime_seconds: float


class MetricsResponse(BaseModel):
    """Metrics response model."""

    uptime_seconds: float
    total_requests: int
    requests_per_minute: float
    average_response_time_ms: float
    status_code_distribution: dict[str, int]


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns the health status of the API.",
)
async def health_check(request: Request) -> dict[str, Any]:
    """Check API health status.

    Returns:
        Health status information.
    """
    from chaos_api.config import settings

    uptime = time.time() - _start_time
    return {
        "status": "healthy",
        "version": settings.app_version,
        "uptime_seconds": round(uptime, 2),
    }


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Metrics endpoint",
    description="Returns basic metrics about API usage.",
)
async def metrics(request: Request) -> dict[str, Any]:
    """Get API metrics.

    Returns:
        Usage metrics and statistics.
    """
    uptime = time.time() - _start_time
    total_requests = sum(_request_counts.values())

    # Calculate requests per minute
    rpm = (total_requests / uptime * 60) if uptime > 0 else 0

    # Calculate average response time
    avg_response_time = sum(_request_times) / len(_request_times) if _request_times else 0

    # Convert status code counts to string keys for JSON
    status_distribution = {str(k): v for k, v in _request_counts.items()}

    return {
        "uptime_seconds": round(uptime, 2),
        "total_requests": total_requests,
        "requests_per_minute": round(rpm, 2),
        "average_response_time_ms": round(avg_response_time * 1000, 2),
        "status_code_distribution": status_distribution,
    }


def record_request_metric(status_code: int, duration_ms: float) -> None:
    """Record a request metric.

    Args:
        status_code: HTTP status code of the response.
        duration_ms: Request duration in milliseconds.
    """
    _request_times.append(duration_ms / 1000)  # Store in seconds
    _request_counts[status_code] = _request_counts.get(status_code, 0) + 1
