from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    environment: Literal["development", "staging", "production"]
    debug: bool
    database_url: PostgresDsn
    database_pool_size: int = 5
    api_v1_prefix: str = "/api/v1"
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url_str(self) -> str:
        """Вернуть адрес базы в виде обычной строки."""
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Создать настройки один раз и затем переиспользовать их."""
    return Settings()


settings = get_settings()
