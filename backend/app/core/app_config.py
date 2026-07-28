import os
from pathlib import Path,WindowsPath
from typing import ClassVar
from pydantic import Field,field_validator
from pydantic_settings import BaseSettings

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
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    INPUT_DIR: ClassVar[WindowsPath] = WindowsPath('data/input')
    OUTPUT_DIR: ClassVar[WindowsPath] = WindowsPath('data/output')

    @classmethod
    def resolve_path(cls, value: object) -> Path:
        path = Path(str(value))

        if not path.is_absolute():
            path = BASE_DIR / path

        return path.resolve()
    
    @field_validator("QDRANT_API_KEY", "GROQ_API_KEY","LANGSMITH_API_KEY","LANGSMITH_PROJECT",mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

app_settings = AppSettings()
