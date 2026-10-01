from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY")
    llm_model: str = "openrouter/free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "documents"

    redis_url: str = "redis://localhost:6379"
    chat_ttl_seconds: int = 3600
    max_history_messages: int = 10

    database_url: str = "sqlite:///./app.db"

    embedding_model: str = "all-mpnet-base-v2"
    vector_size: int = 768


@lru_cache
def get_settings() -> Settings:
    return Settings()
