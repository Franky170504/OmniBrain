from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv(Path(".env"))

@dataclass(frozen=True)
class Settings:
    qdrant_url: str
    qdrant_api_key: str | None
    collection_name: str
    embedding_model: str
    embedding_batch_size: int
    openai_api_key: str | None
    openai_model: str
    qdrant_score_threshold:float
    qdrant_search_limit : int



def load_settings() -> Settings:
    return Settings(
        qdrant_url=os.getenv("QDRANT_URL",),
        qdrant_api_key=(os.getenv("QDRANT_API_KEY") or None),
        collection_name=os.getenv("COLLECTION_NAME"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
        embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE")),
        openai_api_key=(os.getenv("OPENAI_API_KEY") or None),
        openai_model=(os.getenv("OPENAI_MODEL") or None),
        qdrant_score_threshold=float(os.getenv("QDRANT_SCORE_THRESHOLD")),
        qdrant_search_limit=int(os.getenv("QDRANT_SEARCH_LIMIT"))
    )

settings = load_settings()
