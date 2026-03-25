"""Tests for the main FastAPI application."""

import json
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestHandleRoot:
    """Tests for the root path handler."""

    def test_get_root_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return generated response for GET /."""
        mock_llm_client.generate_response.return_value = '{"message": "Welcome"}'

        response = test_client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Welcome"}

    def test_post_root_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return generated response for POST /."""
        mock_llm_client.generate_response.return_value = '{"created": true}'

        response = test_client.post("/", json={"name": "test"})

        assert response.status_code == 200
        assert response.json() == {"created": True}

    def test_put_root_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return generated response for PUT /."""
        mock_llm_client.generate_response.return_value = '{"updated": true}'

        response = test_client.put("/", json={"name": "test"})

        assert response.status_code == 200
        assert response.json() == {"updated": True}

    def test_delete_root_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return generated response for DELETE /."""
        mock_llm_client.generate_response.return_value = '{"deleted": true}'

        response = test_client.delete("/")

        assert response.status_code == 200
        assert response.json() == {"deleted": True}

    def test_patch_root_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return generated response for PATCH /."""
        mock_llm_client.generate_response.return_value = '{"patched": true}'

        response = test_client.patch("/", json={"field": "value"})

        assert response.status_code == 200
        assert response.json() == {"patched": True}


class TestHandleAnyPath:
    """Tests for the catch-all path handler."""

    def test_get_users_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return generated response for GET /users."""
        mock_llm_client.generate_response.return_value = json.dumps(
            [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        )

        response = test_client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alice"

    def test_get_nested_path_returns_response(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should handle deeply nested paths."""
        mock_llm_client.generate_response.return_value = '{"id": 42}'

        response = test_client.get("/api/v2/users/42/orders/123/items")

        assert response.status_code == 200
        assert response.json()["id"] == 42

    def test_post_with_json_body(self, test_client: TestClient, mock_llm_client: MagicMock) -> None:
        """Should handle POST with JSON body."""
        mock_llm_client.generate_response.return_value = '{"id": 1, "name": "New Item"}'

        response = test_client.post("/items", json={"name": "New Item", "price": 19.99})

        assert response.status_code == 200
        assert response.json()["name"] == "New Item"

    def test_query_params_passed_to_llm(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should pass query parameters to LLM."""
        mock_llm_client.generate_response.return_value = '{"items": []}'

        response = test_client.get("/items?page=1&limit=10")

        assert response.status_code == 200
        call_kwargs = mock_llm_client.generate_response.call_args.kwargs
        assert call_kwargs["query_params"] == {"page": "1", "limit": "10"}

    def test_headers_passed_to_llm(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should pass headers to LLM (excluding filtered ones)."""
        mock_llm_client.generate_response.return_value = '{"data": true}'

        response = test_client.get(
            "/protected", headers={"Authorization": "Bearer secret123", "X-Custom": "value"}
        )

        assert response.status_code == 200
        call_kwargs = mock_llm_client.generate_response.call_args.kwargs
        assert "authorization" in call_kwargs["headers"]
        assert "x-custom" in call_kwargs["headers"]
        assert "host" not in call_kwargs["headers"]


class TestMimeTypeHandling:
    """Tests for MIME type handling in responses."""

    def test_returns_json_by_default(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return JSON by default."""
        mock_llm_client.generate_response.return_value = '{"test": true}'

        response = test_client.get("/test")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_returns_xml_when_requested(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return XML when Accept header is set."""
        mock_llm_client.generate_response.return_value = "<root><item>1</item></root>"

        response = test_client.get("/test", headers={"Accept": "application/xml"})

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"

    def test_returns_html_when_requested(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return HTML when Accept header is set."""
        mock_llm_client.generate_response.return_value = "<html><body>Test</body></html>"

        response = test_client.get("/test", headers={"Accept": "text/html"})

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_returns_plain_text_when_requested(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return plain text when Accept header is set."""
        mock_llm_client.generate_response.return_value = "Hello, World!"

        response = test_client.get("/test", headers={"Accept": "text/plain"})

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")


class TestErrorHandling:
    """Tests for error handling."""

    def test_handles_llm_exception(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should handle LLM exceptions gracefully."""
        mock_llm_client.generate_response.side_effect = Exception("LLM service unavailable")

        response = test_client.get("/test")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Failed to generate response" in data["error"]

    def test_error_response_is_json(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return JSON error response even for non-JSON requests."""
        mock_llm_client.generate_response.side_effect = Exception("LLM error")

        response = test_client.get("/test", headers={"Accept": "text/html"})

        assert response.status_code == 500
        assert response.headers["content-type"] == "application/json"


class TestRequestBodyHandling:
    """Tests for request body handling."""

    def test_json_body_parsed_and_passed(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should parse and pass JSON body to LLM."""
        mock_llm_client.generate_response.return_value = '{"received": true}'

        response = test_client.post("/items", json={"name": "Test", "value": 42})

        assert response.status_code == 200
        call_kwargs = mock_llm_client.generate_response.call_args.kwargs
        assert "name" in call_kwargs["body"]
        assert "Test" in call_kwargs["body"]

    def test_empty_body_handled(self, test_client: TestClient, mock_llm_client: MagicMock) -> None:
        """Should handle empty request body."""
        mock_llm_client.generate_response.return_value = '{"ok": true}'

        response = test_client.post("/items")

        assert response.status_code == 200
        call_kwargs = mock_llm_client.generate_response.call_args.kwargs
        assert call_kwargs["body"] is None
