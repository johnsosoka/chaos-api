"""Application configuration using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key for LLM requests")
    model_name: str = Field(default="gpt-4o-mini", description="OpenAI model to use")

    # Application Configuration
    app_name: str = Field(default="Chaos API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Maximum requests per window per IP")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    request_log_format: str = Field(
        default="%(asctime)s - %(request_id)s - %(method)s %(path)s - %(status_code)s - %(duration_ms).2fms",
        description="Request log format string",
    )


# Global settings instance
settings = Settings()
