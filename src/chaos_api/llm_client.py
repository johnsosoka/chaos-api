"""LangChain wrapper for generating chaos API responses via an LLM."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from chaos_api.config import settings
from chaos_api.prompt_builder import build_system_prompt, build_user_prompt


class LLMClient:
    """Wraps a ChatOpenAI model to generate fake REST API responses.

    The client reads OPENAI_API_KEY and MODEL_NAME from the environment at
    instantiation time. MODEL_NAME defaults to gpt-4o-mini when not set.
    """

    def __init__(self) -> None:
        """Initialize the LLM client with settings from config."""
        self._llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,  # type: ignore[arg-type]
            temperature=0.7,
        )

    async def generate_response(
        self,
        method: str,
        path: str,
        query_params: dict,
        headers: dict,
        body: str | None,
        mime_type: str,
    ) -> str:
        """Generate a fake REST API response for the given request context.

        Args:
            method: The HTTP method (e.g., GET, POST).
            path: The URL path the request was made to.
            query_params: Parsed query string parameters.
            headers: Filtered request headers.
            body: The decoded request body, or None.
            mime_type: The desired response MIME type.

        Returns:
            The LLM-generated response body as a stripped string.
        """
        system_prompt = build_system_prompt(mime_type)
        user_prompt = build_user_prompt(
            method=method,
            path=path,
            query_params=query_params,
            headers=headers,
            body=body,
            mime_type=mime_type,
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = await self._llm.ainvoke(messages)
        return str(response.content).strip()
