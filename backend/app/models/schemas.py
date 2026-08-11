from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

AgentRoute = Literal[
    "document_agent",
    "general_agent",
    "clarify_agent",
]

class QdrantHealthResponse(BaseModel):
    status: Literal["healthy","unhealthy"]
    qdrant_initialized: bool
    document_service_initialized: bool
    rag_service_initialized: bool
    agent_graph_initialized: bool
    chat_service_initialized: bool
    langsmith_tracing_enabled: bool = False
    langsmith_project: str | None = None

class HealthResponse(BaseModel):
    status: Literal[
        "healthy",
        "degraded",
        "unhealthy",
    ]
    qdrant: QdrantHealthResponse

class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    page_count: int = Field(ge=0, description="Number of pages parsed from the PDF.")
    chunk_count: int = Field(ge=0, description="Number of text chunks created.")
    image_count: int = Field(ge=0, description="Number of images extracted.")
    indexed_points: int = Field(ge=0, description="Number of vector points written to Qdrant.")

class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5_000,
        description="The user's question.",
        examples=["Who are the authors of this book?"],
    )

    user_id: str = Field(
        default="local-user",
        min_length=1,
        max_length=200,
        description=("Identifier used to isolate one user's indexed documents."),
    )

    document_id: str | None = Field(
        default=None,
        description=(
            "The uploaded document identifier. It may be omitted "
            "for general questions."
        ),
    )

class SourceReference(BaseModel):
    point_id: str | None = None
    chunk_id: str | None = None
    document_id: str | None = None
    filename: str | None = None
    page_start: int | None = Field(default=None,ge=0)
    page_end: int | None = Field(default=None,ge=0)
    score: float | None = None
    model_config = ConfigDict(extra="ignore")

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    route: AgentRoute | None = None
    route_reason: str | None = None
    error: str | None = None

class ErrorResponse(BaseModel):
    detail: str

class AuthCredentials(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=256)

class AuthRegisterRequest(AuthCredentials):
    full_name: str = Field(min_length=1, max_length=150)

class AuthResponse(BaseModel):
    user_id: str
    access_token: str
    token_type: Literal["bearer"] = "bearer"

class OwnerAssignmentRequest(BaseModel):
    owner_user_id: str

class QdrantHealthResponse(BaseModel):
    status: Literal[
        "healthy",
        "unhealthy",
    ]

    collection_name: str
    collection_exists: bool
    points_count: int | None = None
    error: str | None = None

class DocumentMetadata(BaseModel):
    document_id: str
    user_id: str
    filename: str
    page_count: int = Field(default=0, ge=0)
    chunk_count: int = Field(default=0, ge=0)
    image_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)