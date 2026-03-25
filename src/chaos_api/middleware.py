"""FastAPI middleware for production hardening.

Includes request ID tracing, rate limiting, and request logging.
"""

import logging
import time
import uuid
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add a unique request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID header to request and response.

        Args:
            request: The incoming request.
            call_next: The next middleware/endpoint in the chain.

        Returns:
            The response with request ID header added.
        """
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response  # type: ignore[no-any-return]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting per IP address.

    Tracks request counts per IP within a time window.
    Not suitable for distributed deployments (use Redis in production).
    """

    def __init__(self, app: Callable, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            app: The ASGI application.
            max_requests: Maximum requests allowed per window.
            window_seconds: Time window in seconds.
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store: client_ip -> list of timestamps
        self._requests: defaultdict[str, list[float]] = defaultdict(list)

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if the client IP has exceeded the rate limit.

        Args:
            client_ip: The client's IP address.

        Returns:
            True if rate limited, False otherwise.
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests and count recent ones
        requests = self._requests[client_ip]
        requests[:] = [t for t in requests if t > window_start]

        if len(requests) >= self.max_requests:
            return True

        requests.append(now)
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit and proceed or return 429.

        Args:
            request: The incoming request.
            call_next: The next middleware/endpoint in the chain.

        Returns:
            The response, or 429 if rate limited.
        """
        # Get client IP (handle proxies)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        if self._is_rate_limited(client_ip):
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(self.window_seconds)},
            )

        result: Response = await call_next(request)
        return result


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing and metadata."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details and timing.

        Args:
            request: The incoming request.
            call_next: The next middleware/endpoint in the chain.

        Returns:
            The response.
        """
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Extract client IP
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "client_ip": client_ip,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }

        # Log at appropriate level based on status code
        if response.status_code >= 500:
            logger.error("Request failed", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("Request error", extra=log_data)
        else:
            logger.info("Request completed", extra=log_data)

        return response  # type: ignore[no-any-return]
