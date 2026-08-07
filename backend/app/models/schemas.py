from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    message: str
    document_id: UUID
    filename: str
    page_count: int
    chunk_count: int
    image_count: int
    indexed_points: int
    processing_status: str


class SourceReference(BaseModel):
    source_id: int | None = None
    chunk_id: str | None = None
    document_id: str | None = None
    filename: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    score: float | None = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    user_id: str = Field(default="local-user", min_length=1)
    document_id: UUID | None = None
    session_id: UUID | None = None


class ChatResponse(BaseModel):
    session_id: UUID
    message_id: UUID
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    route: Literal["document_agent", "general_agent", "clarify_agent"] | None = None
    route_reason: str | None = None
    error: str | None = None


class QdrantHealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    collection_name: str
    collection_exists: bool
    points_count: int | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    postgres: dict[str, Any]
    qdrant: QdrantHealthResponse
