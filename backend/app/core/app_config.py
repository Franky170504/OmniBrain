import os
from pathlib import Path,WindowsPath
from typing import ClassVar
from pydantic import Field,field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.settings import *
from config.path_config import *

# Base directory for the backend (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class AppSettings(BaseSettings):
    PROJECT_NAME: str = settings.project_name
    PROJECT_VERSION: str = settings.project_version

    QDRANT_URL: str = settings.qdrant_url
    QDRANT_API_KEY: str = (settings.qdrant_api_key) 
    QDRANT_COLLECTION: str = settings.collection_name

    QDRANT_SCORE_THRESHOLD: float = settings.qdrant_score_threshold
    QDRANT_SEARCH_LIMIT: int = settings.qdrant_search_limit

    EMBEDDING_MODEL: str = settings.embedding_model
    EMBEDDING_BATCH_SIZE: int = settings.embedding_batch_size
    EMBEDDING_DIMENSION: int = settings.embedding_dimension
    
    GROQ_API_KEY: str = (settings.groq_api_key)
    GROQ_MODEL: str = settings.groq_model
    GROQ_SUPERVISIOR_MODEL :str = settings.groq_supervisior_model
    GROQ_GENERAL_MODEL :str = settings.groq_general_model

    LANGSMITH_TRACKING: bool = settings.langsmith_tracing
    LANGSMITH_API_KEY: str = (settings.langsmith_api_key)
    LANGSMITH_PROJECT: str = settings.langsmith_project
    LANGSMITH_ENDPOINT: str = settings.langsmith_endpoint

    MAX_UPLOAD_SIZE_MB: int = settings.max_upload_size_mb

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:8501",
            "http://127.0.0.1:8000",
        ]
    )

    INPUT_DIR: Path = Path('data/input')
    OUTPUT_DIR: Path = Path('data/output')

    DATABASE_URL: str  = settings.database_url
    DATABASE_POOL_SIZE: int = settings.database_pool_size
    DATABASE_MAX_OVERFLOW: int = settings.database_max_overflow

    DEFAULT_COLLECTION_ID: str = settings.default_collection_id
    LOCAL_USER_EMAIL: str = settings.local_user_email

    STORE_RETRIEVED_TEXT: bool = settings.store_retrived_text

    model_config = SettingsConfigDict(
        env_file=WindowsPath('.env'),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg://")
        return value

    @field_validator("INPUT_DIR", "OUTPUT_DIR")
    @classmethod
    def ensure_directory(cls, value: Path) -> Path:
        value.mkdir(parents=True, exist_ok=True)
        return value


app_settings = AppSettings()

