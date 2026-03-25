"""Prompt construction for the chaos API LLM calls."""

import json


def build_system_prompt(mime_type: str) -> str:
    """Return a system prompt instructing the LLM to act as a REST API simulator.

    The prompt tells the LLM to infer what API would realistically live at the
    requested path and return believable fake data in the correct format.

    Args:
        mime_type: The MIME type the response should be formatted as.

    Returns:
        A system prompt string.
    """
    format_rules = _format_rules_for_mime_type(mime_type)

    return f"""You are a REST API simulator. Your job is to pretend you are \
whatever real-world API would exist at the given endpoint, and return a \
realistic, believable response for that API.

Rules:
- Infer the API's domain and purpose from the URL path, HTTP method, query \
parameters, and request body.
- Return realistic fake data that makes sense for the endpoint — not lorem \
ipsum or placeholder text.
- Use plausible names, dates, IDs, prices, addresses, and other domain-specific \
values.
- Respond ONLY with the raw response body. No explanations, no commentary, \
no markdown code fences.
- The response must be valid {mime_type}.

{format_rules}"""


def _format_rules_for_mime_type(mime_type: str) -> str:
    """Return format-specific rules for the given MIME type.

    Args:
        mime_type: The target MIME type.

    Returns:
        A string of additional formatting instructions.
    """
    rules: dict[str, str] = {
        "application/json": (
            "Format: Return valid, well-structured JSON only. "
            "No trailing commas. No comments. No markdown fences."
        ),
        "application/xml": (
            "Format: Return valid XML only. Include an XML declaration if appropriate. "
            "Use meaningful element and attribute names. No markdown fences."
        ),
        "text/html": (
            "Format: Return valid HTML only. You may return a full page or a fragment "
            "depending on what makes sense for the endpoint. No markdown fences."
        ),
        "text/plain": (
            "Format: Return plain text only. No markup, no JSON, no XML. "
            "Just human-readable text appropriate for the endpoint."
        ),
    }
    return rules.get(mime_type, "Format: Return content appropriate for the MIME type.")


def build_user_prompt(
    method: str,
    path: str,
    query_params: dict,
    headers: dict,
    body: str | None,
    mime_type: str,
) -> str:
    """Construct the user-facing prompt describing the incoming HTTP request.

    Args:
        method: The HTTP method (e.g., GET, POST).
        path: The URL path (e.g., /users/42).
        query_params: Dictionary of query string parameters.
        headers: Dictionary of request headers (pre-filtered).
        body: The decoded request body, or None if empty.
        mime_type: The desired response MIME type.

    Returns:
        A prompt string describing the request for the LLM.
    """
    lines: list[str] = [
        f"HTTP Method: {method.upper()}",
        f"Path: /{path}" if not path.startswith("/") else f"Path: {path}",
    ]

    if query_params:
        lines.append(f"Query Parameters: {json.dumps(query_params)}")

    if headers:
        lines.append(f"Request Headers: {json.dumps(headers)}")

    if body:
        lines.append(f"Request Body:\n{body}")

    lines.append(f"\nRespond as if you are the API at this endpoint. Return {mime_type}.")

    return "\n".join(lines)
