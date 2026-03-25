"""Pytest fixtures and configuration."""

import os
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("MODEL_NAME", "gpt-4o-mini")


@pytest.fixture
def mock_llm_client() -> Generator[MagicMock, None, None]:
    """Mock the LLM client for testing."""
    with patch("chaos_api.main.llm_client") as mock:
        mock.generate_response = AsyncMock(return_value='{"message": "test response"}')
        yield mock


@pytest.fixture
def test_client(mock_llm_client: MagicMock) -> TestClient:
    """Create a test client with mocked LLM."""
    from chaos_api.main import app

    return TestClient(app)


@pytest.fixture
def mock_chat_openai() -> Generator[MagicMock, None, None]:
    """Mock ChatOpenAI for unit tests."""
    with patch("chaos_api.llm_client.ChatOpenAI") as mock:
        instance = MagicMock()
        instance.ainvoke = AsyncMock(return_value=MagicMock(content='{"test": "response"}'))
        mock.return_value = instance
        yield mock
