"""Tests for prompt building functions."""

import json

from chaos_api.prompt_builder import (
    _format_rules_for_mime_type,
    build_system_prompt,
    build_user_prompt,
)


class TestBuildSystemPrompt:
    """Tests for the build_system_prompt function."""

    def test_includes_mime_type_in_prompt(self) -> None:
        """Should include the MIME type in the system prompt."""
        result = build_system_prompt("application/json")
        assert "application/json" in result

    def test_includes_format_rules_for_json(self) -> None:
        """Should include JSON-specific format rules."""
        result = build_system_prompt("application/json")
        assert "JSON" in result
        assert "No trailing commas" in result

    def test_includes_format_rules_for_xml(self) -> None:
        """Should include XML-specific format rules."""
        result = build_system_prompt("application/xml")
        assert "XML" in result
        assert "XML declaration" in result

    def test_includes_format_rules_for_html(self) -> None:
        """Should include HTML-specific format rules."""
        result = build_system_prompt("text/html")
        assert "HTML" in result
        assert "full page or a fragment" in result

    def test_includes_format_rules_for_plain_text(self) -> None:
        """Should include plain text-specific format rules."""
        result = build_system_prompt("text/plain")
        assert "plain text" in result
        assert "No markup" in result

    def test_includes_core_rules(self) -> None:
        """Should include core simulation rules."""
        result = build_system_prompt("application/json")
        assert "REST API simulator" in result
        assert "realistic, believable response" in result
        assert "No explanations" in result
        assert "no markdown code fences" in result


class TestFormatRulesForMimeType:
    """Tests for the _format_rules_for_mime_type function."""

    def test_returns_json_rules(self) -> None:
        """Should return JSON-specific rules."""
        result = _format_rules_for_mime_type("application/json")
        assert "valid, well-structured JSON" in result

    def test_returns_xml_rules(self) -> None:
        """Should return XML-specific rules."""
        result = _format_rules_for_mime_type("application/xml")
        assert "valid XML" in result

    def test_returns_html_rules(self) -> None:
        """Should return HTML-specific rules."""
        result = _format_rules_for_mime_type("text/html")
        assert "valid HTML" in result

    def test_returns_plain_text_rules(self) -> None:
        """Should return plain text-specific rules."""
        result = _format_rules_for_mime_type("text/plain")
        assert "plain text only" in result

    def test_returns_default_for_unknown_type(self) -> None:
        """Should return default rules for unknown MIME type."""
        result = _format_rules_for_mime_type("image/png")
        assert "appropriate for the MIME type" in result


class TestBuildUserPrompt:
    """Tests for the build_user_prompt function."""

    def test_includes_http_method(self) -> None:
        """Should include HTTP method in the prompt."""
        result = build_user_prompt("GET", "/users", {}, {}, None, "application/json")
        assert "HTTP Method: GET" in result

    def test_includes_path(self) -> None:
        """Should include path in the prompt."""
        result = build_user_prompt("GET", "/users", {}, {}, None, "application/json")
        assert "Path: /users" in result

    def test_handles_path_without_leading_slash(self) -> None:
        """Should handle paths without leading slash."""
        result = build_user_prompt("GET", "users", {}, {}, None, "application/json")
        assert "Path: /users" in result

    def test_includes_query_params_when_present(self) -> None:
        """Should include query params when present."""
        query_params = {"page": "1", "limit": "10"}
        result = build_user_prompt("GET", "/users", query_params, {}, None, "application/json")
        assert "Query Parameters:" in result
        assert '"page": "1"' in result

    def test_omits_query_params_when_empty(self) -> None:
        """Should omit query params when empty."""
        result = build_user_prompt("GET", "/users", {}, {}, None, "application/json")
        assert "Query Parameters:" not in result

    def test_includes_headers_when_present(self) -> None:
        """Should include headers when present."""
        headers = {"Authorization": "Bearer token123"}
        result = build_user_prompt("GET", "/users", {}, headers, None, "application/json")
        assert "Request Headers:" in result
        assert "Bearer token123" in result

    def test_omits_headers_when_empty(self) -> None:
        """Should omit headers when empty."""
        result = build_user_prompt("GET", "/users", {}, {}, None, "application/json")
        assert "Request Headers:" not in result

    def test_includes_body_when_present(self) -> None:
        """Should include body when present."""
        body = '{"name": "John", "email": "john@example.com"}'
        result = build_user_prompt("POST", "/users", {}, {}, body, "application/json")
        assert "Request Body:" in result
        assert "john@example.com" in result

    def test_omits_body_when_none(self) -> None:
        """Should omit body when None."""
        result = build_user_prompt("GET", "/users", {}, {}, None, "application/json")
        assert "Request Body:" not in result

    def test_includes_response_format_instruction(self) -> None:
        """Should include response format instruction."""
        result = build_user_prompt("GET", "/users", {}, {}, None, "application/json")
        assert "Respond as if you are the API" in result
        assert "Return application/json" in result

    def test_handles_post_with_body(self) -> None:
        """Should handle POST request with body correctly."""
        body = json.dumps({"product_id": "abc123", "quantity": 2})
        result = build_user_prompt(
            "POST", "/orders", {}, {"Content-Type": "application/json"}, body, "application/json"
        )
        assert "HTTP Method: POST" in result
        assert "Path: /orders" in result
        assert "abc123" in result
        assert "Content-Type" in result
