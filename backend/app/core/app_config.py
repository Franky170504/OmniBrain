import os
from dotenv import load_dotenv
from pathlib import Path,WindowsPath
from typing import List,ClassVar
from pydantic import BaseModel, Field, field_validator

from config.settings import settings
from config.path_config import *

load_dotenv(Path(".env"))

# Base directory for the backend (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    """Application settings and configuration defaults."""
    PROJECT_NAME: str = "OmniBrain API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend foundation for document ingestion and AI workspace assistant."

    QDRANT_URL: str = settings.qdrant_url
    QDRANT_API_KEY: str = (settings.qdrant_api_key) 
    QDRANT_COLLECTION: str = settings.collection_name

    EMBEDDING_MODEL: str = settings.embedding_model
    EMBEDDING_BATCH_SIZE: int = settings.embedding_batch_size

    QDRANT_SCORE_THRESHOLD: float = settings.qdrant_score_threshold
    QDRANT_SEARCH_LIMIT: int = settings.qdrant_search_limit

    OPENAI_API_KEY: str = (settings.openai_api_key)
    OPENAI_MODEL: str = settings.openai_model

    INPUT_DIR: ClassVar[WindowsPath] = WindowsPath('data/input')
    OUTPUT_DIR: ClassVar[WindowsPath] = WindowsPath('data/output')
    MAX_UPLOAD_SIZE_MB: int = 50

    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ]
    )
    @field_validator("QDRANT_API_KEY", "OPENAI_API_KEY", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]

        return value


settings = Settings()
