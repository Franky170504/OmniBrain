from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database_session
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService
from app.services.rag_service import RagService


async def get_db() -> AsyncIterator[AsyncSession]:
    async for session in get_database_session():
        yield session


def _service(request: Request, name: str):
    value = getattr(request.app.state, name, None)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{name} is not initialized",
        )
    return value


def get_qdrant_service(request: Request) -> QdrantService:
    return _service(request, "qdrant_service")


def get_document_service(request: Request) -> DocumentService:
    return _service(request, "document_service")


def get_rag_service(request: Request) -> RagService:
    return _service(request, "rag_service")


def get_chat_service(request: Request) -> ChatService:
    return _service(request, "chat_service")
