from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv(Path(".env"))

@dataclass(frozen=True)
class Settings:
    project_name: str
    project_version: str

    qdrant_url: str
    qdrant_api_key: str | None
    collection_name: str

    qdrant_score_threshold:float
    qdrant_search_limit : int

    embedding_model: str
    embedding_batch_size: int

    groq_api_key: str | None
    groq_model: str
    groq_supervisior_model: str
    groq_general_model: str

    langsmith_tracing: bool 
    langsmith_api_key: str | None
    langsmith_project: str
    langsmith_endpoint: str

    max_upload_size_mb: int

def load_settings() -> Settings:
    return Settings(
        project_name = os.getenv("PROJECT_NAME"),
        project_version = os.getenv("PROJECT_VERSION"),

        qdrant_url=os.getenv("QDRANT_URL",),
        qdrant_api_key=(os.getenv("QDRANT_API_KEY")  ),
        collection_name=os.getenv("COLLECTION_NAME"),

        qdrant_score_threshold=(os.getenv("QDRANT_SCORE_THRESHOLD")),
        qdrant_search_limit=int(os.getenv("QDRANT_SEARCH_LIMIT")),

        embedding_model=os.getenv("EMBEDDING_MODEL"),
        embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE")),

        groq_api_key=(os.getenv("GROQ_API_KEY")),
        groq_model=(os.getenv("GROQ_MODEL")),
        groq_supervisior_model=(os.getenv("GROQ_SUPERVISIOR_MODEL")),
        groq_general_model=(os.getenv("GROQ_GENERAL_MODEL")),

        langsmith_tracing=(os.getenv("LANGSMITH_TRACKING")),
        langsmith_api_key=(os.getenv("LANGSMITH_API_KEY")),
        langsmith_project=(os.getenv("LANGSMITH_PROJECT")),
        langsmith_endpoint=(os.getenv("LANGSMITH_ENDPOINT")),

        max_upload_size_mb=os.getenv("MAX_UPLOAD_SIZE_MB"),
    )

settings = load_settings()