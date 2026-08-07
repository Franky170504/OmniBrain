from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

import os

load_dotenv(Path(".env"))

@dataclass(frozen=True)
class Settings:
    project_name: str
    project_version: str
    fast_api_url: str

    qdrant_url: str
    qdrant_api_key: str | None
    collection_name: str

    qdrant_score_threshold:float
    qdrant_search_limit : int

    embedding_model: str
    embedding_batch_size: int
    embedding_dimension: int

    groq_api_key: str | None
    groq_model: str
    groq_supervisior_model: str
    groq_general_model: str

    langsmith_tracing: bool 
    langsmith_api_key: str | None
    langsmith_project: str
    langsmith_endpoint: str

    max_upload_size_mb: int

    database_url : str
    database_pool_size: int
    database_max_overflow: int

    default_collection_id: str
    local_user_email: str

    store_retrived_text: bool

def load_settings() -> Settings:
    return Settings(
        project_name = os.getenv("PROJECT_NAME"),
        project_version = os.getenv("PROJECT_VERSION"),
        fast_api_url = os.getenv("FAST_API_URL"),

        qdrant_url=os.getenv("QDRANT_URL"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        collection_name=os.getenv("COLLECTION_NAME"),

        qdrant_score_threshold=os.getenv("QDRANT_SCORE_THRESHOLD"),
        qdrant_search_limit=int(os.getenv("QDRANT_SEARCH_LIMIT")),

        embedding_model=os.getenv("EMBEDDING_MODEL"),
        embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE")),
        embedding_dimension = int(os.getenv("EMBEDDING_DIMENSION")),

        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL"),
        groq_supervisior_model=os.getenv("GROQ_SUPERVISIOR_MODEL"),
        groq_general_model=os.getenv("GROQ_GENERAL_MODEL"),

        langsmith_tracing=os.getenv("LANGSMITH_TRACKING"),
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        langsmith_project=os.getenv("LANGSMITH_PROJECT"),
        langsmith_endpoint=os.getenv("LANGSMITH_ENDPOINT"),

        max_upload_size_mb=os.getenv("MAX_UPLOAD_SIZE_MB"),

        database_url = os.getenv("DATABASE_URL"),
        database_pool_size = os.getenv("DATABASE_POOL_SIZE"),
        database_max_overflow = os.getenv("DATABASE_MAX_OVERFLOW"),

        default_collection_id = os.getenv("DEFAULT_COLLECTION_ID"),
        local_user_email = os.getenv("LOCAL_USER_EMAIL"),

        store_retrived_text = os.getenv("STORE_RETRIEVED_TEXT"), 
    )

settings = load_settings()
