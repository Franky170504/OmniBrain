from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Agent Routes
# ============================================================

AgentRoute = Literal[
    "search_agent",
    "vision_agent",
    "sql_agent",
    "end",
]


# ============================================================
# Health Schemas
# ============================================================

class QdrantHealthResponse(BaseModel):
    status: Literal[
        "healthy",
        "unhealthy",
    ]

    collection_name: str | None = None

    collection_exists: bool = False

    points_count: int | None = Field(
        default=None,
        ge=0,
    )

    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal[
        "healthy",
        "degraded",
        "unhealthy",
    ]

    qdrant: QdrantHealthResponse

    document_service_initialized: bool = False

    rag_service_initialized: bool = False

    agent_graph_initialized: bool = False

    chat_service_initialized: bool = False

    langsmith_tracing_enabled: bool = False

    langsmith_project: str | None = None


# ============================================================
# Upload Schemas
# ============================================================

class UploadResponse(BaseModel):
    message: str

    document_id: str

    filename: str

    page_count: int = Field(
        default=0,
        ge=0,
    )

    chunk_count: int = Field(
        default=0,
        ge=0,
    )

    image_count: int = Field(
        default=0,
        ge=0,
    )

    table_count: int = Field(
        default=0,
        ge=0,
    )

    indexed_points: int = Field(
        default=0,
        ge=0,
    )

    document_type: str | None = None

# ============================================================
# Chat Request
# ============================================================

class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5_000,
        description="The user's question.",
        examples=[
            "Who are the authors of this book?"
        ],
    )

    user_id: str = Field(
        default="local-user",
        min_length=1,
        max_length=200,
        description=(
            "Identifier used to isolate one user's "
            "indexed documents."
        ),
    )

    document_id: str | None = Field(
        default=None,
        description=(
            "The uploaded document identifier. "
            "It may be omitted for SQL questions "
            "that do not depend on a document."
        ),
    )


# ============================================================
# Source / Citation Schema
# ============================================================

class SourceReference(BaseModel):
    """
    Shared source model for all three agents.

    Search Agent:
        point_id
        chunk_id
        document_id

    Vision Agent:
        image_id
        table_id

    SQL Agent:
        datasource_id
        record
    """

    # --------------------------------------------------------
    # Search / Qdrant source identifiers
    # --------------------------------------------------------

    point_id: str | None = None

    chunk_id: str | None = None

    document_id: str | None = None

    # --------------------------------------------------------
    # Vision source identifiers
    # --------------------------------------------------------

    image_id: str | None = None

    table_id: str | None = None

    # --------------------------------------------------------
    # Structured-data source identifier
    # --------------------------------------------------------

    datasource_id: str | None = None

    # --------------------------------------------------------
    # Common source information
    # --------------------------------------------------------

    filename: str | None = None

    page_start: int | None = Field(
        default=None,
        ge=0,
    )

    page_end: int | None = Field(
        default=None,
        ge=0,
    )

    score: float | None = None

    object_path: str | None = None

    highlight_json: dict[str, Any] | None = None

    record: dict[str, Any] | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # Keep additional fields returned by agents instead
    # of silently dropping them.
    model_config = ConfigDict(
        extra="allow"
    )


# ============================================================
# Chat Response
# ============================================================

class ChatResponse(BaseModel):
    answer: str

    # --------------------------------------------------------
    # Evidence / citations
    # --------------------------------------------------------

    sources: list[SourceReference] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Supervisor routing
    # --------------------------------------------------------

    route: AgentRoute | None = None

    route_reason: str | None = None

    # --------------------------------------------------------
    # Search Agent
    # --------------------------------------------------------

    retrieval_attempts: int = Field(
        default=0,
        ge=0,
    )

    # --------------------------------------------------------
    # Vision Agent
    # --------------------------------------------------------

    visual_context: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    visual_type: str | None = None

    page_number: int | None = Field(
        default=None,
        ge=0,
    )

    # --------------------------------------------------------
    # SQL Agent
    # --------------------------------------------------------

    generated_sql: str | None = None

    sql_rows: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Generic error
    # --------------------------------------------------------

    error: str | None = None


# ============================================================
# Generic Error
# ============================================================

class ErrorResponse(BaseModel):
    detail: str


# ============================================================
# Authentication Schemas
# ============================================================

class AuthCredentials(BaseModel):
    email: str = Field(
        min_length=1,
        max_length=320,
        description="User email address.",
    )

    password: str = Field(
        min_length=8,
        max_length=256,
        description="User password.",
    )


class AuthRegisterRequest(
    AuthCredentials
):
    full_name: str = Field(
        min_length=1,
        max_length=150,
        description="User full name.",
    )


class AuthResponse(BaseModel):
    user_id: str

    access_token: str

    token_type: Literal[
        "bearer"
    ] = "bearer"


# ============================================================
# Document Ownership
# ============================================================

class OwnerAssignmentRequest(BaseModel):
    owner_user_id: str = Field(
        min_length=1,
        description=(
            "User ID that should own the document."
        ),
    )


# ============================================================
# Document Metadata
# ============================================================

class DocumentMetadata(BaseModel):
    document_id: str

    user_id: str

    filename: str

    page_count: int = Field(
        default=0,
        ge=0,
    )

    chunk_count: int = Field(
        default=0,
        ge=0,
    )

    image_count: int = Field(
        default=0,
        ge=0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )