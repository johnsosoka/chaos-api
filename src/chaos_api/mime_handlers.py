"""MIME type detection and request body parsing for the chaos API."""

import contextlib
import json

SUPPORTED_MIME_TYPES: list[str] = [
    "application/json",
    "application/xml",
    "text/plain",
    "text/html",
]

_DEFAULT_MIME_TYPE = "application/json"


def detect_mime_type(accept_header: str | None) -> str:
    """Parse an Accept header and return the best matching supported MIME type.

    Falls back to application/json if no supported type is found or the header
    is absent.

    Args:
        accept_header: The value of the HTTP Accept header, or None.

    Returns:
        A supported MIME type string.
    """
    if not accept_header:
        return _DEFAULT_MIME_TYPE

    # Accept headers can contain multiple types with optional quality values,
    # e.g. "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    candidates: list[tuple[float, str]] = []

    for segment in accept_header.split(","):
        segment = segment.strip()
        if not segment:
            continue

        parts = segment.split(";")
        media_type = parts[0].strip().lower()
        quality = 1.0

        for param in parts[1:]:
            param = param.strip()
            if param.startswith("q="):
                with contextlib.suppress(ValueError):
                    quality = float(param[2:])

        candidates.append((quality, media_type))

    # Sort by quality descending, then check each against supported types
    candidates.sort(key=lambda x: x[0], reverse=True)

    for _, media_type in candidates:
        if media_type in SUPPORTED_MIME_TYPES:
            return media_type
        # Handle wildcard subtypes like "text/*"
        if "/" in media_type:
            prefix = media_type.split("/")[0]
            for supported in SUPPORTED_MIME_TYPES:
                if supported.startswith(prefix + "/"):
                    return supported
        # Handle full wildcard */*
        if media_type == "*/*":
            return _DEFAULT_MIME_TYPE

    return _DEFAULT_MIME_TYPE


def parse_request_body(body: bytes, content_type: str | None) -> str:
    """Decode a raw request body to a human-readable string.

    For JSON content types, attempts to pretty-print the parsed JSON.
    Falls back to raw UTF-8 decoding for all other cases.

    Args:
        body: The raw request body bytes.
        content_type: The Content-Type header value, or None.

    Returns:
        A string representation of the body, or an empty string if the body
        is empty.
    """
    if not body:
        return ""

    # Attempt JSON pretty-printing when appropriate
    if content_type and "json" in content_type:
        try:
            parsed = json.loads(body)
            return json.dumps(parsed, indent=2)
        except (json.JSONDecodeError, ValueError):
            pass

    # Fall back to raw decode, replacing undecodable bytes
    return body.decode("utf-8", errors="replace")
