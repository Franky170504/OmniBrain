from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    image_count: int
    indexed_points: int


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5_000,
    )

    user_id: str = Field(
        default="local-user",
        min_length=1,
        max_length=200,
    )

    document_id: str | None = None


class SourceReference(BaseModel):
    chunk_id: str | None = None
    filename: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference]


class QdrantHealth(BaseModel):
    connected: bool
    available_collections: list[str]
    collection: str
    collection_exists: bool
    collection_status: str | None
    point_count: int


class HealthResponse(BaseModel):
    status: str
    qdrant: QdrantHealth