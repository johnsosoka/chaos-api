"""FastAPI application entry point for the chaos API."""

import json
import logging

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from chaos_api.config import settings
from chaos_api.llm_client import LLMClient
from chaos_api.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from chaos_api.mime_handlers import detect_mime_type, parse_request_body
from chaos_api.routes import record_request_metric, router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Accepts any endpoint and HTTP method, then generates a fake response via LLM.",
    version=settings.app_version,
    debug=settings.debug,
)

# Add middleware (order matters - last added is first to execute)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window,
)
app.add_middleware(RequestIDMiddleware)

# Include health and metrics routes
app.include_router(router)

# Single shared client — ChatOpenAI is safe to reuse across requests
llm_client = LLMClient()

# Headers that are internal to HTTP infrastructure and not useful for the LLM
_FILTERED_HEADERS = frozenset(
    {
        "host",
        "content-length",
        "transfer-encoding",
        "connection",
        "keep-alive",
        "te",
        "trailers",
        "upgrade",
        "proxy-authorization",
        "proxy-authenticate",
    }
)


def _extract_headers(request: Request) -> dict:
    """Return request headers with internal/noisy ones removed.

    Args:
        request: The incoming FastAPI request.

    Returns:
        A dictionary of header name → value pairs.
    """
    return {
        key: value for key, value in request.headers.items() if key.lower() not in _FILTERED_HEADERS
    }


async def _handle_request(request: Request, path: str = "") -> Response:
    """Core request handler shared by all routes.

    Extracts request context, detects the desired MIME type, delegates to the
    LLM, and returns the generated response body.

    Args:
        request: The incoming FastAPI request.
        path: The captured URL path segment (may be empty for root).

    Returns:
        A Response containing the LLM-generated body and the correct media type.
    """
    method = request.method
    query_params = dict(request.query_params)
    headers = _extract_headers(request)
    accept_header = request.headers.get("accept")
    mime_type = detect_mime_type(accept_header)
    content_type = request.headers.get("content-type")

    raw_body = await request.body()
    body = parse_request_body(raw_body, content_type) if raw_body else None

    try:
        content = await llm_client.generate_response(
            method=method,
            path=path or "/",
            query_params=query_params,
            headers=headers,
            body=body,
            mime_type=mime_type,
        )
        response = Response(content=content, media_type=mime_type)

        # Record metrics
        record_request_metric(response.status_code, 0)  # Duration logged by middleware

        return response

    except Exception as exc:
        logger.exception("LLM generation failed for %s %s", method, path)
        error_body = json.dumps(
            {
                "error": "Failed to generate response",
                "detail": str(exc),
            }
        )
        return JSONResponse(
            content=json.loads(error_body),
            status_code=500,
        )


@app.api_route(
    "/",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"],
)
async def handle_root(request: Request) -> Response:
    """Handle requests to the root path."""
    return await _handle_request(request, path="/")


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"],
)
async def handle_any(request: Request, path: str) -> Response:
    """Handle requests to any path below root."""
    # Skip the API routes (health, metrics)
    if path in ("health", "metrics"):
        return await _handle_request(request, path=path)
    return await _handle_request(request, path=path)
