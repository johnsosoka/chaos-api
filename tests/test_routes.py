"""Tests for health and metrics endpoints."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, test_client: TestClient, mock_llm_client: MagicMock) -> None:
        """Should return 200 OK for health check."""
        response = test_client.get("/health")

        assert response.status_code == 200

    def test_health_returns_json(self, test_client: TestClient, mock_llm_client: MagicMock) -> None:
        """Should return JSON response."""
        response = test_client.get("/health")

        assert response.headers["content-type"] == "application/json"

    def test_health_contains_status(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include status field."""
        response = test_client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_contains_version(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include version field."""
        response = test_client.get("/health")
        data = response.json()

        assert "version" in data

    def test_health_contains_uptime(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include uptime_seconds field."""
        response = test_client.get("/health")
        data = response.json()

        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], int | float)
        assert data["uptime_seconds"] >= 0


class TestMetricsEndpoint:
    """Tests for the /metrics endpoint."""

    def test_metrics_returns_200(self, test_client: TestClient, mock_llm_client: MagicMock) -> None:
        """Should return 200 OK for metrics."""
        response = test_client.get("/metrics")

        assert response.status_code == 200

    def test_metrics_returns_json(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should return JSON response."""
        response = test_client.get("/metrics")

        assert response.headers["content-type"] == "application/json"

    def test_metrics_contains_uptime(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include uptime_seconds field."""
        response = test_client.get("/metrics")
        data = response.json()

        assert "uptime_seconds" in data

    def test_metrics_contains_total_requests(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include total_requests field."""
        response = test_client.get("/metrics")
        data = response.json()

        assert "total_requests" in data
        assert isinstance(data["total_requests"], int)

    def test_metrics_contains_requests_per_minute(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include requests_per_minute field."""
        response = test_client.get("/metrics")
        data = response.json()

        assert "requests_per_minute" in data
        assert isinstance(data["requests_per_minute"], float)

    def test_metrics_contains_average_response_time(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include average_response_time_ms field."""
        response = test_client.get("/metrics")
        data = response.json()

        assert "average_response_time_ms" in data
        assert isinstance(data["average_response_time_ms"], float)

    def test_metrics_contains_status_code_distribution(
        self, test_client: TestClient, mock_llm_client: MagicMock
    ) -> None:
        """Should include status_code_distribution field."""
        response = test_client.get("/metrics")
        data = response.json()

        assert "status_code_distribution" in data
        assert isinstance(data["status_code_distribution"], dict)
