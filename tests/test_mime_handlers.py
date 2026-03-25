"""Tests for MIME type detection and request body parsing."""

import json

from chaos_api.mime_handlers import detect_mime_type, parse_request_body


class TestDetectMimeType:
    """Tests for the detect_mime_type function."""

    def test_returns_json_for_none_header(self) -> None:
        """Should return JSON when Accept header is None."""
        result = detect_mime_type(None)
        assert result == "application/json"

    def test_returns_json_for_empty_header(self) -> None:
        """Should return JSON when Accept header is empty."""
        result = detect_mime_type("")
        assert result == "application/json"

    def test_returns_json_for_json_accept(self) -> None:
        """Should return JSON when Accept header is application/json."""
        result = detect_mime_type("application/json")
        assert result == "application/json"

    def test_returns_xml_for_xml_accept(self) -> None:
        """Should return XML when Accept header is application/xml."""
        result = detect_mime_type("application/xml")
        assert result == "application/xml"

    def test_returns_html_for_html_accept(self) -> None:
        """Should return HTML when Accept header is text/html."""
        result = detect_mime_type("text/html")
        assert result == "text/html"

    def test_returns_plain_for_plain_accept(self) -> None:
        """Should return plain text when Accept header is text/plain."""
        result = detect_mime_type("text/plain")
        assert result == "text/plain"

    def test_handles_multiple_types_with_quality(self) -> None:
        """Should handle Accept headers with multiple types and quality values."""
        result = detect_mime_type("text/html,application/xhtml+xml,application/xml;q=0.9")
        assert result == "text/html"

    def test_prefers_higher_quality(self) -> None:
        """Should prefer the type with higher quality value."""
        result = detect_mime_type("application/xml;q=0.8,application/json;q=0.9")
        assert result == "application/json"

    def test_handles_wildcard_subtype(self) -> None:
        """Should handle wildcard subtypes like text/*."""
        result = detect_mime_type("text/*")
        assert result in ["text/plain", "text/html"]

    def test_handles_full_wildcard(self) -> None:
        """Should handle */* wildcard and return default."""
        result = detect_mime_type("*/*")
        assert result == "application/json"

    def test_returns_json_for_unsupported_type(self) -> None:
        """Should return JSON for unsupported MIME types."""
        result = detect_mime_type("image/png")
        assert result == "application/json"

    def test_is_case_insensitive(self) -> None:
        """Should be case insensitive for MIME types."""
        result = detect_mime_type("APPLICATION/JSON")
        assert result == "application/json"

    def test_handles_complex_accept_header(self) -> None:
        """Should handle complex real-world Accept headers."""
        header = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        result = detect_mime_type(header)
        assert result == "text/html"


class TestParseRequestBody:
    """Tests for the parse_request_body function."""

    def test_returns_empty_string_for_empty_body(self) -> None:
        """Should return empty string for empty body."""
        result = parse_request_body(b"", None)
        assert result == ""

    def test_pretty_prints_json_body(self) -> None:
        """Should pretty-print JSON bodies."""
        body = b'{"key": "value", "number": 42}'
        result = parse_request_body(body, "application/json")
        expected = json.dumps({"key": "value", "number": 42}, indent=2)
        assert result == expected

    def test_handles_json_content_type_with_charset(self) -> None:
        """Should handle JSON content type with charset."""
        body = b'{"test": "data"}'
        result = parse_request_body(body, "application/json; charset=utf-8")
        expected = json.dumps({"test": "data"}, indent=2)
        assert result == expected

    def test_falls_back_to_utf8_for_non_json(self) -> None:
        """Should fall back to UTF-8 decoding for non-JSON content."""
        body = b"Hello, World!"
        result = parse_request_body(body, "text/plain")
        assert result == "Hello, World!"

    def test_handles_invalid_json_gracefully(self) -> None:
        """Should handle invalid JSON gracefully."""
        body = b"not valid json"
        result = parse_request_body(body, "application/json")
        assert result == "not valid json"

    def test_handles_utf8_decoding_with_replacement(self) -> None:
        """Should handle invalid UTF-8 bytes with replacement."""
        body = b"Hello \xff\xfe World"
        result = parse_request_body(body, "text/plain")
        assert "Hello" in result
        assert "World" in result

    def test_handles_none_content_type(self) -> None:
        """Should handle None content type."""
        body = b"plain text"
        result = parse_request_body(body, None)
        assert result == "plain text"
