"""Tests for the LLM client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chaos_api.llm_client import LLMClient


class TestLLMClient:
    """Tests for the LLMClient class."""

    def test_uses_api_key_from_settings(self) -> None:
        """Should use API key from settings."""
        with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
            with patch("chaos_api.llm_client.settings") as mock_settings:
                mock_settings.openai_api_key = "test-key-123"
                mock_settings.model_name = "gpt-4o-mini"
                LLMClient()
                mock_chat.assert_called_once()
                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["api_key"] == "test-key-123"

    def test_uses_default_model_from_settings(self) -> None:
        """Should use default model from settings."""
        with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
            with patch("chaos_api.llm_client.settings") as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.model_name = "gpt-4o-mini"
                LLMClient()
                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["model"] == "gpt-4o-mini"

    def test_uses_custom_model_from_settings(self) -> None:
        """Should use custom model from settings."""
        with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
            with patch("chaos_api.llm_client.settings") as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.model_name = "gpt-4o"
                LLMClient()
                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["model"] == "gpt-4o"

    def test_sets_temperature(self) -> None:
        """Should set temperature to 0.7."""
        with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
            with patch("chaos_api.llm_client.settings") as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.model_name = "gpt-4o-mini"
                LLMClient()
                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["temperature"] == 0.7


class TestLLMClientGenerateResponse:
    """Tests for the generate_response method."""

    @pytest.mark.asyncio
    async def test_generates_response_with_correct_prompts(self) -> None:
        """Should generate response with correct system and user prompts."""
        with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
            with patch("chaos_api.llm_client.settings") as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.model_name = "gpt-4o-mini"
                mock_instance = MagicMock()
                mock_response = MagicMock()
                mock_response.content = '{"id": 1, "name": "Test User"}'
                mock_instance.ainvoke = AsyncMock(return_value=mock_response)
                mock_chat.return_value = mock_instance

                client = LLMClient()
                result = await client.generate_response(
                    method="GET",
                    path="/users/1",
                    query_params={},
                    headers={},
                    body=None,
                    mime_type="application/json",
                )

            assert result == '{"id": 1, "name": "Test User"}'
            mock_instance.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_strips_whitespace_from_response(self) -> None:
        """Should strip whitespace from LLM response."""
        with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
            with patch("chaos_api.llm_client.settings") as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.model_name = "gpt-4o-mini"
                mock_instance = MagicMock()
                mock_response = MagicMock()
                mock_response.content = '  {"test": "value"}  \n\n'
                mock_instance.ainvoke = AsyncMock(return_value=mock_response)
                mock_chat.return_value = mock_instance

                client = LLMClient()
                result = await client.generate_response(
                    method="GET",
                    path="/test",
                    query_params={},
                    headers={},
                    body=None,
                    mime_type="application/json",
                )

            assert result == '{"test": "value"}'

    @pytest.mark.asyncio
    async def test_passes_all_parameters_to_prompt_builder(self) -> None:
        """Should pass all parameters to prompt builder functions."""
        with patch("chaos_api.llm_client.build_system_prompt") as mock_system:
            with patch("chaos_api.llm_client.build_user_prompt") as mock_user:
                with patch("chaos_api.llm_client.ChatOpenAI") as mock_chat:
                    with patch("chaos_api.llm_client.settings") as mock_settings:
                        mock_settings.openai_api_key = "test-key"
                        mock_settings.model_name = "gpt-4o-mini"
                        mock_instance = MagicMock()
                        mock_instance.ainvoke = AsyncMock(return_value=MagicMock(content="test"))
                        mock_chat.return_value = mock_instance

                        client = LLMClient()
                        await client.generate_response(
                            method="POST",
                            path="/users",
                            query_params={"page": "1"},
                            headers={"Authorization": "Bearer token"},
                            body='{"name": "John"}',
                            mime_type="application/json",
                        )

                    mock_system.assert_called_once_with("application/json")
                    mock_user.assert_called_once_with(
                        method="POST",
                        path="/users",
                        query_params={"page": "1"},
                        headers={"Authorization": "Bearer token"},
                        body='{"name": "John"}',
                        mime_type="application/json",
                    )
