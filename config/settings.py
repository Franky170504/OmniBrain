from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(".env"))


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _get_int_env(name: str, default: int) -> int:
    value = _get_env(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_float_env(name: str, default: float) -> float:
    value = _get_env(name)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_bool_env(name: str, default: bool) -> bool:
    value = _get_env(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    project_name: str
    project_version: str
    fast_api_url: str

    qdrant_url: str
    qdrant_api_key: str | None
    collection_name: str

    qdrant_score_threshold: float
    qdrant_search_limit: int

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

    minio_endpoint: str
    minio_access_key: str | None
    minio_secret_key: str | None
    minio_bucket: str
    minio_secure: bool


def load_settings() -> Settings:
    return Settings(
        project_name=_get_env("PROJECT_NAME", "OmniBrain") or "OmniBrain",
        project_version=_get_env("PROJECT_VERSION", "0.1") or "0.1",
        fast_api_url=_get_env("FAST_API_URL", "http://localhost:8000") or "http://localhost:8000",
        qdrant_url=_get_env("QDRANT_URL", "http://localhost:6333") or "http://localhost:6333",
        qdrant_api_key=_get_env("QDRANT_API_KEY"),
        collection_name=_get_env("COLLECTION_NAME", "omnibrain") or "omnibrain",
        qdrant_score_threshold=_get_float_env("QDRANT_SCORE_THRESHOLD", 0.5),
        qdrant_search_limit=_get_int_env("QDRANT_SEARCH_LIMIT", 10),
        embedding_model=_get_env("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2") or "sentence-transformers/all-MiniLM-L6-v2",
        embedding_batch_size=_get_int_env("EMBEDDING_BATCH_SIZE", 1),
        groq_api_key=_get_env("GROQ_API_KEY"),
        groq_model=_get_env("GROQ_MODEL", "llama-3.3-70b-versatile") or "llama-3.3-70b-versatile",
        groq_supervisior_model=_get_env("GROQ_SUPERVISOR_MODEL", "llama-3.3-70b-versatile") or "llama-3.3-70b-versatile",
        groq_general_model=_get_env("GROQ_GENERAL_MODEL", "llama-3.3-70b-versatile") or "llama-3.3-70b-versatile",
        langsmith_tracing=_get_bool_env("LANGSMITH_TRACKING", False),
        langsmith_api_key=_get_env("LANGSMITH_API_KEY"),
        langsmith_project=_get_env("LANGSMITH_PROJECT", "omnibrain") or "omnibrain",
        langsmith_endpoint=_get_env("LANGSMITH_ENDPOINT", "http://localhost") or "http://localhost",
        max_upload_size_mb=_get_int_env("MAX_UPLOAD_SIZE_MB", 10),
        minio_endpoint=_get_env("MINIO_ENDPOINT", "localhost:9000") or "localhost:9000",
        minio_access_key=_get_env("MINIO_ACCESS_KEY"),
        minio_secret_key=_get_env("MINIO_SECRET_KEY"),
        minio_bucket=_get_env("MINIO_BUCKET", "omnibrain-docs") or "omnibrain-docs",
        minio_secure=_get_bool_env("MINIO_SECURE", False),
    )


settings = load_settings()
