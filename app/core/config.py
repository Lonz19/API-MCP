from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "API-MCP"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Authentication
    api_key: str = "change-me-in-production"

    # Google Gemini
    gemini_api_key: str = ""
    gemini_default_model: str = "gemini-3.1-flash-lite-preview"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
