import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


# Base directory for the backend (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_UPLOAD_DIR = BASE_DIR / "uploads"


class Settings(BaseModel):
    """Application settings and configuration defaults."""
    PROJECT_NAME: str = "OmniBrain API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend foundation for document ingestion and AI workspace assistant."
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ]
    )
    
    # File Storage
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(DEFAULT_UPLOAD_DIR)))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    ALLOWED_CONTENT_TYPES: List[str] = ["application/pdf"]


settings = Settings()
