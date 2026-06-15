from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    github_webhook_secret: str = ""
    app_id: str = ""
    private_key: str = ""
    log_level: str = "INFO"
    api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()

