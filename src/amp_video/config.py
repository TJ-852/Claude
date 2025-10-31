"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Required API keys
    heygen_api_key: str
    elevenlabs_api_key: str

    # Optional API keys
    openai_api_key: str | None = None

    # Default provider settings
    default_voice: str = "Rachel"
    default_avatar: str = "SantaFe_v2"

    # Storage settings
    output_bucket: str | None = None

    # AWS credentials (optional, for S3)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_default_region: str = "us-east-1"

    # Application settings
    log_level: str = "INFO"
    max_concurrency: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
