import os
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings

# =============================================================================
# Backend Root Directory
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR.parent / ".env")


class AppSettings(BaseSettings):
    # =========================================================================
    # Project Configuration
    # =========================================================================

    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    # PROJECT_VERSION: str = "0.1"
    FAST_API_URL: str = os.getenv("FAST_API_URL")

    # =========================================================================
    # Qdrant Configuration
    # =========================================================================

    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = os.getenv("COLLECTION_NAME")

    QDRANT_SCORE_THRESHOLD: float = 0.50
    QDRANT_FALLBACK_THRESHOLD: float = 0.35
    QDRANT_SEARCH_LIMIT: int = 10
    QDRANT_TOP_K: int = 5

    # =========================================================================
    # Embedding Configuration
    # =========================================================================

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_BATCH_SIZE: int = os.getenv("EMBEDDING_BATCH_SIZE")

    # =========================================================================
    # Groq Configuration
    # =========================================================================

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL")
    GROQ_SUPERVISOR_MODEL: str = os.getenv("GROQ_SUPERVISOR_MODEL")
    GROQ_GENERAL_MODEL: str = os.getenv("GROQ_GENERAL_MODEL")

    # =========================================================================
    # LangSmith Configuration
    # =========================================================================

    LANGSMITH_TRACKING: str = os.getenv("LANGSMITH_TRACKING")
    LANGSMITH_API_KEY: str | None = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT")
  
    # =========================================================================
    # Upload Configuration
    # =========================================================================

    MAX_UPLOAD_SIZE_MB: int = os.getenv("MAX_UPLOAD_SIZE_MB")

    # =========================================================================
    # MinIO Configuration
    # =========================================================================

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE","false").lower()=="true"
    print(MINIO_SECURE)

    # =========================================================================
    # PostgreSQL Configuration
    # =========================================================================

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT")
    POSTGRES_DATABASE: str = os.getenv("POSTGRES_DATABASE")
    POSTGRES_USERNAME: str = os.getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")


    SQL_ECHO: bool = Field(
        default=False,
        description="Enable SQLAlchemy SQL logging."
    )
    POOL_SIZE: int = Field(
        default=10,
        ge=1,
        description="Persistent database connections."
    )
    MAX_OVERFLOW: int = Field(
        default=20,
        ge=0,
        description="Temporary overflow connections."
    )
    POOL_TIMEOUT: int = Field(
        default=30,
        ge=5,
        description="Connection timeout in seconds."
    )
    POOL_RECYCLE: int = Field(
        default=1800,
        ge=300,
        description="Recycle idle connections."
    )
    POOL_PRE_PING: bool = Field(
        default=True,
        description="Validate pooled connections."
    )
    DATABASE_AUTO_INIT: bool = Field(
        default=True,
        description="Automatically apply SQL schema files on startup when enabled."
    )

    AUTH_JWT_SECRET: str = os.getenv("AUTH_JWT_SECRET")
    AUTH_JWT_PREVIOUS_JWT_SECRETS: str | None = Field(default=None, repr=False)
    AUTH_TOKEN_TTL_SECONDS: int = Field(default=3600, ge=60, le=86400)
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, ge=1)
    AUTH_RATE_LIMIT_MAX_REQUESTS: int = Field(default=5, ge=1)
    AUTH_RATE_LIMIT_KEY_SALT: str = Field(default="omnibrain-auth-rate-limit", repr=False)


    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (f"postgresql+psycopg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DATABASE}")
        #postgresql+psycopg://postgres:5792195319@127.0.0.1:5432/omnibrain

    # =========================================================================
    # CORS
    # =========================================================================

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:8501",
            "http://127.0.0.1:8000",
        ]
    )

    # =========================================================================
    # Paths
    # =========================================================================

    INPUT_DIR: ClassVar[Path] = Path("data/input")
    OUTPUT_DIR: ClassVar[Path] = Path("data/output")

    CHUNKS: ClassVar[str] = r"data/output/chunks.jsonl"
    DOCUMENTS: ClassVar[str] = r"data/output/documents.jsonl"
    IMAGES: ClassVar[str] = r"data/output/images.jsonl"

    @classmethod
    def resolve_path(cls, value: object) -> Path:
        path = Path(str(value))

        if not path.is_absolute():
            path = BASE_DIR / path

        return path.resolve()

    # =========================================================================
    # Backward-Compatible Property Aliases
    # =========================================================================

    @property
    def project_name(self) -> str:
        return self.PROJECT_NAME

    @property
    def project_version(self) -> str:
        return self.PROJECT_VERSION

    @property
    def fast_api_url(self) -> str:
        return self.FAST_API_URL

    @property
    def qdrant_url(self) -> str:
        return self.QDRANT_URL

    @property
    def qdrant_api_key(self) -> str | None:
        return self.QDRANT_API_KEY

    @property
    def auth_jwt_previous_secrets(self) -> tuple[bytes, ...]:
        raw_value = self.AUTH_JWT_PREVIOUS_JWT_SECRETS or ""
        secrets = [secret.strip() for secret in raw_value.split(",") if secret.strip()]
        return tuple(secret.encode("utf-8") for secret in secrets)

    @property
    def collection_name(self) -> str:
        return self.QDRANT_COLLECTION

    @property
    def qdrant_score_threshold(self) -> float:
        return self.QDRANT_SCORE_THRESHOLD

    @property
    def qdrant_search_limit(self) -> int:
        return self.QDRANT_SEARCH_LIMIT

    @property
    def qdrant_fallback_threshold(self) -> float:
        return self.QDRANT_FALLBACK_THRESHOLD

    @property
    def qdrant_top_k(self) -> int:
        return self.QDRANT_TOP_K

    @property
    def embedding_model(self) -> str:
        return self.EMBEDDING_MODEL

    @property
    def embedding_batch_size(self) -> int:
        return self.EMBEDDING_BATCH_SIZE

    @property
    def groq_api_key(self) -> str | None:
        return self.GROQ_API_KEY

    @property
    def groq_model(self) -> str:
        return self.GROQ_MODEL

    @property
    def groq_supervisior_model(self) -> str:
        env_value = os.getenv("GROQ_SUPERVISOR_MODEL")
        if env_value and env_value.strip():
            return env_value.strip()
        try:
            return self.GROQ_SUPERVISOR_MODEL
        except Exception:
            return "llama-3.3-70b-versatile"

    @property
    def groq_general_model(self) -> str:
        env_value = os.getenv("GROQ_GENERAL_MODEL")
        if env_value and env_value.strip():
            return env_value.strip()
        try:
            return self.GROQ_GENERAL_MODEL
        except Exception:
            return "groq/compound"

    @property
    def langsmith_tracing(self) -> bool:
        return self.LANGSMITH_TRACKING

    @property
    def langsmith_api_key(self) -> str | None:
        return self.LANGSMITH_API_KEY

    @property
    def langsmith_project(self) -> str:
        return self.LANGSMITH_PROJECT

    @property
    def langsmith_endpoint(self) -> str:
        return self.LANGSMITH_ENDPOINT

    @property
    def max_upload_size_mb(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB

    @property
    def minio_endpoint(self) -> str:
        return self.MINIO_ENDPOINT

    @property
    def minio_access_key(self) -> str | None:
        return self.MINIO_ACCESS_KEY

    @property
    def minio_secret_key(self) -> str | None:
        return self.MINIO_SECRET_KEY

    @property
    def minio_bucket(self) -> str:
        return self.MINIO_BUCKET

    @property
    def minio_secure(self) -> bool:
        return self.MINIO_SECURE

    @property
    def postgres_host(self) -> str:
        return self.POSTGRES_HOST

    @property
    def postgres_port(self) -> int:
        return self.POSTGRES_PORT

    @property
    def postgres_database(self) -> str:
        return self.POSTGRES_DATABASE

    @property
    def postgres_username(self) -> str:
        return self.POSTGRES_USERNAME

    @property
    def postgres_password(self) -> str:
        return self.POSTGRES_PASSWORD

    @property
    def sql_echo(self) -> bool:
        return self.SQL_ECHO

    @property
    def pool_size(self) -> int:
        return self.POOL_SIZE

    @property
    def max_overflow(self) -> int:
        return self.MAX_OVERFLOW

    @property
    def pool_timeout(self) -> int:
        return self.POOL_TIMEOUT

    @property
    def pool_recycle(self) -> int:
        return self.POOL_RECYCLE

    @property
    def pool_pre_ping(self) -> bool:
        return self.POOL_PRE_PING

    @property
    def database_auto_init(self) -> bool:
        return self.DATABASE_AUTO_INIT

    # =========================================================================
    # Validators
    # =========================================================================

    @model_validator(mode="before")
    @classmethod
    def map_legacy_env_names(cls, values: object) -> object:
        if isinstance(values, dict):
            if "QDRANT_COLLECTION" not in values:
                legacy_collection = os.getenv("COLLECTION_NAME") or os.getenv("collection_name")
                if legacy_collection:
                    values["QDRANT_COLLECTION"] = legacy_collection

            groq_key = values.get("GROQ_API_KEY")
            if isinstance(groq_key, str):
                normalized = groq_key.strip()
                if not normalized or normalized.lower() in {
                    "placeholder",
                    "<placeholder>",
                    "your_api_key",
                    "your_api_key_here",
                    "changeme",
                    "none",
                    "xxx",
                }:
                    values["GROQ_API_KEY"] = None

        return values

    @field_validator(
        "QDRANT_API_KEY",
        "GROQ_API_KEY",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


# =============================================================================
# Global Settings Instance
# =============================================================================

app_settings = AppSettings()
settings = app_settings

if not settings.groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing or invalid. "
        "Set a valid Groq API key in .env or the environment."
    )

if not settings.groq_model or not settings.groq_model.strip():
    raise RuntimeError(
        "GROQ_MODEL must be configured and cannot be empty. "
        "Verify GROQ_MODEL in .env or environment settings."
    )

if not settings.groq_general_model or not settings.groq_general_model.strip():
    raise RuntimeError(
        "GROQ_GENERAL_MODEL must be configured and cannot be empty. "
        "Verify GROQ_GENERAL_MODEL in .env or environment settings."
    )

if not settings.groq_supervisior_model or not settings.groq_supervisior_model.strip():
    raise RuntimeError(
        "GROQ_SUPERVISIOR_MODEL must be configured and cannot be empty. "
        "Verify GROQ_SUPERVISIOR_MODEL in .env or environment settings."
    )

INPUT_DIR = AppSettings.INPUT_DIR
OUTPUT_DIR = AppSettings.OUTPUT_DIR
CHUNKS = AppSettings.CHUNKS
DOCUMENTS = AppSettings.DOCUMENTS
IMAGES = AppSettings.IMAGES

