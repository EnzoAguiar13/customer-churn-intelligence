"""Environment-backed application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration that is safe to load in development and CI."""

    model_config = SettingsConfigDict(
        env_prefix="CCI_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = Field(default="Customer Churn Intelligence")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return one immutable-by-convention settings instance per process."""

    return Settings()
