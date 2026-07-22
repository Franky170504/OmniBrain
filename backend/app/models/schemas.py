from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(default="ok", example="ok", description="Current status of the backend API")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the status check")
    version: str = Field(default="1.0.0", description="API version")


class UploadResponse(BaseModel):
    """Response model for document upload endpoint."""
    document_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000", description="Generated unique ID for the uploaded document")
    filename: str = Field(..., example="sample_report.pdf", description="Original filename of the uploaded PDF")
    file_size: int = Field(..., example=102450, description="File size in bytes")
    message: str = Field(..., example="Document uploaded successfully.", description="Status message")


class ChatRequest(BaseModel):
    """Request model for interactive document querying."""
    document_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000", description="ID of the document to query")
    question: str = Field(..., min_length=1, example="What are the key takeaways from this document?", description="Question to ask regarding the document")


class ChatResponse(BaseModel):
    """Response model for document query endpoint (mock response)."""
    document_id: str = Field(..., description="ID of the document queried")
    question: str = Field(..., description="The original question asked")
    answer: str = Field(..., description="Generated answer or mock response")
    sources: List[str] = Field(default_factory=list, description="List of source references or citations")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Detailed description of the error encountered")
